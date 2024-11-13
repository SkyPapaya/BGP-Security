from multiprocessing import Process
import datetime,time
from URLGetter import *
import requests
from constant import *
import urllib3
import urllib3.exceptions
import time,random,os
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import Tags
import io
from tools import *
from ftplib import FTP
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MINUTE=60

def download_file_with_progress(url, destination):
    # 创建一个带有进度条的下载器
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 如果请求返回了不成功的状态码，会引发HTTPError异常
    total_size = int(response.headers.get('content-length', 0))  # 获取文件总大小
    block_size = 1024  # 每次读取的块大小
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading')
    with response.iter_content(block_size) as block:
        for data in block:
            progress_bar.update(len(data))  # 更新进度条
        progress_bar.close()  # 关闭进度条
        return response

class downloadProcess(Process):
    def __init__(self,base_type:str,urllist:list,destination):
        super(downloadProcess,self).__init__()
        self.base_type = base_type
        self.urllist = urllist
        self.client = Minio(
            "minio.lab:9000",
            # "minio:90",
            access_key="cnic",
            secret_key="Cnic2022_",
            secure=False
        )
        self.destination = destination
        self.ErrorList=[]
        self.AnomalList=[]
                 
    def run(self):
        total = len(self.urllist)
        i = 0
        pid = os.getpid()
        for data in self.urllist:
            mod = data[0]
            url = data[1]
            if mod == HTTPS:
                print("start:"+url)
                self.downloadByHTTP(url,isError=False)
            elif mod == MINIO:
                self.downloadByMINIO(url)
            elif mod == FTPN:
                self.downloadByFTP(url,isError=False)
                pass
            else:
                print("Not Supported Yet!")
                pass
            i+=1
            print("process %u done %d/%d %s"%(pid,i,total,url))
        self.HandleErrorList()
        self.PrintErrorInfo()
        return


    def downloadByHTTP(self,url:str,isError:bool):
        headers = {
            'User-Agent': 'Wget/1.21.1'
        }
        name,timeout,tags = getInfoFromURL(self.base_type,url)
        if isError:
            timeout *= 2
        if timeout == LARGE_TIMEOUT:
            try:
                r = requests.head(url)
                os.system(f"wget -c {url} -O {name}")
                self.client.fput_object(MINIO_BUCKET_NAME[self.base_type], tranPath(name), name, content_type=r.headers['Content-Type'], part_size=4*1024*1024*1024)
                if self.destination=="":
                    os.system(f"rm {name}")
                else:
                    os.system(f"mv {name} {self.destination}")
            except Exception as e:
                print(e)
                print("http error %s"%(url))
                if isError==False:
                    self.ErrorList.append((HTTPS,url))
        else:
            try:
                # r=requests.get(url,headers=headers,allow_redirects=True,verify=False,timeout=timeout)
                # self.client.put_object(MINIO_BUCKET_NAME[self.base_type],tranPath(name),io.BytesIO(r.content),length=int(r.headers['Content-Length']),content_type=r.headers['Content-Type'],part_size=4*1024*1024*1024)
                # if self.destination!="":
                #     open("%s/%s"%(self.destination,name), 'wb').write(r.content)
                # print("http done: "+url)
                with requests.get(url, headers=headers, allow_redirects=True, verify=False, timeout=timeout, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('Content-Length', 0))
                    chunk_size = 1024
                    with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                        content = io.BytesIO()
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            pbar.update(len(chunk))
                            content.write(chunk)
                        content.seek(0)
                        self.client.put_object(MINIO_BUCKET_NAME[self.base_type], tranPath(name), content, length=total_size, content_type=r.headers['Content-Type'], part_size=4*1024*1024*1024)
                    if self.destination != "":
                        with open(f"{self.destination}/{name}", 'wb') as f:
                            f.write(content.getvalue())
                    print("http done: " + url)
            except Exception as e:
                print(e)
                print("http error %s"%(url))
                if isError==False:
                    self.ErrorList.append((HTTPS,url))
    
    def downloadByFTP(self,url:str,isError:bool):
        host=url[0]
        path=url[1]
        sources=url[2]
        # handle
        ftp=FTP(host)
        ftp.login()
        ftp.cwd(path)
        errlist = []
        for s in sources:
            filename=s.split("/")[-1]
            downloaded_file = io.BytesIO()
            try:
                ftp.retrbinary('RETR '+ s, downloaded_file.write)
                downloaded_file.seek(0)
                self.client.put_object(MINIO_BUCKET_NAME["IRR"],s.split("/")[-1],downloaded_file,length=downloaded_file.getbuffer().nbytes)
                if self.destination!="":
                    with open(self.destination+"/"+filename,'wb') as local_file:
                        downloaded_file.seek(0)
                        local_file.write(downloaded_file.read())
                print("ftp done: "+filename)
            except Exception as e:
                print(e)
                errlist.append(s)
                print("ftp error %s"%(s))
        if len(errlist)>0:
            if isError==False:
                self.ErrorList.append((FTPN,(host,path,errlist)))
    
    def downloadByMINIO(self,url:str):
        if self.destination!="":
            try:
                filename = getFileName(self.base_type,url)
                self.client.fget_object(MINIO_BUCKET_NAME[self.base_type],tranPath(filename),"%s/%s"%(self.destination,filename))
                print("minio done: "+url)
            except Exception as e:
                if "http" in url:
                    self.downloadByHTTP(url,False)
                else:
                    self.downloadByFTP(url,False)
    
    def HandleErrorList(self):
        i = 0
        pid = os.getpid()
        while i < len(self.ErrorList):
            data=self.ErrorList[i]
            mod = data[0]
            url = data[1]
            try:
                if mod == HTTPS:
                    print("start fixing: "+url)
                    self.downloadByHTTP(url,isError=True)
                elif mod == FTPN:
                    self.downloadByFTP(url,isError=True)
                    pass
                else:
                    print("Not Supported Yet!")
                    pass
            except Exception as e:
                print(e)
                self.AnomalList.append(data)
            i+=1
            print("process %u fix %d/%d"%(pid,i,len(self.ErrorList)))
    
    def PrintErrorInfo(self):
        f=open("./errorInfo.txt","a")
        for url in self.AnomalList:
            f.writelines("%s|%s\n"%(str(url[0]),str(url[1])))

