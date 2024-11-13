import datetime
import warnings
from constant import *


class base_params:
    '''
    用于存放所需数据包的基本参数，例如起止时间、数据类型等，并对这些参数做一些基本的检查

    属性:
        start_time: 开始时间
        end_time: 结束时间
        bgp_data_type: bgp数据类型
        bgp_collectors: bgp采集器
        bgp_data_type: ripe提供的RPKI数据的类型
        rpki_collectors: rpki采集器
        ip_collectors: ip注册数据采集器
        irr_history_collectors: irr历史数据采集器

        此处不设置irr每日数据采集器，我们默认irr每日数据需要下载所有的采集点的数据，因此不设置可选参数
    '''
    __slot__=["base_type","start_time","end_time","bgp_data_type","bgp_collectors","rpki_data_type","rpki_collectors","asrel_data_type","ip_collectors","irr_history_collectors"]

    def __init__(self,
        base_type=None,
        start_time=None,
        end_time=None,
        bgp_data_type=None,
        bgpcollectors=None,
        rpki_data_type=None,
        rpkicollectors=None,
        asrel_data_type=None,
        ipcollectors=None,
        irrhistorycollectors=None
    ):
        if base_type==None:
            warnings.warn("Not set basic type!",UserWarning)
            exit(1)
        elif base_type not in BASE_TYPE_LIST:
            warnings.warn("ERROR basic type!",UserWarning)
            exit(1)
        else:
            self.base_type = base_type
            
        # 这里start_time和end_time需要设置为datetime类型
        if start_time==None:
            pass
        elif isinstance(start_time,str):
            self.start_time=datetime.datetime.strptime(start_time,"%Y-%m-%d-%H:%M")
        elif isinstance(start_time,datetime.datetime):
            self.start_time=start_time
        else:
            warnings.warn("Incorrect DataType:start_time",UserWarning)
            exit(1)

        if end_time==None:
            pass
        elif isinstance(end_time,str):
            self.end_time=datetime.datetime.strptime(end_time,"%Y-%m-%d-%H:%M")
        elif isinstance(end_time,datetime.datetime):
            self.end_time=end_time
        else:
            warnings.warn("Incorrect DataType:end_time",UserWarning)
            exit(1)
        
        if start_time!=None and end_time!=None:
            if start_time>end_time:
                warnings.warn("start_time should be previous before end_time",UserWarning)
                exit(1)
                
        if bgp_data_type==None:
            self.bgp_data_type=BGP_DATATYPE["ALL"]
        elif isinstance(bgp_data_type,int):
            self.bgp_data_type=bgp_data_type
        elif isinstance(bgp_data_type,str):
            if bgp_data_type.lower()=="all":
                self.bgp_data_type=BGP_DATATYPE["ALL"]
            elif bgp_data_type.lower()=="ribs":
                self.bgp_data_type=BGP_DATATYPE["RIBS"]
            elif bgp_data_type.lower()=="updates":
                self.bgp_data_type=BGP_DATATYPE["UPDATES"]
        else:
            warnings.warn("Incorrect bgp data type",UserWarning)
            exit(1)

        # 检查bgpcollector
        if bgpcollectors==None:
            pass
        elif isinstance(bgpcollectors,str):
            self.bgp_collectors = []
            if bgpcollectors.lower()=="all":
                self.bgp_collectors=list(RouteViews)+list(BGP_RIPE)
            elif bgpcollectors.lower()=="routeviews":
                self.bgp_collectors=list(RouteViews)
            elif bgpcollectors.lower()=="ripe":
                self.bgp_collectors=list(BGP_RIPE)
            else:
                b = bgpcollectors.split(",")
                for c in b:
                    c = c.lower()
                    if c in RouteViews or c in BGP_RIPE:
                        self.bgp_collectors.append(c)
        elif isinstance(bgpcollectors,list):
            s=set()
            for c in bgpcollectors:
                if c.lower() in BGP_RIPE or c.lower() in RouteViews:
                    s.add(c)
            self.bgp_collectors=list(s)
        else:
            warnings.warn("Incorrect DataType:bgpcollectors",UserWarning)
            exit(1)
        
        if rpki_data_type==None:
            self.rpki_data_type=RPKI_DATATYPE["ALL"]
        elif isinstance(rpki_data_type,str):
            if rpki_data_type.lower()=="all":
                self.rpki_data_type=RPKI_DATATYPE["ALL"]
            elif rpki_data_type.lower()=="csv":
                self.rpki_data_type=RPKI_DATATYPE["CSV"]
            elif rpki_data_type.lower()=="tar":
                self.rpki_data_type=RPKI_DATATYPE["TAR"]
            elif rpki_data_type.lower()=="json":
                self.rpki_data_type=RPKI_DATATYPE["JSON"]
        else:
            warnings.warn("Incorrect rpki data type",UserWarning)
            exit(1)
        
        # 检查rpkicollectors
        if rpkicollectors==None:
            pass
        elif isinstance(rpkicollectors,str):
            self.rpki_collectors = []
            if rpkicollectors.lower()=="all":
                self.rpki_collectors=list(RPKI_RIPE)+list(RPKI_NTT)
            elif rpkicollectors.lower()=="ntt":
                self.rpki_collectors=list(RPKI_NTT)
            elif rpkicollectors.lower()=="ripe":
                self.rpki_collectors=list(RPKI_RIPE)
            else:
                r = rpkicollectors.split(",")
                for c in r:
                    c = c.lower()
                    if c in RPKI_RIPE or c in RPKI_NTT:
                        self.rpki_collectors.append(c)
        elif isinstance(rpkicollectors,list):
            s=set()
            for c in rpkicollectors:
                if c.lower() in RPKI_RIPE or c.lower() in RPKI_NTT:
                    s.add(c)
            self.rpki_collectors=list(s)
        else:
            warnings.warn("Incorrect DataType:rpkicollectors",UserWarning)
            exit(1)
        
        if asrel_data_type==None:
            self.asrel_data_type=ASREL_DATATYPE["ALL"]
        elif isinstance(asrel_data_type,str):
            if asrel_data_type=="all":
                self.asrel_data_type=ASREL_DATATYPE["ALL"]
            elif asrel_data_type.lower()=="1":
                self.asrel_data_type=ASREL_DATATYPE["1"]
            elif asrel_data_type.lower()=="2":
                self.asrel_data_type=ASREL_DATATYPE["2"]
        else:
            warnings.warn("Incorrect asrel data type",UserWarning)
            exit(1)
        
        if ipcollectors==None:
            pass
        elif isinstance(ipcollectors,str):
            if ipcollectors.lower()=="all":
                self.ip_collectors=list(IP_COLLECTORS)
            elif ipcollectors.lower() in IP_COLLECTORS:
                self.ip_collectors=[ipcollectors.lower()]
            else:
                warnings.warn("Incorrect Type:ipcollectors",UserWarning)
                exit(1)
        elif isinstance(ipcollectors,list):
            s=set()
            for c in ipcollectors:
                if c.lower() in IP_COLLECTORS:
                    s.add(c.lower())
            self.ip_collectors=list(s)
        else:
            warnings.warn("Incorrect Type:ipcollectors",UserWarning)
            exit(1)
        
        if irrhistorycollectors==None:
            pass
        elif isinstance(irrhistorycollectors,str):
            if irrhistorycollectors.upper()=="ALL":
                self.irr_history_collectors=list(IRR_HISTORY_SET)
            elif irrhistorycollectors.upper() in IRR_HISTORY_SET:
                self.irr_history_collectors=[irrhistorycollectors.upper()]
        elif isinstance(irrhistorycollectors,list):
            s=set()
            for c in irrhistorycollectors:
                if c.upper() in IRR_HISTORY_SET:
                    s.add(c.upper())
            self.irr_history_collectors=list(s)
        else:
            warnings.warn("Incorrect Type:irrcollectors",UserWarning)
            exit(1)


