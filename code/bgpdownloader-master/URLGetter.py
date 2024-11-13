import datetime
from ftplib import FTP
from typing import Tuple
from constant import AS_ORGANIZATION, AS_RELATION_SERIAL_1, AS_RELATION_SERIAL_2, ASRANK_GRAPHQL, HTTPS, IP_AFRINIC, IP_APNIC, IP_ARIN, IP_COLLECTORS, IP_LACNIC, IP_RIPE, IRR_DAILY_URL, IRR_HISTORY, IRR_HISTORY_SET, MINIO, PATTERN_STR, BGP_RIPE_URL, PY, RP_RRDP, RP_RSYNC, RPKI_CLOUDFLARE, RPKI_NTT, RPKI_RIPE, RPKI_RIPE_URL, SQL_TABLE_NAME, RouteViews,BGP_RIPE, RouteViews_URL, BGP_DATATYPE, FTPN
import urllib,re
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from tools import *
from base import base_params
from dateutil.relativedelta import relativedelta
from getInfoFromSQL import *
from minio.error import *


class urlGetter:
    '''
    urlGetter基类，提供获取url的基本函数

    参数：
        params:base_params类型，用于保存所需数据包的相关参数
    '''
    def __init__(self,params:base_params):
        super(urlGetter).__init__()
        self.params=params
    
    def findElement(self, url, pattern_str):
        '''
        该函数用于在url对应的html内容中找出所有与pattern_str匹配的内容，返回结果为list类型

        参数：
            url:目标链接
            pattern_str:正则表达式
        '''
        sources=[]
        bs4_parser = "html.parser"
        print(url)
        try:
            response = urllib.request.urlopen(url)
            html = BeautifulSoup(response.read(), bs4_parser)
            for link in html.findAll('a',text=re.compile(pattern_str)):
                sources.append(link['href'])
            response.close()
        except urllib.error.HTTPError:
            response.close()
            print(url + " dont have such data!") 
        return sources

    def getURL(self):
        '''
        获取url，后面会根据不同的子类进行重写
        '''
        pass

class bgpGetter(urlGetter):
    '''
    获取bgp数据包，继承自urlGetter\n
    需要参数：start_time, end_time, bgp_data_type, bgpcollectors
    '''
    def set_base_url(self,collector):
        '''
        根据collector设置相应的基本url,一级目录
        '''
        base_url=""
        if collector in RouteViews:
            if collector == "route-views2":
                base_url = "%s/bgpdata"%(RouteViews_URL)
            else:
                base_url = "%s/%s/bgpdata"%(RouteViews_URL,collector)
        elif collector in BGP_RIPE:
            base_url="%s/%s/"%(BGP_RIPE_URL,collector)
        return base_url
    
    def set_base_url_by_type(self,collector,selected_time,datatype):
        '''
        根据collector，selectedtime和datatype来设置url，二级目录
        '''
        base_url=[]
        if collector in RouteViews:
            if datatype==BGP_DATATYPE["UPDATES"] or datatype==BGP_DATATYPE["ALL"]:
                if collector=="route-views2":
                    base_url.append("%s/bgpdata/%s/UPDATES/"%(RouteViews_URL,selected_time))         
                else:
                    base_url.append("%s/%s/bgpdata/%s/UPDATES/"%(RouteViews_URL,collector,selected_time))
                    
            if datatype==BGP_DATATYPE["RIBS"] or datatype==BGP_DATATYPE["ALL"]:
                if collector=="route-views2":
                    base_url.append("%s/bgpdata/%s/RIBS/"%(RouteViews_URL,selected_time))  
                else:        
                    base_url.append("%s/%s/bgpdata/%s/RIBS/"%(RouteViews_URL,collector,selected_time))
        elif collector in BGP_RIPE:
            base_url.append("%s/%s/%s/"%(BGP_RIPE_URL,collector,selected_time))
        return base_url
    
    def set_pattern_str(self,cc,dt):
        '''
        根据采集点和所需数据类型设置正则表达式
        '''
        pattern_str=""
        if dt==BGP_DATATYPE["UPDATES"]:
            pattern_str=PATTERN_STR['UPDATES']
        elif dt==BGP_DATATYPE["RIBS"]:
            pattern_str=PATTERN_STR['BZ2'] if cc in RouteViews else PATTERN_STR['BVIEW']
        elif dt==BGP_DATATYPE["ALL"]:
            pattern_str=PATTERN_STR['UPDATES']+"|"+(PATTERN_STR['BZ2'] if cc in RouteViews else PATTERN_STR['BVIEW'])
        return pattern_str   

    def getURL(self):
        RibUrls=[] 
        start_time=self.params.start_time
        end_time=self.params.end_time
        datatype=self.params.bgp_data_type
        for cc in self.params.bgp_collectors:
            print(cc)
            sources=[]
            base_url=self.set_base_url(cc)
            sources=self.findElement(base_url, PATTERN_STR["YEAR_MONTH"])
            selected_times=[]    
            for s in sources:
                t=s.split("/")[0]
                ym=get_year_month(datetime.datetime.strptime(t,"%Y.%m"))
                if get_year_month(start_time) <= ym and get_year_month(end_time) >= ym:
                    selected_times.append(t)
            if len(selected_times)==0:
                print(cc+" dont have such data in your start_time and end_time")
                continue
            # print(selected_times)
            for st in selected_times:
                sources=[]
                base_url=self.set_base_url_by_type(cc,st,datatype)
                pattern_str=self.set_pattern_str(cc,datatype)
                for url in base_url:
                    sources = self.findElement(url, pattern_str)
                    # print(sources)
                    for s in sources:
                        if len(s)<20:
                            continue
                        data=s.split(".")
                        tt=datetime.datetime.strptime(data[1]+'.'+data[2],"%Y%m%d.%H%M")
                        if start_time <= tt and end_time >= tt:
                            finalurl=url+s
                            RibUrls.append((HTTPS,finalurl))
        return RibUrls


