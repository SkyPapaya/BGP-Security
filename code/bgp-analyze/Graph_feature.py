import networkx as nx
import numpy as np
from Routes import Routes
import os
import json
import multiprocessing as mp
from multiprocessing import Process, JoinableQueue, Manager
import time
from Data_generator import data_generator_wlabel


# second time transfer to '%Y-%m-%d %H:%M:%S'.
def s2t(seconds:int) -> str:
    utcTime = time.gmtime(seconds)
    strTime = time.strftime("%Y-%m-%d %H:%M:%S",utcTime)
    return strTime

# str time transfer to second time.
def t2s(str_time:str) -> int:
    time_format = '%Y-%m-%d %H:%M:%S'
    time_int = int(time.mktime(time.strptime(str_time, time_format)))
    return time_int

def dictKeys(d, keys):
    subD = {}
    keys2 = dict(d).keys()
    for k in keys:
        if(k in keys2):
            subD[k] = d[k]
    return(subD)

'''
extract Graph-based features
'''

def num_of_nodes(graph):
    return len(graph.nodes)

def num_of_edges(graph):
    return len(graph.edges)

def degree(graph):
    d = graph.degree()
    return d

# centrality measurement
def degree_centrality(G):
    d = nx.degree_centrality(G)
    # sub = dictKeys(d, nodes)
    return np.average(list(d.values()))

# the computing rate is too slow
def betweenness_centrality(G):
    d = nx.betweenness_centrality(G)
    return np.average(list(d.values()))

def local_clustering(G):
    d = nx.triangles(G)
    return np.average(list(d.values()))

def pagerank(G):
    d = nx.pagerank(G)
    return np.average(list(d.values()))

# Clique measurement
def clique_measure(G):
    cliques = list(nx.find_cliques(G))
    numclique = len(cliques)
    return numclique

def average_neighbor_degree(G):
    degrees = nx.degree(G)
    d = sum(dict(degrees).values())/len(degrees)
    return d

def clustering_coefficient(G):
    d = nx.clustering(G)
    return np.average(list(d.values()))

# consume much time
def eccentricity(G):
    res = 0
    if nx.is_connected(G):
        res = nx.eccentricity(G)
    else:
        d = nx.connected_components(G)
        res = len(max(d,key=len))
    return res


'''
build the network by the routes.
'''
def buildGraph(routes):
    # build the graph from priming data.
    graph = nx.Graph()
    edges = set()
    for prefix in routes.keys():
        for peer_as in routes[prefix]:
            if routes[prefix][peer_as] != None:
                as_path = routes[prefix][peer_as]
                if not ('{' in as_path):
                    as_list = as_path.split(' ')
                    for i in range(len(as_list)-1):
                        if as_list[i] != as_list[i+1]:
                            edges.add((as_list[i], as_list[i+1]))                 
    graph.add_edges_from(edges)
    return graph

def updateGraph(G, addedge, removeedge):
    G.add_edges_from(addedge)
    G.remove_edges_from(removeedge)
    return G

def get_focus_nodes(add_edges, remove_edges):
    # get the impacted as by updates.

    focus_nodes = set()
    for i in add_edges:
        focus_nodes.add(i[0])
        focus_nodes.add(i[1])
    for j in remove_edges:
        focus_nodes.add(j[0])
        focus_nodes.add(j[1])
    return focus_nodes



