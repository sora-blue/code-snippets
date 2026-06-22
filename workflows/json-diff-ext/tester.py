import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
import argparse
import os
import shutil
import multiprocessing as mp
from tqdm import tqdm
import logging
import time

def process_item(item, standard_prefix, test_prefix, output, temp_dir, progress_counter, pbar):
    url_suffix = item['url_suffix']
    case_name = item['case_name']
    standard_url = standard_prefix + url_suffix
    test_url = test_prefix + url_suffix

    standard_output_file = os.path.join(temp_dir, f'standard_output_{case_name}.json')
    test_output_file = os.path.join(temp_dir, f'test_output_{case_name}.json')

    # 调用标准接口并保存结果到文件
    subprocess.run(['curl', '-s', '-o', standard_output_file, standard_url])

    # 调用测试接口并保存结果到文件
    subprocess.run(['curl', '-s', '-o', test_output_file, test_url])

    # 将结果保存到输出数组
    output.append((case_name, standard_output_file, test_output_file))

    # 更新进度计数器
    with progress_counter.get_lock():
        progress_counter.value += 1
        progress = progress_counter.value
        # 打印进度
        pbar.update(1)
        # print(f'Progress: {progress}/{total}', end='\n', flush=True)

def main(args):
    with open(args.input_file, 'r') as f:
        data = json.load(f)

    standard_prefix = data['standard_prefix']
    test_prefix = data['test_prefix']
    items = data['items']

    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)

    output = []

    # 创建进度计数器
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("fetching...")
    progress_counter = mp.Value('i', 0)
    pbar = tqdm(total=len(items))

    
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = []
        for item in items:
            futures.append(executor.submit(process_item, item, standard_prefix, test_prefix, output, temp_dir, progress_counter, pbar))
        
        # 等待所有任务完成
        for future in futures:
            future.result()
    
    time.sleep(1)
    logging.debug("outputing...")

    # 将输出写入文件
    with open(args.output_file, 'w') as f:
        output_bar = tqdm(total=len(output))
        for idx, (case_name, standard_output_file, test_output_file) in enumerate(output):
            if not os.path.isfile(standard_output_file) or not os.path.isfile(test_output_file):
                raise ValueError(f"file of case {case_name} is missing!")
            diff_output = subprocess.run(['json-diff', standard_output_file, test_output_file], capture_output=True, text=True)
            f.write(f'--- {idx+1}/{len(output)}. diff of {case_name} ---\n')
            f.write(diff_output.stdout)
            f.write('\n')
            output_bar.update(1)

    # 清除临时文件夹
    if not args.savetemp:
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = "This script is to diff json from two urls. <br/> Note: you should install json-diff before running it."
    parser.add_argument('input_file', help='input JSON file')
    parser.add_argument('output_file', help='output file')
    parser.add_argument('-c', '--concurrency', type=int, default=4, help='concurrency level')
    parser.add_argument('--savetemp', help="save temp dir or not", action="store_true")
    args = parser.parse_args()

    main(args)