class rpkiGetter(urlGetter):
    '''
    获取rpki数据包，继承自urlGetter\n
    需要参数：start_time, end_time, rpki_collectors
    '''
    def set_base_url(self,collector):
        if collector in RPKI_RIPE:
            return RPKI_RIPE_URL+collector
        else:
            if collector=="josephine.sobornost.net":
                return "http://%s/%s/rpkidata/"%(collector,collector)
            else:
                return "https://%s/rpkidata/"%(collector)

    def getURL(self):
        FinalUrls=[]
        start_time=self.params.start_time
        end_time=self.params.end_time
        for cc in self.params.rpki_collectors:
            url=self.set_base_url(cc)
            # 先看年份)
            ps=PATTERN_STR["YEAR"]
            if "josephine.sobornost.net" in url:
                ps=PATTERN_STR["YEAR_JSN"]
            year=self.findElement(url,ps)
            for y in year:
                y=int(y.split("/")[0])
                if start_time.year<=y and end_time.year>=y:
                    yurl=url+"/"+str(y)+"/"
                    # 再看月份
                    month=self.findElement(yurl,PATTERN_STR["MONTH"])
                    for m in month:
                        m=m.split("/")[0]
                        t=datetime.datetime.strptime(str(y)+"."+m,"%Y.%m")
                        if get_year_month(start_time)<=get_year_month(t) and get_year_month(end_time)>=get_year_month(t):
                            murl=yurl+"/"+str(m)+"/"
                            # 再看几号
                            day=self.findElement(murl,PATTERN_STR["DAY"])
                            # print(day)
                            for d in day: 
                                d=d.split("/")[0]
                                t=datetime.datetime.strptime(str(y)+"."+m+"."+d,"%Y.%m.%d")
                                if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(end_time)>=get_year_month_day(t):
                                    durl=murl+"/"+str(d)+"/"
                                    # RIPE的直接拿
                                    if cc in RPKI_RIPE:
                                        sources=self.findElement(durl,PATTERN_STR["RIPE_RPKI"])
                                        for s in sources:
                                            rd = self.params.rpki_data_type
                                            if rd==RPKI_DATATYPE["ALL"] or rd in s:
                                                furl=durl+s
                                                FinalUrls.append((HTTPS,furl))
                                    # NTT的还需要看下具体时间
                                    else:
                                        sources=self.findElement(durl,PATTERN_STR["NTT"])
                                        for s in sources:
                                            tmp=s.split(".")[0].split("-")[1].split("Z")[0].replace("T",".")
                                            t=datetime.datetime.strptime(tmp,"%Y%m%d.%H%M%S")
                                            if start_time<=t and end_time>=t:
                                                furl=durl+s
                                                if furl[-1]=='/':
                                                    furl = furl[0:-1]
                                                FinalUrls.append((HTTPS,furl))                                            
        return FinalUrls
