import os
from matplotlib import pyplot as plt
import json


def plot_attribute(file, attr_name:str):
    with open(file, 'r') as f:
        content = f.read()
        data = json.loads(content)
    res_list = []
    for l in data:
        res_list.append((l[attr_name], l['label'], l['index']))
    res_list = sorted(res_list, key=lambda x: x[2])
    res = [float(i[0]) for i in res_list]
    anomaly = [float(i[0]) for i in res_list if i[1] == '1']
    anomaly_index = [i[2] for i in res_list if i[1] == '1']
    ax = plt.subplot()
    l1, = ax.plot(range(1, len(res_list)+1), res, color='b', label='normal')
    l2, = ax.plot(anomaly_index, anomaly, color='r', label='anomaly')
    ax.legend(handles=[l1,l2])

    ax.set_xlabel('index')
    ax.set_ylabel('value')
    plt.savefig(f'{attr_name}.png', dpi=300)

if __name__ == "__main__":
    path = '/data/wuzheng_data/anomaly_event/route_leak/event2/'
    file = 'graphfeatures.json'
    plot_attribute(path+file, 'pagerank')
