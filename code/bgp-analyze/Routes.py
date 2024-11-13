import os
from collections import defaultdict


class Routes:
    '''
    From RIB or priming updates datas, extract routes info as truth-grouding info.
    routes:
    {
        prefix: {peer_as: [as_path]}
    }
    '''

    def __init__(self, path):
        self.path = path
        self.routes = defaultdict(lambda: defaultdict(str))
        self.mode = "updates"

    def collect_routes(self):
        if self.mode == 'updates':
            # 获取路径中的所有文件
            files = os.listdir(self.path)
            # 遍历所有文件
            for f in files:
                f_path = os.path.join(self.path, f)
                # 只处理文件而不是目录
                if os.path.isfile(f_path):
                    with open(f_path, 'r') as file:
                        for l in file:
                            if l.strip() != '':
                                line = l.strip().split('|')
                                prefix = line[5]
                                peer_asn = line[4]
                                op_ = line[2]
                                if op_ == 'A':
                                    if '{' not in line[6]:
                                        self.routes[prefix][peer_asn] = line[6]
                                elif op_ == 'W':
                                    self.routes[prefix][peer_asn] = None
                                else:
                                    pass

    def compute_edge(self, updates, directed=False):
        # routes format: routes[prefix][peer_asn] = as_path
        # updates format: [bgpdump_line, label]
        edge_updates = []
        for update in updates:
            time_ = update[1]
            op_ = update[2]
            peer_as = update[4]
            prefix_ = update[5]
            if op_ == 'A':
                as_path = update[6]
                if as_path != self.routes[prefix_][peer_as]:
                    if '{' not in as_path:
                        self.routes[prefix_][peer_as] = as_path
                        as_path_list = as_path.split(' ')
                        for l in range(len(as_path_list) - 1):
                            if as_path_list[l] != as_path_list[l + 1]:
                                edge_updates.append(('A', [as_path_list[l], as_path_list[l + 1]]))

            elif op_ == 'W':
                if self.routes[prefix_][peer_as] != None:
                    as_path_list = self.routes[prefix_][peer_as].split(' ')
                    for p in range(len(as_path_list) - 1):
                        if as_path_list[p] != as_path_list[p + 1]:
                            edge_updates.append(('W', [as_path_list[p], as_path_list[p + 1]]))
                    self.routes[prefix_][peer_as] = None
            else:
                pass

        # undirected graph or directed
        edge_combine = {}
        if not directed:
            for e in edge_updates:
                edge = tuple(sorted(e[1]))
                if edge not in edge_combine:
                    edge_combine[edge] = 0
                if e[0] == 'W':
                    edge_combine[edge] -= 1
                elif e[0] == 'A':
                    edge_combine[edge] += 1
        else:
            for e in edge_updates:
                edge = tuple(e[1])  # Directed edges use as is, no sorting
                if edge not in edge_combine:
                    edge_combine[edge] = 0
                if e[0] == 'W':
                    edge_combine[edge] -= 1
                elif e[0] == 'A':
                    edge_combine[edge] += 1

        add_edges = []
        remove_edges = []

        for idx in edge_combine:
            if edge_combine[idx] > 0:
                add_edges.append(idx)
            elif edge_combine[idx] < 0:
                remove_edges.append(idx)

        return (add_edges, remove_edges)