class RPKICloudflareGetter(urlGetter):
    '''
    获取rpkicloudflare数据包，继承自urlGetter\n
    需要参数：none
    '''
    def getURL(self):
        return [(HTTPS,RPKI_CLOUDFLARE)]

class ASRelationGetter(urlGetter):
    '''
    获取AS-Relationship数据包，继承自urlGetter\n
    需要参数：start_time, end_time
    '''
    def getURL(self):
        FinalUrls=[]
        start_time=self.params.start_time
        end_time=self.params.end_time
        if self.params.asrel_data_type==ASREL_DATATYPE["ALL"]:
            urllist=[AS_RELATION_SERIAL_1,AS_RELATION_SERIAL_2]
        elif self.params.asrel_data_type==ASREL_DATATYPE["1"]:
            urllist=[AS_RELATION_SERIAL_1]
        elif self.params.asrel_data_type==ASREL_DATATYPE["2"]:
            urllist=[AS_RELATION_SERIAL_2]
        for url in urllist:
            source1=self.findElement(url,PATTERN_STR["BZ2"])
            for s in source1:
                t=datetime.datetime.strptime(s.split(".")[0],"%Y%m%d")
                if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(end_time)>=get_year_month_day(t):
                    FinalUrls.append((HTTPS,url+"/"+s))
        return FinalUrls

class ASOrganizationGetter(urlGetter):
    '''
    获取AS-Organization数据包，继承自urlGetter\n
    需要参数：start_time, end_time
    '''
    def getURL(self):
        FinalUrls=[]
        start_time=self.params.start_time
        end_time=self.params.end_time
        source=self.findElement(AS_ORGANIZATION,PATTERN_STR["GZ"])
        for s in source:
            if ".txt" in s:
                t=datetime.datetime.strptime(s.split(".")[0],"%Y%m%d")
                if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(end_time)>=get_year_month_day(t):
                    FinalUrls.append((HTTPS,AS_ORGANIZATION+"/"+s))
        return FinalUrls