''' extract the overall feature set '''
class GraphFeature():
    def __init__(self):
        # self.G = G
        self.features = {}
    
    def init(self):
        self.features['num_of_nodes'] = 0
        self.features['num_of_edges'] = 0
        self.features['degree_centrality'] = 0
        # self.features['betweenness_centrality'] = 0
        self.features['num_cliques'] = 0
        self.features['local_clustering'] = 0
        self.features['average_neighbor_degree'] = 0
        self.features['clustering_coefficient'] = 0
        self.features['eccentricity'] = 0
        self.features['pagerank'] = 0
        self.features['index'] = 0
        self.features['label'] = None

    def extract_features(self, G, label, index):
        self.init()
        self.features['index'] = index
        
        self.features['label'] = label
        
        self.features['num_of_nodes'] = num_of_edges(G)
        
        self.features['num_of_edges'] = num_of_nodes(G)
        
        self.features['degree_centrality'] = degree_centrality(G)
        
        # self.features['betweenness_centrality'] = betweenness_centrality(G)
        self.features['num_cliques'] = clique_measure(G)
        
        self.features['local_clustering'] = local_clustering(G)
        
        self.features['average_neighbor_degree'] = average_neighbor_degree(G)
        
        self.features['clustering_coefficient'] = clustering_coefficient(G)
        
        self.features['pagerank'] = pagerank(G)
        
        # self.features['eccentricity'] = eccentricity(G)


def Producer(collector, path,  start_time, end_time, anomaly_start_time, anomaly_end_time, Period, q):
    print('Have started Producer!')
    if t2s(start_time) > t2s(end_time):
        print('Error: Starting time is bigger than ending time')
        raise TypeError

    if t2s(anomaly_start_time) > t2s(anomaly_end_time):
        print('Error: Starting time is bigger than ending time')
        raise TypeError

    priming_path = path + 'priming_data/txt/' + collector
    r = Routes(priming_path)
    r.collect_routes()
    r1 = r.routes
    print('Complete collection!')
    init_graph = buildGraph(r1)
    Period = 1
    updates_files = sorted([os.path.join(data_path, i) for i in os.listdir(data_path)])
    a = data_generator_wlabel(updates_files, Period, start_time= start_time, end_time= end_time, anomaly_start_time= anomaly_start_time, anomaly_end_time= anomaly_end_time)


    idx = 0
    G = init_graph
    print('starting produce instance and update the graph!')
    for update in a:
        idx += 1
        label = update[1]
        update = update[0]
        addedge, removeedge = r.compute_edge(update)
        graph = updateGraph(G, addedge, removeedge)
        q.put((idx, label, graph))
        G = graph
        if idx == 8:
            break
    q.join()
        

def Consumer(q, fea_queue):
    pid = os.getpid()
    print('Have started Consumer!', pid)
    GF = GraphFeature()
    # graphfeature = []
    while True:
        idx, label, graph = q.get()
        GF.extract_features(graph, label, index=idx)
        f = GF.features
        print(f'Consumer {pid} feature:', f)
        fea_queue.put(f.copy())
        q.task_done()

if __name__ == "__main__":
    
    # initialized info.
    collector = 'route-views.amsix'
    path = "/home/skypapaya/code/BGP-Security/code/bgp-analyze/"
    data_path = path + 'txt/' + collector +'/20211004'
    start_time = "2021-10-04 00:00:00"
    end_time = "2021-10-04 22:45:00"

    anomaly_start_time = "2021-10-04 15:07:00"
    anomaly_end_time = "2021-10-04 21:49:00"
    period = 1
    q = JoinableQueue(10)
    feature_queue = Manager().Queue()

    log_list = Manager().dict()
    producer = Process(target=Producer, args=(collector, path, start_time, end_time, anomaly_start_time, anomaly_end_time, period, q))
    
    num_consumer = 4
    consumer_list = []
    for i in range(num_consumer):
        consumer_list.append(Process(target=Consumer, args=(q, feature_queue,)))
    
    producer.start()

    for i in range(num_consumer):
        consumer_list[i].daemon = True



    for i in range(num_consumer):
        consumer_list[i].start()
    
    producer.join()
    print('producer Over!')

    print('Data over!')
    feature_list = []
    while not feature_queue.empty():
        feature_list.append(feature_queue.get())
    
    # write the results in the txt.
    with open('graphfeatures.json','w') as f:
        data = json.dumps(feature_list)
        f.write(data)

    print(feature_list)