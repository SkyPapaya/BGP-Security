import os
import matplotlib.pyplot as plt
from datetime import datetime


# 将时间戳转换为指定时间间隔（例如每小时）
def convert_to_time_interval(timestamp, interval=900):
    return int(timestamp // interval * interval)


# 将时间戳转化为时分秒格式
def timestamp_to_time(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


# 读取文件夹下的所有文件
def get_files_from_folder(folder_path):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]


# 统计每个时间段的更新数量总和，并绘制折线图
def plot_total_updates(folder_path, interval, save_path):
    time_updates = {}  # 用于记录每个时间段的更新总数

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

                # 将更新计入对应时间段
                time_interval = convert_to_time_interval(timestamp, interval)
                if time_interval not in time_updates:
                    time_updates[time_interval] = 0
                time_updates[time_interval] += 1

    # 将时间段数据排序
    sorted_intervals = sorted(time_updates.keys())
    counts = [time_updates[interval] for interval in sorted_intervals]

    # 转换时间戳为实际时间字符串
    time_labels = [timestamp_to_time(interval) for interval in sorted_intervals]

    # 绘制折线图
    plt.figure(figsize=(12, 8))
    plt.plot(time_labels, counts, marker='o', linestyle='-', color='skyblue', label='Total Updates')
    plt.xlabel('Time Intervals')
    plt.ylabel('Total Updates Count')
    plt.title(f'Total Updates Across All Data (Interval: {interval} seconds)')
    plt.xticks(rotation=45, fontsize=8)  # x 轴标签旋转以避免重叠
    plt.legend()

    # 保存图片到指定位置
    plt.tight_layout()  # 自动调整布局以防止标签被截断
    plt.savefig(save_path)
    plt.close()  # 关闭图形，避免内存泄漏
    print(f"Plot saved to {save_path}")


# 示例用法
folder_path = '/home/skypapaya/code/BGP-Security/code/bgp-analyze/txt/route-views.amsix/20211004'  # 数据文件夹路径
interval = 1800 # 时间间隔（单位：秒，1小时 = 3600秒）
save_path = '/home/skypapaya/code/BGP-Security/code/bgp-analyze/output_picture/hourly_updates_total/hourly_updates_20211004.png'  # 保存图形的路径

plot_total_updates(folder_path, interval, save_path)
