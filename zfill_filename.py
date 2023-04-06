import os
import argparse
import re

'''
编写一个python脚本，接收一个输入参数作为源文件夹，把源文件夹下文件名匹配"[0-9]+\."的文件，文件名都补上前缀0，使数字前缀位数一致
请使用argparse解析输入参数，并把补零的位数也作为一个可选的参数
'''

# 创建参数解析器
parser = argparse.ArgumentParser(description='Add leading zeros to file names')
# 添加必选参数：源文件夹路径
parser.add_argument('src_dir', type=str, help='source directory path')
# 添加可选参数：补零的位数，默认为2
parser.add_argument('-z', '--zeroes', type=int, default=2, help='number of leading zeroes')

# 解析参数
args = parser.parse_args()

# 获取源文件夹路径
src_dir = args.src_dir

# 获取源文件夹下所有文件
files = os.listdir(src_dir)

# 遍历文件列表
for file in files:
    # 匹配文件名中的数字
    match = re.search(r'(\d+)\.', file)
    if match:
        # 获取数字
        num = match.group(1)
        # 计算数字位数
        num_len = len(num)
        # 计算需要补零的个数
        zeroes_needed = args.zeroes - num_len
        # 如果需要补零，就在数字前补上相应数量的0
        if zeroes_needed > 0:
            new_num = '0' * zeroes_needed + num
            # 构造新文件名
            new_file = file.replace(num + '.', new_num + '.')
            # 重命名文件
            os.rename(os.path.join(src_dir, file), os.path.join(src_dir, new_file))
