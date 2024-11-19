import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


# 将时间戳转换为指定格式（60分钟区间）
def convert_to_time_interval(timestamp, interval=3600):
    return int(timestamp // interval * interval)


# 将时间戳转化为时分秒格式
def timestamp_to_time(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')


# 读取文件夹下的所有文件
def get_files_from_folder(folder_path):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]


# 统计AS路径长度变化
def plot_as_path_length_changes(folder_path, threshold, save_path):
    path_length_dict = {}  # 用于存储每个 AS 在各时间段的路径长度

    files = get_files_from_folder(folder_path)

    # 处理所有文件
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split('|')

                # 确保每行数据至少有 7 部分
                if len(parts) < 7:
                    print(f"Skipping malformed line: {line}")
                    continue  # 跳过格式不正确的行

                timestamp = float(parts[1])  # 时间戳
                as_path = parts[6]  # AS路径

                # 计算路径长度
                path_length = len(as_path.split())

                # 计算时间区间
                time_interval = convert_to_time_interval(timestamp)

                # 更新路径长度数据
                if time_interval not in path_length_dict:
                    path_length_dict[time_interval] = []
                path_length_dict[time_interval].append(path_length)

    # 计算每个时间段的路径长度平均值
    time_intervals = sorted(path_length_dict.keys())
    avg_path_lengths = [np.mean(path_length_dict[t]) for t in time_intervals]

    # 计算路径长度变化率
    changes = []
    for i in range(1, len(avg_path_lengths)):
        prev_length = avg_path_lengths[i - 1]
        curr_length = avg_path_lengths[i]
        if prev_length > 0:
            changes.append(abs(curr_length - prev_length) / prev_length)
        else:
            changes.append(0)

    # 找到显著变化的时间段
    significant_changes = [time_intervals[i] for i, change in enumerate(changes) if change > threshold]

    # 绘制图形
    plt.figure(figsize=(12, 8))
    plt.plot(time_intervals, avg_path_lengths, marker='o', label='Average AS Path Length')

    # 标记显著变化的时间点
    for t in significant_changes:
        plt.axvline(t, color='red', linestyle='--', alpha=0.7, label=f'Significant Change @ {timestamp_to_time(t)}')

    # 设置x轴为时分秒格式
    time_labels = [timestamp_to_time(t) for t in time_intervals]
    plt.xticks(time_intervals, time_labels, rotation=45, fontsize=8)

    plt.xlabel('Time (60 minutes intervals)')
    plt.ylabel('Average AS Path Length')
    plt.title(f'AS Path Length Changes (Threshold: {threshold})')
    plt.legend(loc='upper left')
    plt.tight_layout()

    # 保存图片到指定位置
    plt.savefig(save_path)
    plt.close()  # 关闭图形，避免内存泄漏
    print("Finished!!!")


# 示例用法
folder_path = '/home/skypapaya/code/BGP-Security/code/bgp-analyze/txt/route-views.amsix/20211004'  # 数据文件夹路径
threshold = 0.2  # 设定路径长度变化率阈值
save_path = '/home/skypapaya/code/BGP-Security/code/bgp-analyze/output_picture/path_length_changes/path_length_changes_20211004.png'  # 保存图形的路径

plot_as_path_length_changes(folder_path, threshold, save_path)
