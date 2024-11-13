import getopt,sys
import os

from base import *
from URLGetter import *
from downloadByParams import downloadByParams
import time

# python3 download.py -s 2023-07-21-00:00 -e 2023-07-21-00:00 -t BGP:RIBS -c routeviews -d ../downloaded_data/routeviews_rib

if __name__=="__main__":
    start_time = "2021-10-04-00:00"
    end_time = "2021-10-05-00:00"
    data_types = "BGP:UPDATES"
    collector = "route-views.amsix"
    destination = "/home/skypapaya/code/BGP/code/data/output/update_table"
    if not os.path.exists(destination):
        print("unknown dir")
    st = time.time()
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"hs:e:t:c:d:",["help","start_time=","end_time=","data_type=","collector=","dest="])
    except getopt.GetoptError:
        print('Error format!')
        print('download.py -s <start_time> -e <end_time> -t <data_type> -c <collector> -d <dest folder>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print('download.py -s <start_time> -e <end_time> -t <data_type> -c <collector> -d <dest folder>')
            sys.exit()
        elif opt in ("-s", "--start_time"):
            start_time = arg
        elif opt in ("-e", "--end_time"):
            end_time = arg
        elif opt in ("-t", "--data_type"):
            data_types = arg
        elif opt in ("-c", "--collector"):
            collector = arg
        elif opt in ("-d", "--dest"):
            destination = arg
    bp = set_base_params(start_time,end_time,data_types,collector)
    urllist = getURLList(bp)
    # urllist = getURLFromFile("./todown.txt")
   # print(urllist)
    downloadByParams(
        base_type = bp.base_type,
        # base_type="BGP",
        urllist=urllist,
        destination=destination).start_on()
    et = time.time()
    print(et-st)