
from datetime import datetime
from typing import Tuple
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import Tags
import io
import requests
import re
import datetime
from constant import *

def tranPath(old_file_name):
    if ".tal" in old_file_name:
        d = old_file_name.split("_")
        return "%s/%s.%s/%s"%(d[0],d[1][0:4],d[1][4:6],old_file_name)
    elif "as-rel" in old_file_name or "as-org" in old_file_name:
        return old_file_name
    elif "radb" in old_file_name:
        return old_file_name
    else:    
        old_file_pattern = r'(?P<file>(?P<collector>[\w\-\.]*)_(?P<type>[\w]*).(?P<datetime>(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}).(?P<time>\d{4,6})).(?P<ft>\w*))'
        result = re.match(old_file_pattern, old_file_name)
        return "{collector}/{year}.{month}/{file}".format(
        collector=result.group('collector'),
        year=result.group('year'),
        month=result.group('month'),
        file=result.group('file'),
        )


def get_year_month(datetime):
    return datetime.year*100+datetime.month

def get_year_month_day(datetime):
    return datetime.year*10000+datetime.month*100+datetime.day

def getFileName(base_type:str,url:str)->str:
    if base_type=="BGP":
        return getBGPFileName(url)
    elif base_type=="RPKI":
        return getRPKIFileName(url)
    elif base_type=="IRR":
        return getIRRFileName(url)
    elif base_type=="AS-RELATIONSHIP":
        return getASRELFileName(url)
    elif base_type=="AS-ORGANIZATION":
        return getASORGFileName(url)
    else:
        return None

def getBGPFileName(url:str)->str:
    data = url.replace("//","/").split('/')
    if len(data)==6:
        filename = "route-views2.oregon-ix.net_"+data[-1]
    else:
        filename = data[2]+"_"+data[-1]
    return filename

def getRPKIFileName(url:str)->str:
    n=url.replace("//","/")
    if n[-1]=='/':
        n = n[0:-1]
    print(n)
    data = n.split('/')
    # print(data)
    if "ripe" in url:
        filename=data[3]+"_"+data[4]+data[5]+data[6]+"_"+data[-1]
    else:
        filename=data[1]+"_"+data[-1]
    return filename

def getIRRFileName(url:str)->str:
    n=url.replace("//","/")
    data = n.split('/')
    return data[-1]

def getASRELFileName(url:str)->str:
    n=url.replace("//","/")
    if n[-1]=='/':
        n = n[0:-1]
    data = n.split('/')
    return data[-1]

def getASORGFileName(url:str)->str:
    n=url.replace("//","/")
    if n[-1]=='/':
        n = n[0:-1]
    data = n.split('/')
    return data[-1]

def set_time_out(url:str):
    timeout=BASE_TIMEOUT
    if "bview" in url or "rib" in url:
        timeout=LARGE_TIMEOUT
    elif "rpki" in url:
        if "amber.massars.net" in url:
            timeout=LARGE_TIMEOUT
        else:
            timeout=MEDIUM_TIMEOUT  
    return timeout

def getInfoFromURL(base_type:str,url:str)->Tuple[str,int,Tags]:
    n=url.replace("//","/")
    if n[-1]=='/':
        n = n[1:-1]
    data = n.split('/')
    name=""
    timeout=BASE_TIMEOUT
    tags = Tags.new_object_tags()
    if base_type=="BGP":
        if len(data)==6:
            collector = "route-views2.oregon-ix.net"
        else:
            collector=data[2]
        name=str(collector)+str("_")+str(data[-1])
        tmp = name.split("_")
        ndata = tmp[1].split(".")
        datatype = ndata[0]
        datatime = ndata[1]+"."+ndata[2]
        timeout=set_time_out(url)
        tags["Collector"] = collector
        tags["Time"] = datatime
        tags["Type"] = datatype
    elif base_type=="RPKI":
        if "ripe" in url:
            name=data[3]+"_"+data[4]+data[5]+data[6]+"_"+data[-1]
            collector=data[3]
            datatime=data[4]+data[5]+data[6]+".000000"
        else:
            name=data[1]+"_"+data[-1]
            collector=data[1]
            ndata=name.split("-")[1].split(".")[0]
            datatime=ndata[0:8]+"."+ndata[9:15]
        timeout=set_time_out(url)
        if ".csv" in name:
            tags["Type"] = "rpki_csv"
        else:
            tags["Type"] = "rpki"
        tags["Collector"] = collector
        tags["Time"] = datatime  
    elif base_type=="AS-RELATIONSHIP" or base_type=="AS-ORGANIZATION":
        name = data[-1]
        datatime = name.split(".")[0]
        tags["Time"] = datatime
    else:
        pass            
    return name,timeout,tags


