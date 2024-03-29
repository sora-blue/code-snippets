```
请编写一个python脚本，按行接收如下输入。输入有三种情况：
1. 全是空白字符：直接丢弃
2. 含有not found：直接丢弃
3. 否则，分割成标题和链接两个字符串，用标题匹配$rtitle，用链接匹配$rurl，用标题的第一个字符匹配$ricon，从#000000到#FFFFFF中随机选择一个颜色匹配$rcolor，输出如下格式的文本：
'<outline type="rss" text="$rtitle" title="$rtitle" xmlUrl="$rurl" desc="$rtitle" icon="$ricon" iconType="2" color="$rcolor"/>'

示例输入：
```
南华早报		https://rsshub.rssforever.com/scmp/3
韩国中央日报	not found
```

示例输出：
```
<outline type="rss" text="南华早报" title="南华早报" xmlUrl="https://rsshub.rssforever.com/scmp/3" desc="南华早报" icon="南" iconType="2" color="#FF0000"/>
```
```
import re
import random
import argparse
import xml.sax.saxutils

parser = argparse.ArgumentParser(description="Generate OPML from RSS URLs")
parser.add_argument('--in', dest='input_path', required=True, help='input file path')
parser.add_argument('--out', dest='output_path', required=True, help='output file path')
parser.add_argument("-l", "--length", type=int, default=5, help="length of icon text")
args = parser.parse_args()

with open(args.input_path, "r", encoding="utf-8") as f_in, \
        open(args.output_path, "w", encoding="utf-8") as f_out:
    f_out.write('<?xml version="1.0" encoding="UTF-8"?><opml version="1.0"><head><title>rolly rss export</title></head><body>\n')
    for line in f_in:
        line = line.strip()
        if not line or "not found" in line:
            continue
        # 使用正则表达式匹配标题和链接
        match = re.match(r'(.+)\s+(https?://\S+)', line)
        if match:
            title, url = match.group(1), match.group(2)
            title = xml.sax.saxutils.escape(title.strip())
            url = xml.sax.saxutils.escape(url.strip())
            icon = title.split()[0][:args.length]  # 添加这一行，将 icon 设为标题的第一个单词的前 length 个字符
        else:
            continue
        color = "#" + "%06x" % random.randint(0, 0xFFFFFF)
        f_out.write(f'<outline type="rss" text="{title}" title="{title}" xmlUrl="{url}" desc="{title}" icon="{icon}" iconType="2" color="{color}"/>\n')
    f_out.write('</body></opml>\n')