def set_base_params(start_time:str,end_time:str,data_types:str,collector:str)->base_params:
    bp = None
    d = data_types.split(":")
    data_type=d[0]
    if data_type=="BGP":
        if d[1]=='':
            sub_type = "all"
        else:
            sub_type = d[1]
        bp = base_params(
            base_type=data_type,
            start_time=start_time,
            end_time=end_time,
            bgp_data_type=sub_type,
            bgpcollectors=collector
        )
    elif data_type=="RPKI":
        if d[1]=='':
            sub_type = "all"
        else:
            sub_type = d[1]
        bp = base_params(
            base_type=data_type,
            start_time=start_time,
            end_time=end_time,
            rpki_data_type=sub_type,
            rpkicollectors=collector
        )
    elif data_type=="IRR":
        bp = base_params(
            base_type=data_type,
            start_time=start_time,
            end_time=end_time,
            irrhistorycollectors=collector
        )
    elif data_type=="AS-RELATIONSHIP":
        if d[1]=='':
            sub_type = "all"
        else:
            sub_type = d[1]
        bp = base_params(
            base_type=data_type,
            start_time=start_time,
            end_time=end_time,
            asrel_data_type=sub_type
        )
    elif data_type=="AS-ORGANIZATION":
        bp = base_params(
            base_type=data_type,
            start_time=start_time,
            end_time=end_time,
        )
    else:
        print("NOT support yet!")
        exit(0)
    return bp