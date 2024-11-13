'''
用于保存一些常量
'''

BASE_FOLDER = "/home/nizedong/downloaded_data/"

MAX_WAIT_TIME=200

BASE_TIMEOUT=400
MEDIUM_TIMEOUT=2000
LARGE_TIMEOUT=6000

BASE_TYPE_LIST = ["BGP","RPKI","IRR","AS-RELATIONSHIP","AS-ORGANIZATION"]

BGP_RIPE={"rrc00","rrc01","rrc02","rrc03","rrc04","rrc05","rrc06","rrc07","rrc08","rrc09","rrc10","rrc11","rrc12","rrc13","rrc14","rrc15","rrc16","rrc18","rrc19","rrc20","rrc21","rrc22","rrc23","rrc24","rrc25","rrc26"}
BGP_RIPE_URL="http://data.ris.ripe.net/"

RouteViews={"route-views2",
            "route-views3",
            "route-views4",
            "route-views5",
            "route-views6",
            "route-views7",
            "decix.jhb",
            "route-views.amsix",
            "amsix.ams",
            "route-views.bdix",
            "route-views.bknix",
            "route-views.chicago",
            "route-views.chile",
            "route-views.eqix",
            "route-views.flix",
            "route-views.gixa",
            "route-views.gorex",
            "iraq-ixp.bgw",
            "route-views.isc",
            "route-views.kixp",
            "route-views.jinx",
            "route-views.linx",
            "route-views.mwix",
            "route-views.napafrica",
            "route-views.nwax",
            "pacwave.lax",
            "pit.scl",
            "pitmx.qro",
            "route-views.phoix",
            "route-views.telxatl",
            "route-views.wide",
            "route-views.sydney",
            "route-views.saopaulo",
            "route-views2.saopaulo",
            "route-views.sg",
            "route-views.perth",
            "route-views.peru",
            "route-views.sfmix",
            "route-views.siex",
            "route-views.soxrs",
            "route-views.rio",
            "route-views.fortaleza",
            "route-views.uaeix",
            "route-views.ny",
            }
RouteViews_URL="http://archive.routeviews.org/"

RPKI_RIPE={"afrinic.tal","apnic-afrinic.tal","apnic-arin.tal","apnic-iana.tal","apnic-lacnic.tal","apnic-ripe.tal","apnic.tal","arin.tal","certstats","lacnic.tal","localcert.tal","ripencc.tal"}
RPKI_RIPE_URL="https://ftp.ripe.net/rpki/"

RPKI_NTT={"josephine.sobornost.net","amber.massars.net","view.rpki.co","dango.attn.jp"}

RPKI_CLOUDFLARE="https://rpki.cloudflare.com/rpki.json"

AS_RELATION_SERIAL_1="https://publicdata.caida.org/datasets/as-relationships/serial-1/"
AS_RELATION_SERIAL_2="https://publicdata.caida.org/datasets/as-relationships/serial-2/"

AS_ORGANIZATION="https://publicdata.caida.org/datasets/as-organizations/"

IP_COLLECTORS={"ripe","apnic","arin","afrinic","lacnic"}
IP_APNIC="https://ftp.apnic.net/stats/apnic/"
IP_ARIN="https://ftp.arin.net/pub/stats/arin/"
IP_RIPE="https://ftp.ripe.net/pub/stats/ripencc/"
IP_AFRINIC="https://ftp.ripe.net/pub/stats/afrinic/"
IP_LACNIC="https://ftp.apnic.net/stats/lacnic/"

RP_RRDP="https://rp-data.rpki.net/archive/ca.rg.net/rrdp/"
RP_RSYNC="https://rp-data.rpki.net/archive/ca.rg.net/rsync/"

ASRANK_GRAPHQL="python3 asrank-download.py -v -a asns.jsonl -o organizations.jsonl -l asnLinks.jsonl -u https://api.asrank.caida.org/v2/graphql"

