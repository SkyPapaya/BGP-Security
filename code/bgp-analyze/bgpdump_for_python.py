import os
import subprocess
from tqdm import tqdm  # 需要安装 tqdm 库


def parse_bz2_files(input_folder, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有需要处理的 .bz2 文件
    bz2_files = [f for f in os.listdir(input_folder) if f.endswith('.bz2')]

    # 如果没有 .bz2 文件，提示用户
    if not bz2_files:
        print(f"No .bz2 files found in the folder {input_folder}.")
        return

    total_files = len(bz2_files)  # 总文件数

    # 使用 tqdm 显示进度条
    for filename in tqdm(bz2_files, desc="Processing files", total=total_files):
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename.replace('.bz2', '.txt'))

        # 使用 bgpdump 解析 .bz2 文件
        with open(output_file_path, 'w') as output_file:
            result = subprocess.run(['bgpdump', '-m', input_file_path], stdout=output_file, stderr=subprocess.PIPE)

            # 检查是否有错误输出
            if result.returncode != 0:
                print(f"Error processing {filename}: {result.stderr.decode()}")
            else:
                # 进度条会自动更新
                pass  # 没有错误则不做额外的操作

    print("All files processed.")


if __name__ == "__main__":
    input_folder = "/home/skypapaya/code/BGP/code/data/update-source"  # 替换为你的 .bz2 文件所在的文件夹路径
    output_folder = "/home/skypapaya/code/BGP/code/data/output/update_table"  # 替换为解析结果输出文件夹路径
    parse_bz2_files(input_folder, output_folder)
