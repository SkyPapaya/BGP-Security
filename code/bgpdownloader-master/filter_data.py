import os
import glob


def extract_and_filter_files(directory, pattern, output_file):
    """
    遍历指定文件夹中的文件，筛选特定命名规则的文件，提取内容并输出到 txt 文件。

    :param directory: 文件夹路径
    :param pattern: 文件命名规则的通配符（例如 *.txt）
    :param output_file: 输出文件路径，用于保存筛选后的内容
    """
    # 使用 glob 模块获取符合条件的文件列表
    file_pattern = os.path.join(directory, pattern)
    matching_files = glob.glob(file_pattern)

    with open(output_file, 'w') as out_file:
        # 遍历所有匹配的文件
        for file_path in matching_files:
            print(f"处理文件: {file_path}")

            # 读取并写入文件内容到输出文件
            with open(file_path, 'r') as in_file:
                content = in_file.read()
                # 将文件内容写入到输出文件
                out_file.write(f"内容来自文件: {file_path}\n")
                out_file.write(content)
                out_file.write("\n\n")  # 文件之间添加空行分隔

    print(f"筛选结果已保存到: {output_file}")


# 示例调用：假设你想筛选所有以 "bgp_data" 开头，扩展名为 ".txt" 的文件
directory_path = "/path/to/your/folder"  # 文件夹路径
pattern = "bgp_data*.txt"  # 匹配文件命名规则
output_file = "/home/skypapaya/code/BGP/code/data/output/filter_data"  # 输出文件路径

extract_and_filter_files(directory_path, pattern, output_file)
