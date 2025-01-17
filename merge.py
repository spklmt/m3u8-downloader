import os
import re

# 自然排序函数
def natural_key(string):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string)]

def merge_ts_files(input_dir, output_file):
    with open(output_file, 'wb') as merged:
        # 按自然排序读取 .ts 文件
        for file_name in sorted(os.listdir(input_dir), key=natural_key):
            if file_name.endswith('.ts'):
                file_path = os.path.join(input_dir, file_name)
                print(f"正在合并: {file_path}")
                with open(file_path, 'rb') as ts_file:
                    merged.write(ts_file.read())
    print(f"合并完成: {output_file}")

if __name__ == "__main__":
    # 输入文件夹路径
    input_dir = "ts_files"
    # 输出文件路径
    output_file = "merged.ts"
    # 合并 .ts 文件
    merge_ts_files(input_dir, output_file)
