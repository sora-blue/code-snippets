#!/bin/bash
set -ex

# 判断是否输入了文件路径参数
if [ -z "$1" ]; then
  echo "请提供一个音视频文件路径作为参数"
  exit 1
fi

# 获取文件名和文件后缀
dirpath=$(dirname "$1")
filename=$(basename -- "$1")
extension="${filename##*.}"
basefilename=$(basename -- "$filename" ".$extension")
sepfile=separated/htdemucs/"$basefilename"/vocals.wav
 
# 判断文件后缀是否为音视频格式
if [ "$extension" != "mp4" ] && [ "$extension" != "mkv" ] && [ "$extension" != "avi" ] && [ "$extension" != "mov" ]; then
  echo "不支持的文件格式"
  exit 1
fi

cd "$dirpath"

if [ ! -f "$sepfile" ]; then
  # 转换为 MP3 格式
  ffmpeg -i "$filename" -f mp3 -acodec libmp3lame -y "$basefilename".mp3
  
  # 处理 MP3 文件
  demucs --two-stems=vocals "$basefilename".mp3 
fi

# 替换音轨
ffmpeg -i "$filename" -i "$sepfile"  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k "$basefilename"_converted.mp4

cd -
