
from downloadProcess import *
from tools import *
from constant import *
import os
from dateutil.relativedelta import relativedelta

GROUPNUM=10

class downloadByParams:
    def __init__(self,base_type:str,urllist:list,destination:str) -> None:
        self.base_type = base_type
        self.urllist = urllist
        self.destination = destination
        #print(self.destination)
        #print(self.urllist)
        if destination=="":
            print("empty path")
            pass
        else:
            try:
                os.stat(self.destination)
            except:
                os.mkdir(self.destination)
            else:
                pass
    
    def mission_divider(self,urllist:list):
        hard_task=[]
        normal_task=[]
        d_hard_task=[]
        d_normal_task=[]
        mission=[]
        if len(urllist)<=GROUPNUM:
            divider=1
            mission=[urllist[i:i + divider] for i in range(0, len(urllist), divider)]
        else:
            for url in urllist:
                if url[0]==HTTPS:
                    if "rib" in url[1] or "bview" in url[1] or "amber.massars.net" in url[1] or "all-path" in url[1]:
                        hard_task.append(url)
                    else:
                        normal_task.append(url)
                elif url[0]==FTPN:
                    hard_task.append(url)
                elif url[0]==MINIO:
                    normal_task.append(url)
                else:
                    hard_task.append(url)
            
            if len(hard_task)==0:
                pass 
            else:
                h_divider=len(hard_task)//GROUPNUM
                if len(hard_task)<=GROUPNUM:
                    h_divider=1
                d_hard_task=[hard_task[i:i + h_divider] for i in range(0, len(hard_task), h_divider)]

            if len(normal_task)==0:
                pass 
            else:
                n_divider=len(normal_task)//GROUPNUM
                if len(normal_task)<=GROUPNUM:
                    n_divider=1
                d_normal_task=[normal_task[i:i + n_divider] for i in range(0, len(normal_task), n_divider)]    

            i=0
            while i<min(len(d_normal_task),len(d_hard_task)):
                mission.append(d_hard_task[i]+d_normal_task[i])
                i+=1
            if len(d_normal_task)>len(d_hard_task):
                while i<len(d_normal_task):
                    mission.append(d_normal_task[i])
                    i+=1
            elif len(d_normal_task)<len(d_hard_task):
                while i<len(d_hard_task):
                    mission.append(d_hard_task[i])
                    i+=1
            else:
                pass
        return mission

    def start_on(self):
        urllist=self.urllist
        #print(len(urllist))
        # divider=10
        split=self.mission_divider(urllist)
        # print(split)
        downloadprocess=[]
        for s in split:
            downloadprocess.append(downloadProcess(self.base_type,s,self.destination))
        for i in range(len(split)):
            downloadprocess[i].start()
        for i in range(len(split)):
            downloadprocess[i].join()