class IPRIRGetter(urlGetter):
    def setPattern(self,rir):
        if rir.lower()=="arin":
            return PATTERN_STR["ARIN"]
        else:
            return PATTERN_STR["INT"]

    def getURL(self):
        FinalUrls=[]
        start_time=self.params.start_time
        end_time=self.params.end_time
        collectors=self.params.ip_collectors
        for c in collectors:
            if c=="apnic":
                print("apnic")
                self.APNICGetter(FinalUrls,start_time,end_time)
            elif c=="afrinic":
                print("afrinic")
                self.AFRINICGetter(FinalUrls,start_time,end_time)
            elif c=="ripe":
                print("ripe")
                self.RIPEGetter(FinalUrls,start_time,end_time)
            elif c=="arin":
                print("arin")
                self.ARINGetter(FinalUrls,start_time,end_time)
            elif c=="lacnic":
                print("lacnic")
                self.LACNICGetter(FinalUrls,start_time,end_time)
        return FinalUrls
    
    def transfer_divided_Getter(self,url,FinalUrls,start_time,end_time):
        base_url=url+"/transfers/"
        year=self.findElement(base_url,PATTERN_STR["YEAR"])
        for y in year:
            y=int(y.split("/")[0])
            if start_time.year<=y and y<=end_time.year:
                durl=base_url+str(y)+"/"
                sources=self.findElement(durl,PATTERN_STR["TRANSFERS"])
                for s in sources:
                    
                    t=datetime.datetime.strptime("".join(s.split(".")[0].split("_")[1].split("Z")[0].split("T")),"%Y%m%d%H%M%S")
                    if start_time<=t and end_time>=t:
                        FinalUrls.append((HTTPS,durl+s))

    
    def get_sources_by_year_folder(self,url,FinalUrls:list,start_time,end_time):
        year=self.findElement(url,PATTERN_STR["YEAR"])
        for y in year:
            y=int(y.split("/")[0])
            if start_time.year<=y and y<=end_time.year:
                yurl=url+"/"+str(y)+"/"
                sources=self.findElement(yurl,self.setPattern(url.replace("//","/").split("/")[4]))
                for s in sources:
                    if "md5" not in s and "asc" not in s:
                        t=datetime.datetime.strptime(s.split("-")[-1].split(".")[0],"%Y%m%d")
                        if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(end_time)>=get_year_month_day(t):
                            FinalUrls.append((HTTPS,yurl+"/"+s))

    def APNICGetter(self,FinalUrls,start_time,end_time):
        self.transfer_divided_Getter(IP_APNIC,FinalUrls,start_time,end_time)
        self.get_sources_by_year_folder(IP_APNIC,FinalUrls,start_time,end_time)
        
    def AFRINICGetter(self,FinalUrls,start_time,end_time):
        self.transfer_divided_Getter(IP_AFRINIC,FinalUrls,start_time,end_time)
        self.get_sources_by_year_folder(IP_AFRINIC,FinalUrls,start_time,end_time)
    
    def ARINGetter(self,FinalUrls,start_time,end_time):
        self.transfer_divided_Getter(IP_ARIN,FinalUrls,start_time,end_time)
        divider=datetime.datetime(2021,1,1,10,45)
        if end_time<=divider:
            self.get_sources_by_year_folder(IP_ARIN+"/archive/",FinalUrls,start_time,end_time)
        else:
            if start_time<divider:
                self.get_sources_by_year_folder(IP_ARIN+"/archive/",FinalUrls,start_time,divider)    
                start_time=divider
            sources=self.findElement(IP_ARIN,PATTERN_STR["ARIN"])
            for s in sources:
                if "latest" not in s and "md5" not in s and "key" not in s:
                    t=datetime.datetime.strptime(s.split("-")[-1],"%Y%m%d")
                    if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(end_time)>=get_year_month_day(t):
                        FinalUrls.append((HTTPS,IP_ARIN+"/"+s))
            
    def RIPEGetter(self,FinalUrls,start_time,end_time):
        FinalUrls.append(IP_RIPE+"/transfers/transfers_latest.json")
        self.get_sources_by_year_folder(IP_RIPE,FinalUrls,start_time,end_time)
    
    def LACNICGetter(self,FinalUrls,start_time,end_time):
        self.transfer_divided_Getter(IP_LACNIC,FinalUrls,start_time,end_time)
        divider=datetime.datetime(2004,1,1,8,50)
        if end_time<=divider:
            self.get_sources_by_year_folder(IP_LACNIC+"/archive/",FinalUrls,start_time,end_time)
        else:
            if start_time<divider:
                self.get_sources_by_year_folder(IP_LACNIC+"/archive/",FinalUrls,start_time,divider)    
                start_time=divider
            sources=self.findElement(IP_LACNIC,PATTERN_STR["INT"])
            for s in sources:
                if "." not in s:
                    t=datetime.datetime.strptime(s.split("-")[-1],"%Y%m%d")
                    if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(end_time)>=get_year_month_day(t):
                        FinalUrls.append((HTTPS,IP_APNIC+"/"+s))

