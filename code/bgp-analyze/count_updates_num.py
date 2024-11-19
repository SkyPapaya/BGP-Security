import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


# 将时间戳转换为指定格式（60分钟区间）
def convert_to_time_interval(timestamp, interval=1800):
    return int(timestamp // interval * interval)


# 将时间戳转化为时分秒格式
def timestamp_to_time(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')


# 读取文件夹下的所有文件
def get_files_from_folder(folder_path):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]


# 统计每个AS的更新数量
def plot_significant_changes_from_folder(folder_path, threshold, save_path):
    updates_dict = {}  # 用于存储每个 AS 在各时间段的更新数量

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
                prefix = parts[5]  # 目标prefix
                as_path = parts[6]  # AS路径

                # 只处理IPv4地址
                if '.' in prefix:
                    # 提取 AS 路径中的 AS 号
                    as_numbers = as_path.split()
                    for as_number in as_numbers:
                        if as_number not in updates_dict:
                            updates_dict[as_number] = []
                        updates_dict[as_number].append(timestamp)

    # 按时间段统计每个 AS 的更新数量
    time_intervals = sorted(
        set([convert_to_time_interval(ts) for timestamps in updates_dict.values() for ts in timestamps]))

    as_counts = {as_number: np.zeros(len(time_intervals)) for as_number in updates_dict}

    for as_number, timestamps in updates_dict.items():
        for timestamp in timestamps:
            time_interval = convert_to_time_interval(timestamp)
            if time_interval in time_intervals:
                idx = time_intervals.index(time_interval)
                as_counts[as_number][idx] += 1

    # 绘制显著变化的 AS 的折线图
    plt.figure(figsize=(12, 8))  # 增大图表尺寸

    for as_number, counts in as_counts.items():
        total_updates = sum(counts)
        if total_updates > 0:
            change_ratio = counts / total_updates
            # 如果某个时间段的更新数量占总更新数量的比例大于 threshold，则认为它发生了显著变化
            if any(change_ratio > threshold):  # 如果超过阈值，则绘制这个 AS 的变化图
                plt.plot(time_intervals, counts, label=f'AS {as_number}')

    # 将时间区间转换为实际的时分秒
    time_labels = [timestamp_to_time(t) for t in time_intervals]

    # 设置图形的 x 轴为实际的时分秒
    plt.xticks(time_intervals, time_labels, rotation=45, fontsize=8)  # 设置字体大小

    plt.xlabel('Time (15 minutes intervals)')
    plt.ylabel('Updates Count')
    plt.title(f'AS Updates with Significant Changes (Threshold: {threshold})')
    plt.legend().set_visible(False)

    # 手动调整边距
    plt.subplots_adjust(bottom=0.15, top=0.95)

    # 保存图片到指定位置
    plt.savefig(save_path)
    plt.close()  # 关闭图形，避免内存泄漏
    print("Finished!!!")


# 示例用法
folder_path = '/home/skypapaya/code/BGP-Security/code/bgp-analyze/txt/route-views.amsix/20211004'  # 数据文件夹路径
threshold = 0.6  # 设定阈值（可以输入小数）
save_path = '/home/skypapaya/code/BGP-Security/code/bgp-analyze/output_picture/updates/updates_20211004.png'  # 保存图形的路径

plot_significant_changes_from_folder(folder_path, threshold, save_path)