HTTPS=1
FTPN=2
PY=3
MINIO=4

IRR_DAILY_COLLECTOR={"afrinic","altdb","apnic","arin","bboi","bell","canarie","host","idnic","jpirr","lacnic","level3","nestegg","nttcom","openface","panix","radb","reach","rgnet","ripe","tc"}

IRR_DAILY_URL=dict({
    'AFRINIC':(HTTPS,'https://ftp.afrinic.net/pub/dbase/afrinic.db.gz'),
    'APNIC':(FTPN,('ftp.apnic.net','/pub/apnic/whois/')),
    'IDNIC':(FTPN,('irr-mirror.idnic.net','')),
    'LACNIC':(HTTPS,'https://ftp.lacnic.net/lacnic/irr/lacnic.db.gz'),
    'RIPE':(FTPN,('ftp.ripe.net','/ripe/dbase/split/')),
    'JPIRR':(FTPN,('ftp.apnic.net','/public/apnic/whois-data/JPIRR/split/')),
    'RADB':(FTPN,('ftp.radb.net','/radb/dbase/'))
})

IRR_HISTORY_SET={'RADB','LACNIC'}
IRR_HISTORY=dict({
    'RADB':(FTPN,('ftp.radb.net','/radb/dbase/archive')),
    'LACNIC':(HTTPS,'https://ftp.lacnic.net/lacnic/irr/')
})

OTHER=dict({
    'ROGERS':(FTPN,('whois.rogerstelecom.net','/rogers'))
})

# BGP_DATATYPE=reverse_defaultdict({
#     1:'RIBS',
#     2:'UPDATES',
#     3:'ALL'
# })

BGP_DATATYPE=dict({
    'RIBS':1,
    'UPDATES':2,
    'ALL':3
})

RPKI_DATATYPE=dict({
    'CSV':"csv",
    'TAR':"tar",
    'JSON':"json",
    'ALL':"all"
})

ASREL_DATATYPE=dict({
    '1':1,
    '2':2,
    'ALL':3
})

# PATTERN_STR=reverse_defaultdict({
#     '^(((?:19|20)\d\d).(0?[1-9]|1[0-2]))':'YEAR_MONTH',
#     '((?:19|20)\d\d)/':'YEAR',
#     '((?:19|20)\d\d)':'YEAR_JSN',
#     '(0?[1-9]|1[0-2])':'MONTH',
#     '(0[1-9]|1\d|2\d)':'DAY',
#     '^rpki':'NTT',
#     '^updates':'UPDATES',
#     '.bz2$':'BZ2',
#     '^bview':'BVIEW',
#     '.gz$':'GZ',
#     '\d+':'INT',
#     '^delegated':'ARIN',
#     'transfer|.json$':'TRANSFERS'
# })


PATTERN_STR=dict({
    'YEAR_MONTH':'^(((?:19|20)\d\d).(0?[1-9]|1[0-2]))',
    'YEAR':'((?:19|20)\d\d)/',
    'YEAR_JSN':'((?:19|20)\d\d)',
    'MONTH':'(0?[1-9]|1[0-2])',
    'DAY':'(0[1-9]|1\d|2\d|3\d)',
    'NTT':'^rpki',
    'RIPE_RPKI':'.gz$|.csv$|.xz$',
    'UPDATES':'^updates',
    'BZ2':'.bz2$',
    'BVIEW':'^bview',
    'GZ':'.gz$',
    'INT':'\d+',
    'ARIN':'^delegated',
    'TRANSFERS':'transfer|.json$'
})

SQL_TABLE_NAME = {
    "BGP":"bgpdataindex",
    "RPKI":"rpkidataindex"
}

MINIO_BUCKET_NAME = {
    "BGP":"bgpdata",
    "RPKI":"rpkidata",
    "IRR":"irrdata",
    "AS-RELATIONSHIP":"asreldata",
    "AS-ORGANIZATION":"asorgdata"
}