class IRRGetter(urlGetter):    
    def getURL_HTTPS(self,FinalUrls,url:str,start_time=None,end_time=None):
        if start_time==None and end_time==None:
            FinalUrls.append((HTTPS,url))
        else:
            sources=self.findElement(url,PATTERN_STR["GZ"])
            for s in sources:
                t=s.split(".")[0]
                if len(t)<=6:
                    continue
                t=datetime.datetime.strptime(t.split("-")[1],"%Y%m%d")
                if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(t)<=get_year_month_day(end_time):
                    FinalUrls.append((HTTPS,url+'/'+s))

    def getURL_FTP(self,FinalUrls:list,url:tuple,start_time=None,end_time=None):
        host=url[0]
        path=url[1]
        Urls=(FTPN,(host,path,[]))
        if start_time==None and end_time==None:
            ftp=FTP(host)
            ftp.login()
            ftp.cwd(path)
            nlst=ftp.nlst()
            for f in nlst:
                if ".gz" in f:
                    Urls[1][2].append(f)
            FinalUrls.append(Urls)
        else:
            ftp=FTP(host)
            ftp.login()
            ftp.cwd(path)
            nlst=ftp.nlst()
            for f in nlst:
                y = int(f)
                if start_time.year<=y and y<=end_time.year:
                    ftp.cwd(path+"/"+f)
                    subnlst=ftp.nlst()
                    for sf in subnlst:
                        if ".gz" in sf:
                            # print(sf)
                            dt = sf.split(".")[2]
                            if len(dt)==6:
                                t=datetime.datetime.strptime(sf.split(".")[2],"%y%m%d")
                            elif len(dt)==8:
                                t=datetime.datetime.strptime(sf.split(".")[2],"%Y%m%d")
                            if get_year_month_day(start_time)<=get_year_month_day(t) and get_year_month_day(t)<=get_year_month_day(end_time):
                                Urls[1][2].append(f+"/"+sf)
            FinalUrls.append(Urls)

class ASRANKGetter(IRRGetter):
    def getURL(self):
        return [(PY,"")]

class IRRHistoryGetter(IRRGetter):
    def getURL(self):
        FinalUrls=[]
        collectors=self.params.irr_history_collectors
        start_time=self.params.start_time
        end_time=self.params.end_time
        for c in collectors:
            d=IRR_HISTORY[c]
            if d[0]==HTTPS:
                self.getURL_HTTPS(FinalUrls,d[1],start_time,end_time)
            elif d[0]==FTPN:
                self.getURL_FTP(FinalUrls,d[1],start_time,end_time)
        return FinalUrls

class IRRDailyGetter(IRRGetter):
    def getURL(self):
        FinalUrls=[]
        for c in IRR_DAILY_URL.keys():
            d=IRR_DAILY_URL[c]
            if d[0]==HTTPS:
                self.getURL_HTTPS(FinalUrls,d[1])
            elif d[0]==FTPN:
                self.getURL_FTP(FinalUrls,d[1])
        return FinalUrls

class RPDDGetter(urlGetter):
    def getURL(self):
        FinalUrls=[]
        source1=self.findElement(RP_RRDP,PATTERN_STR["GZ"])
        for s in source1:
            FinalUrls.append((HTTPS,RP_RRDP+"/"+s))
        return FinalUrls

class RPRSYNCGetter(urlGetter):
    def getURL(self):
        FinalUrls=[]
        source1=self.findElement(RP_RSYNC,PATTERN_STR["GZ"])
        for s in source1:
            FinalUrls.append((HTTPS,RP_RRDP+"/"+s))
        return FinalUrls

def getURLGetter(bp:base_params)->urlGetter:
    if bp.base_type=="BGP":
        return bgpGetter(bp)
    elif bp.base_type=="RPKI":
        return rpkiGetter(bp)
    elif bp.base_type=="IRR":
        return IRRHistoryGetter(bp)
    elif bp.base_type=="AS-RELATIONSHIP":
        return ASRelationGetter(bp)
    elif bp.base_type=="AS-ORGANIZATION":
        return ASOrganizationGetter(bp)
    else:
        return None
    
def getURLList(bp:base_params)->Tuple[list,list]:
    urllist = []
    client = Minio(
        "minio.lab:9000",
        access_key="cnic",
        secret_key="Cnic2022_",
        secure=False
    )
    urlgetter = getURLGetter(bp)
    urls = urlgetter.getURL()
    # return urls
    # print(urls)
    for data in urls:
        if data[0]==HTTPS:
            url = data[1]
            # print(url)
            file = getFileName(bp.base_type,url)
            # print(file)
            # print(file)
            p = tranPath(file)
            # print(p)
            try:
                client.stat_object(MINIO_BUCKET_NAME[bp.base_type],p)
                urllist.append((MINIO,url))
            except Exception:
                urllist.append((HTTPS,url))
            # print("checkout")
        else:
            detailed_urls = data[1][2]
            not_in_minio = []
            for detailed_url in detailed_urls:
                file = getFileName(bp.base_type,detailed_url)
                try:
                    client.stat_object(MINIO_BUCKET_NAME[bp.base_type],file)
                    urllist.append((MINIO,detailed_url))
                except Exception:
                    not_in_minio.append(detailed_url)
            if len(not_in_minio)>0:
                urllist.append((FTPN,(data[1][0],data[1][1],not_in_minio)))      
    return urllist