'''
unit test
'''
if __name__=="__main__":
    urlgetter=bgpGetter(base_params(
        start_time="2022-10-26-00:00",
        end_time="2022-10-26-01:00",
        bgpcollectors=["rrc00","rrc26"],
        bgp_data_type=BGP_DATATYPE["ALL"]
    ))
    bgpdbp=downloadByParams(
        urllist=urlgetter.getURL(),  
        destination="../data/output",
        save_by_collector=0
    )
    bgpdbp.start_on()
    
    # bgpdbp=downloadByParams(
    #     urlgetter=bgpGetter(base_params(
    #         start_time="2023-02-01-08:00",
    #         end_time="2023-02-01-08:00",
    #         bgpcollectors=["rrc03","rrc04","rrc05"],
    #         bgp_data_type=BGP_DATATYPE["RIBS"]
    #     )),
    #     destination="./2023.0201_rib_2",
    #     save_by_collector=0
    # )
    # bgpdbp.start_on()
    
    # print(len(RouteViews))
    # pre = datetime.datetime(2020,1,1,0,0)
    # next=pre+datetime.timedelta(days=1)
    # stime=pre.strftime("%Y-%m-%d-%H:%M")
    # etime=next.strftime("%Y-%m-%d-%H:%M")
    # i=0
    # while i<24:
    #     bgpdbp=downloadByParams(
    #         urlgetter=bgpGetter(base_params(
    #             start_time=stime,
    #             end_time=etime,
    #             bgpcollectors=["rrc00"],
    #             bgp_data_type=BGP_DATATYPE["UPDATES"]
    #         )),
    #         destination="./rrc00_2020_updates/"+stime,
    #         save_by_collector=0
    #     )
    #     bgpdbp.start_on()
    #     i+=1
    #     pre = pre+relativedelta(months=1)
    #     next = next+relativedelta(months=1)
    #     stime=pre.strftime("%Y-%m-%d-%H:%M")
    #     etime=next.strftime("%Y-%m-%d-%H:%M")
    
    # rpkidbp=downloadByParams(
    #     urlgetter=rpkiGetter(base_params(
    #         rpkicollectors=["josephine.sobornost.net"],
    #         start_time="2022-10-26-05:00",
    #         end_time="2022-10-26-05:10"
    #     )),
    #     destination="./rpkidata",
    #     save_by_collector=1
    # )
    # rpkidbp.start_on()
    
    # rpkicfdbp=downloadByParams(
    #     urlgetter=RPKICloudflareGetter(base_params()),
    #     destination="./rpkidata",
    #     save_by_collector=1
    # )
    # rpkicfdbp.start_on()

    # asrankdbq=downloadByParams(
    #     urlgetter=ASRANKGetter(base_params()),
    #     destination="/data/asrank/"
    # )
    # asrankdbq.start_on()

    # asrdbp=downloadByParams(
    #     urlgetter=ASOrganizationGetter(base_params(
    #         start_time="2022-10-01-00:00",
    #         end_time="2022-10-02-00:00"
    #     )),
    #     destination="./asorg"
    # )
    # asrdbp.start_on()

    # asrsdbp=downloadByParams(
    #     urlgetter=ASRelationGetter(base_params(
    #         start_time="2022-11-01-00:00",
    #         end_time="2022-11-17-12:00"
    #     )),
    #     # destination="/data/asrel/"
    #     destination="./asrel"
    # )
    # asrsdbp.start_on()

    # bgpdbp=downloadByParams(
    #     urlgetter=IPRIRGetter(base_params(
    #         start_time="2022-10-11-00:00",
    #         end_time="2022-10-12-00:00",
    #         ipcollectors="all",
    #     )),
    #     destination="./irrdata",
    #     save_by_collector=1
    # )
    # bgpdbp.start_on()

    # irrddbq=downloadByParams(
    #     urlgetter=IRRDailyGetter(base_params()),
    #     destination="./irrdata",
    #     save_by_collector=1
    # )
    # irrddbq.start_on()
    # error_checking("/data/irrdata/ErrorInfo.txt")

    # irrhdbq=downloadByParams(
    #     urlgetter=IRRHistoryGetter(base_params(
    #         start_time="2022-10-11-00:00",
    #         end_time="2022-10-12-00:00",
    #         irrhistorycollectors="all"
    #     )),
    #     destination="./irrdata",
    #     save_by_collector=1
    # )
    # irrhdbq.start_on()

    # rp = downloadByParams(
    #     urlgetter=RPDDGetter(base_params()),
    #     destination="/data/rpdata-rrdp",
    #     save_by_collector=0
    # )
    # rp.start_on()
    # error_checking("/data/rpdata-rpdd/ErrorInfo.txt")

    # rp = downloadByParams(
    #     urlgetter=RPRSYNCGetter(base_params()),
    #     destination="/data/rpdata-rsync",
    #     save_by_collector=0
    # )
    # rp.start_on()
    # error_checking("/data/rpdata-rsync/ErrorInfo.txt")
