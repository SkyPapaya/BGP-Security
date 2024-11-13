# BGPDownloader
支持多种数据类型采集（bgp/rpki/irr/as-relationship/as-organization）

数据采集过程首先根据需求获取相关url，再判断数据存储系统中是否已存在所需数据，最后将数据存放至目标目录中。

# 指令格式
```
examlpe: python download.py -s 2024-05-01-00:00 -e 2024-05-02-00:00 -t BGP:UPDATES -c rrc00 -d ../downloaded_data/
```
-s : 开始时间，格式%Y-%m-%d-%H:%M

-e : 结束时间，格式%Y-%m-%d-%H:%M

-t : 数据类型，格式TYPE:SUBTYPE
```
BGP（BGP的所有数据）
BGP:UPDATES（仅采集BGP Updates数据）
BGP:RIB（仅采集BGP RIB数据）
RPKI
RPKI:CSV
IRR
AS-Organization
AS-Relationship(AS-Relationship所有数据)
AS-Relationship:1(AS-Relationship 1类数据)
AS-Relationship:2(AS-Relationship 2类数据)
```

-c : 所用数据采集点，格式如下
```
BGP采集点：三种模式（单个采集点，多个采集点，所有采集点）
- 单采集点：constant.py中BGP_RIPE和RouteViews数组中的任意一个元素
- 多采集点：constant.py中BGP_RIPE和RouteViews数组中的任意多个元素，用','连接
- 所有采集点：三种取值（ripe表示所有ripe采集点，routeviews同理，all表示ripe+routeviews的所有采集点）
        
RPKI采集点：三种模式（单个采集点，多个采集点，所有采集点）
- 单采集点：constant.py中RPKI_RIPE和RPKI_NTT数组中的任意一个元素
- 多采集点：constant.py中RPKI_RIPE和RPKI_NTT数组中的任意多个元素，用','连接
- 所有采集点：三种取值（ripe表示所有ripe采集点，ntt同理，all表示ripe+ntt的所有采集点）

IRR采集点：三种模式（单个采集点，多个采集点，所有采集点）
- 单采集点：constant.py中IRR_HISTORY_SET数组中的任意一个元素
- 多采集点：constant.py中IRR_HISTORY_SET数组中的任意多个元素，用','连接
- 所有采集点：一种取值（all表示所有采集点）

AS-Organization/AS-Relationship：无需指定采集点，因此不需要选择-c
``` 


-d ：目标目录（非必选，若不选择-d，则将数据采集后存放至minio中；若选择，其格式为文件目录格式"/home/.."）