class downloadLocalProcess(Process):
    '''
    download data in local
    '''
    def __init__(self,s:list,destination,save_by_collector=0):
        super(downloadLocalProcess,self).__init__()
        self.s=s
        self.destination=destination
        self.flag=save_by_collector
        self.ErrorList=[]
    
    def set_file_name(self,url:str):
        '''
        通过url来设置该文件存储到本地的文件名，以及他在目标文件夹下的存储位置
        '''
        destination=""
        name,collector=set_name_collector(url)
        if self.flag==0:
            destination=self.destination+'/'+name
        else:
            try:
                os.stat(self.destination+'/'+collector)
            except:
                os.mkdir(self.destination+'/'+collector)
            else:
                pass
            destination=self.destination+'/'+collector+'/'+name
        return name,destination
    
    def run(self):
        total = len(self.s)
        i = 0
        pid = os.getpid()
        for data in self.s:
            mod=data[0]
            url=data[1]
            if mod==HTTPS:
                self.downloadByHTTP(url)
            elif mod==FTPN:
                self.downloadByFTP(url)
            elif mod==PY:
                self.downloadByPY(url)
            i+=1
            print("process %u done %d/%d"%(pid,i,total))
        time.sleep(1)
        self.HandleErrorList()
        self.PrintErrorInfo()
        return
    
    def set_time_out(self,url:str):
        timeout=BASE_TIMEOUT
        if "bview" in url or "rib" in url:
            timeout=MEDIUM_TIMEOUT
        elif "rpki" in url:
            if "amber.massars.net" in url:
                timeout=LARGE_TIMEOUT
            else:
                timeout=BASE_TIMEOUT  
        return timeout
    
    def downloadByHTTP(self,url:str):
        '''
        根据url，通过https的连接方法获取数据
        '''
        name,destination=self.set_file_name(url)
        try:
            timeout=set_time_out(url)
            r=requests.get(url,allow_redirects=True,verify=False,timeout=timeout)
            open(destination, 'wb').write(r.content)
            print("done: "+name)
        except Exception as e:
            self.ErrorList.append((HTTPS,url))

    
    def downloadByFTP(self,url:tuple):
        '''
        根据url，通过ftp的连接方法获取数据
        '''
        host=url[0]
        path=url[1]
        sources=url[2]
        # handle
        ftp=FTP(host)
        ftp.login()
        ftp.cwd(path)
        Errorlist=[]
        for s in sources:
            name,destination=self.set_file_name(host+"/"+path+"/"+s)
            try:
                ftp.retrbinary('RETR '+ s, open(destination,'wb').write)
                print("done: "+name)
            except Exception as e:
                Errorlist.append((name,destination,s))
        if len(Errorlist)>0:
            self.ErrorList.append((FTPN,url))
    
    def downloadByPY(self,url:str):
        asns=self.destination+"/"+datetime.datetime.utcnow().strftime("%Y%m")+"_"+"asns"
        organizations=self.destination+"/"+datetime.datetime.utcnow().strftime("%Y%m")+"_"+"organizations"
        asnlinks=self.destination+"/"+datetime.datetime.utcnow().strftime("%Y%m")+"_"+"asnLinks"
        url=("python3 asrank-download.py -v -a %s.jsonl -o %s.jsonl -l %s.jsonl -u https://api.asrank.caida.org/v2/graphql"%(asns,organizations,asnlinks))
        os.system(url)
        print("done:asrank")

    def ErrorCheck(self):
        total = len(self.ErrorList)
        i = 0
        pid = os.getpid()
        while i < total:
            data=self.ErrorList[i]
            mod = data[0]
            url = data[1]
            try:
                if mod == HTTPS:
                    self.downloadByHTTP(url,isError=True)
                elif mod == FTPN:
                    self.downloadByFTP(url)
                elif mod == PY:
                    self.downloadByPY(url)
                else:
                    print("Not Supported Yet!")
                    pass
                self.ErrorList.remove(data)
                i-=1
            except Exception as e:
                print(e)
            i+=1
            print("process %u fix %d/%d"%(pid,i,total))

        # 将仍无法解决的url存放到ErrorInfo.txt中
        f=open(self.destination+"/ErrorInfo.txt","a")
        for s in self.ErrorList:
            if s[0]==HTTPS:
                f.writelines("%s|%s|%s|%s\n"%(str(s[0]),s[1],s[2],s[3]))
            elif s[0]==FTPN:
                f.writelines("%s|%s|%s|"%(str(s[0]),s[1],s[2]))
                for data in s[3]:
                    f.writelines("%s %s %s,"%(data[0],data[1],data[2]))
                f.writelines("\n")


if __name__ == "__main__":
    urlgetter=rpkiGetter(base_params(
        rpkicollectors=["josephine.sobornost.net"],
        start_time="2020-12-26-05:00",
        end_time="2020-12-26-06:10"
    ))
    urllist = urlgetter.getURL()
    p = downloadProcess(
        s=urllist,
        destination="rpkidata"
    )
    p.start()
    p.join()
    



