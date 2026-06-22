import random
import time

import requests
import asyncio
import bilibili_api.video
import os

from colorama import Fore, Back, Style

# Security the first.
# Is failure rate 53% an artificial number?


def fetchJson():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Referer": "https://www.bilibili.com",
        "Host": "api.bilibili.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
    }
    url = "https://api.bilibili.com/x/web-interface/archive/stat?aid=7"
    response = requests.get(url, headers)
    return response.text


def produceHeaders():
    with open("tmp.txt", "w") as file:
        while True:
            try:
                header, content = input().split('\t')
            except Exception:
                break
            print("\"%s\": \"%s\"," % (header, content), file=file)


record_fail = 0
total_ok = 0
total_not_ok = 0


async def fetchThroughPackage(aid, chooser: int = 0):
    global record_fail, total_ok, total_not_ok
    bDir = "data_without_tags"
    if not os.path.isdir(bDir):
        os.mkdir(bDir)
    filePath1 = "%s/api_info_%d.json" % (bDir, aid)
    filePath2 = "%s/api_info_%d_tags.json" % (bDir, aid)
    if chooser and os.path.isfile(filePath1) and os.path.isfile(filePath2):
        print("File already exists. [%s, %s]" % (filePath1, filePath2))
        return
    with open("%s/api_info_%d.json" % (bDir, aid), "w") as output:
        try:
            vid = bilibili_api.video.Video(aid=aid)
            try:
                s3 = await vid.get_tags()
                f2 = open(filePath2, "w")
                print(s3, file=f2)
                f2.close()
                print(Fore.GREEN, "* TAG fetch succeeded.")
            except Exception:
                print(Fore.RED, "* \tTAG fetch failed")
                pass
            s2 = await vid.get_info()
            print(s2, file=output)
            print(Fore.GREEN, "Success [av %d]" % aid)
            record_fail = 0
            total_ok += 1

        except Exception:
            print(Fore.RED, "\tFailure [av %d]" % aid)
            print("{}", file=output)
            record_fail += 1
            total_not_ok += 1
    print(Fore.WHITE)

# from 14200: sequential failure
# before 21221: no tags got
# 250, 0000 -> one packet(10 GB)
# expected 386 * 2 GB in total
# from 43500 speed up, seq double failure, [banned from video api, <0.1s, suggested about 0.5s]

# banned yet another time with aver 0.5s per entry at 248189
# to tell the truth, fetch one by one is too silly
# but fine for lazy guys like me just hate to bother splitting it into random ops
# todo: record the two ends of sequential failure

# believable data : from 1 to 248189


def fetcher(limit_time=600, interval=0.4, sequential_limit=300):
    global total_ok, total_not_ok, record_fail
    record_fail = 0
    config_file_name = "config.txt"
    index = 1
    limit = int(limit_time / interval)
    print("--------------limit %d--------------" % limit)
    rand = random.Random()
    if os.path.isfile(config_file_name):
        with open(config_file_name, "r") as config:
            index = int(config.readline())
            print("read config: %d" % index)
    for new_index in range(index, index + limit):
        print("---------------------------------")
        if record_fail > sequential_limit:
            print("sequential failure detected, stop running")
            with open(config_file_name, "w") as config:
                print("%d" % (new_index - record_fail), file=config)
            return 1
            break
        if new_index > 1e8:
            print("Avid stopped here at 1,0000,0000.")
            break
        asyncio.get_event_loop().run_until_complete(fetchThroughPackage(new_index))
        with open(config_file_name, "w") as config:
            print("%d" % (new_index + 1), file=config)
        tmp = interval + 0.05 * rand.randrange(1, 9)
        print("wait %f s, success: %d, failure: %d, sequential_failure: %d" % (tmp, total_ok, total_not_ok, record_fail))
        time.sleep(tmp)
    print("--------------Mission finished--------------")
    print("success: %d, failure: %d, total: %d" % (total_ok, total_not_ok, total_ok+total_not_ok))
    return 0


async def test():
    await fetchThroughPackage(7)
    pass


if __name__ == '__main__':
    while True:
        val = fetcher()
        if val == 1 :
            break
        print("------- wait until next phase -------")
        time.sleep(60 * 3)
    pass