def check_error_list(fname):
    ErrorList=[]
    client = Minio(
        "minio:90",
        access_key="cnic",
        secret_key="Cnic2022_",
        secure=False
    )
    with open(fname,"r") as f:
        for line in f:
            data=line.strip().split("|")
            name=data[0]
            timeout=int(data[1])
            url=data[2]        
            if "rpki" in name:
                if "rpki" in name:
                    urlsplit=url.replace("//","/").split('/')
                    if "ripe" in url:
                        collector=urlsplit[3]
                        datatime=urlsplit[4]+urlsplit[5]+urlsplit[6]+".000000"
                    else:
                        collector=urlsplit[1]
                        ndata=name.split("-")[1].split(".")[0]
                        datatime=ndata[0:8]+"."+ndata[9:15]
                    try:
                        r=requests.get(url,allow_redirects=True,verify=False,timeout=timeout)
                        tags = Tags.new_object_tags()
                        tags["Collector"] = collector
                        tags["Time"] = datatime
                        if ".csv" in name:
                            tags["Type"] = "rpki_csv"
                        else:
                            tags["Type"] = "rpki"
                        client.put_object("rpki",name,io.BytesIO(r.content),length=int(r.headers['Content-Length']),content_type=r.headers['Content-Type'],tags=tags)
                        print("redone: "+name)
                    except Exception as e:
                        ErrorList.append(line)
            else:
                tmp = name.split("_")
                collector = tmp[0]
                tmpd = tmp[1].split(".")
                datatype = tmpd[0]
                datatime = tmpd[1]+"."+tmpd[2]
                try:
                    r=requests.get(url,allow_redirects=True,verify=False,timeout=timeout)
                    tags = Tags.new_object_tags()
                    tags["Collector"] = collector
                    tags["Time"] = datatime
                    tags["Type"] = datatype
                    client.put_object("bgpdata",name,io.BytesIO(r.content),length=int(r.headers['Content-Length']),content_type=r.headers['Content-Type'],tags=tags)
                    print("redone: "+name)
                except Exception as e:
                    ErrorList.append(line)
    with open(fname,"w") as f:
        for url in ErrorList:
            f.writelines(url)

def set_name_collector(url):
    '''
    根据url设置文件名和采集器名
    '''
    data=url.replace("//","/").split('/')
    name=""
    collector=""
    if "rpki.cloudflare" in url:
        name=datetime.datetime.utcnow().strftime("%Y%m%d")+".json"
        collector="cloudflare"
    elif "rpki" in url:
        if "ripe" in url:
            name=data[3]+"_"+data[4]+data[5]+data[6]+"_"+data[-1]
            collector=data[3]
        else:
            name=data[1]+"_"+data[-1]
            collector=data[1]
    elif "as-relationships" in url:
        name=data[-1]
        collector=data[-2]
    elif "as-organizations" in url:
        name=data[-1]
    elif "delegated" in url or "assigned" in url or "legacy" in url:
        name=data[-1]
        collector=name.split("-")[1]
    elif "transfers" in url:
        if "latest" in url:
            name=datetime.datetime.utcnow().strftime("%Y%m%d%H%M")+".json"
            collector="/ripencc/transfers/"
        else:
            name=data[-1]
            collector=data[-4]+"/transfers/"
    elif "ftp" in url:
        name=data[-1]
        havedigit=bool(re.search(r'\d{6}', name))
        if havedigit:
            if "radb" in url:
                collector="radb"
            else:
                collector="lacnic"
        else:
            t=datetime.datetime.utcnow().strftime("%Y%m%d")
            name=t+"_"+name
            if "https" in url:
                collector=data[1].split(".")[1]
            else:
                collector=data[-1].split(".")[0]
                if "-" in collector:
                    collector=collector.split("-")[0]
    elif "idnic" in url:
        name=datetime.datetime.utcnow().strftime("%Y%m%d")+"_"+data[-1]
        collector="idnic"
    else:
        collector=data[2]
        name=str(collector)+str("_")+str(data[-1])
    return name,collector