def getURLFromFile(filename)->list:
    client = Minio(
        "newminio:9000",
        access_key="cnic",
        secret_key="Cnic2022_",
        secure=False
    )
    f=open(filename,"r")
    urllist = []
    for line in f:
        data = datetime.datetime.strptime(line.strip(),"%Y-%m-%d %H:%M:%S")
        date0 = data.strftime("%Y.%m")
        date1 = data.strftime("%Y%m%d.%H%M")
        url = "%s/rrc00/%s/bview.%s.gz"%(BGP_RIPE_URL,date0,date1)
        fname = "rrc00_bview.%s.gz"%(date1)
        p = tranPath(fname)
        try:
            client.stat_object(MINIO_BUCKET_NAME["BGP"],p)
            urllist.append((MINIO,url))
        except Exception:
            urllist.append((HTTPS,url))
           
        # print(url)
    f.close()
    return urllist

'''
unit test
'''
if __name__ == '__main__':
    # print(getBGPFileName("http://archive.routeviews.org//route-views.amsix/bgpdata/2021.10/UPDATES/updates.20211012.0200.bz2"))
    getURLFromFile("./left.txt")
    # urlgetter=bgpGetter(base_params(
    #     start_time="2023-02-01-08:00",
    #     end_time="2023-02-01-08:00",
    #     bgpcollectors=["rrc03","rrc04","rrc05"],
    #     bgp_data_type=BGP_DATATYPE["ALL"]
    # ))
    # print(urlgetter.getURL())
        
    # pre = datetime.datetime(2020,1,1,0,0)
    # next=pre
    # stime=pre.strftime("%Y-%m-%d-%H:%M")
    # etime=next.strftime("%Y-%m-%d-%H:%M")
    # i=0
    # urllist=[]
    # while i<24:
    #     urlgetter=bgpGetter(base_params(
    #         start_time=stime,
    #         end_time=etime,
    #         bgpcollectors=["rrc00"],
    #         bgp_data_type=BGP_DATATYPE["ALL"]
    #     ))
    #     urllist += urlgetter.getURL()
    #     i+=1
    #     pre = pre+relativedelta(months=1)
    #     next = next+relativedelta(months=1)
    #     stime=pre.strftime("%Y-%m-%d-%H:%M")
    #     etime=next.strftime("%Y-%m-%d-%H:%M")
    # print(urllist)
    
    # urlgetter=rpkiGetter(base_params(
    #     rpkicollectors=["josephine.sobornost.net"],
    #     start_time="2022-10-26-05:00",
    #     end_time="2022-10-27-05:10"
    # ))
    # print(urlgetter.getURL())

    # urlgetter=RPKICloudflareGetter(base_params())
    # print(urlgetter.getURL())

    # urlgetter=ASRANKGetter(base_params())
    # print(urlgetter.getURL())

    # urlgetter=ASOrganizationGetter(base_params(
    #     start_time="2022-10-01-00:00",
    #     end_time="2022-10-02-00:00"
    # ))
    # print(urlgetter.getURL())

    # urlgetter=ASRelationGetter(base_params(
    #     start_time="2022-11-01-00:00",
    #     end_time="2022-11-17-12:00"
    # ))
    # print(urlgetter.getURL())

    # urlgetter=IPRIRGetter(base_params(
    #     start_time="2022-10-11-00:00",
    #     end_time="2022-10-12-00:00",
    #     ipcollectors="all",
    # ))
    # print(urlgetter.getURL())

    # urlgetter=IRRDailyGetter(base_params())
    # print(urlgetter.getURL())
        
    # urlgetter=IRRHistoryGetter(base_params(
    #     start_time="2022-10-11-00:00",
    #     end_time="2022-10-12-00:00",
    #     irrhistorycollectors="all"
    # ))
    # print(urlgetter.getURL())

    # urlgetter=RPDDGetter(base_params())
    # print(urlgetter.getURL())
        
    # urlgetter=RPRSYNCGetter(base_params())
    # print(urlgetter.getURL())
       