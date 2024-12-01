import networkx as nx
import os
import json
from tqdm import tqdm  # 导入进度条模块
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 读取文件并提取数据
def read_bgp_rib(file_path):
    rib_data = []
    with open(file_path, "r") as f:
        for line in tqdm(f, desc="Reading RIB data", unit="line", ncols=100, dynamic_ncols=True):  # 添加进度条并设置百分比
            # 跳过空行或无效行
            if not line.strip():
                continue

            # 按 '|' 分隔每一行的数据
            fields = line.strip().split('|')

            # 确保字段数量足够
            if len(fields) < 6:
                print(f"Skipping invalid line: {line}")
                continue

            # 提取需要的字段（假设按位置提取）
            next_hop = fields[3]  # 第4列是 next_hop
            as_path = fields[6]  # 第7列是 as_path

            # 添加到 RIB 数据中
            rib_data.append({"next_hop": next_hop, "as_path": as_path})

    return rib_data

# 构建图
def build_graph_from_rib(rib_data):
    G = nx.Graph()  # 使用无向图

    for entry in tqdm(rib_data, desc="Building graph", unit="entry", ncols=100, dynamic_ncols=True):  # 添加进度条并设置百分比
        as_path = entry["as_path"]

        if not as_path:  # 如果没有 AS 路径，跳过
            continue

        as_list = as_path.split(' ')  # 将 AS 路径分割成 AS 列表

        # 如果 AS 列表长度不足 2，说明没有足够的边来连接，跳过
        if len(as_list) < 2:
            continue

        # 遍历 AS 列表中的每一对 AS，构建图的边
        for i in range(len(as_list) - 1):
            # 添加边到图中
            G.add_edge(as_list[i], as_list[i + 1])

    return G

# 计算图特征
def calculate_graph_features(G):
    features = {}

    # 原来的特征
    features['num_nodes'] = len(G.nodes)
    features['num_edges'] = len(G.edges)
    degrees = dict(G.degree())
    features['avg_degree'] = np.mean(list(degrees.values()))
    features['clustering_coefficient'] = nx.average_clustering(G)
    
    # 新的特征
    if nx.is_connected(G):
        features['avg_shortest_path_length'] = nx.average_shortest_path_length(G)
    else:
        features['avg_shortest_path_length'] = None

    features['is_connected'] = nx.is_connected(G)
    features['degree_centrality'] = np.mean(list(nx.degree_centrality(G).values()))
    features['betweenness_centrality'] = np.mean(list(nx.betweenness_centrality(G).values()))
    features['pagerank'] = np.mean(list(nx.pagerank(G).values()))

    return features

# 保存特征到JSON文件
def save_features_to_json(features, output_folder):
    path = output_folder + "json"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # 如果文件夹不存在，创建文件夹
    
    output_filename = f"graph_features_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, 'w') as json_file:
        json.dump(features, json_file, indent=4)

    print(f"Graph features saved to {output_path}")
    return output_path

# 主函数
if __name__ == "__main__":
    file_path = "/home/whm/Code/bgp/BGP-Security/BGP-Security/code/bgp-analyze/priming_data/txt/route-views.amsix/test.txt"  # RIB 数据文件的路径
    rib_data = read_bgp_rib(file_path)  # 读取数据

    # 打印 rib_data 确认数据是否正确
    print(f"Loaded {len(rib_data)} entries from the file.")

    # 构建图
    graph = build_graph_from_rib(rib_data)

    # 打印图的一些信息
    print(f"Number of nodes in the graph: {len(graph.nodes)}")
    print(f"Number of edges in the graph: {len(graph.edges)}")

    # 计算图特征
    features = calculate_graph_features(graph)

    # 打印计算的图特征
    print("Graph Features:")
    for feature, value in features.items():
        print(f"{feature}: {value}")

    # 保存图特征到JSON文件
    output_folder = "/home/whm/Code/bgp/BGP-Security/BGP-Security/code/bgp-analyze-whm/data/"
    save_features_to_json(features, output_folder)

    # 保存图像到指定文件夹
    output_image_path = os.path.join(output_folder, "graph/bgp_graph_20211004.png")

    # 可视化图并保存到文件
    plt.figure(figsize=(12, 12))  # 设置图的尺寸
    nx.draw(graph, with_labels=True, node_size=500, node_color='skyblue', font_size=8)
    plt.title("BGP Network Graph")
    plt.savefig(output_image_path)  # 保存图像到指定路径
    plt.close()  # 关闭图像以释放资源

    print(f"Graph image saved to {output_image_path}")
