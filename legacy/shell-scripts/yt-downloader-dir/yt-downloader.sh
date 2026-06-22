# set -ex
url=$1
is_diy="y"
is_convert="n"
tmp_file=$(echo $url | sed 's/.*v=\(.*\)/\1/') 
tmp_file="downloader-$tmp_file.tmp" # MODIFY THIS LATER TO SUPPORT MULTI-THREAD
echo "A script to download ytb videos with ytdlp fork (see https://github.com/yt-dlp/yt-dlp)."

# -- download format info
echo "- Video url: $url"
echo "- Checking supported formats..."
# * try to save multi-line var as the same is a waste of time
# * supported_formats=$(ytdlp -F "$url") # | awk 'NR==1{sub(/^[\r\n]+/, "");print;next} 1') # gpt # do not add space bwt var definition
ytdlp -F "$url" > $tmp_file

# -- choose video stream
video_line="$(cat $tmp_file | grep "video only" | tail -n 1)"
default_video_id=$(echo $video_line | sed 's/ .*//')

if [ "$is_diy" = "y" ]; then
    cat $tmp_file | grep "video only"
    echo "- Choosed video id (default $default_video_id): "
    read video_id
else
    echo "- Choose video id: skipped, use default"
fi
if [ -z "$video_id" ]; then
    video_id=$default_video_id
fi
video_line=$(cat $tmp_file | grep "video only" | grep $video_id)

# -- choose audio stream
audio_line="$(cat $tmp_file | grep "audio only" | tail -n 1)"
default_audio_id=$(echo $audio_line | sed 's/ .*//')

if [ "$is_diy" = "y" ]; then
    cat $tmp_file | grep "audio only"
    echo "- Choosed audio id (default $default_audio_id): "
    read audio_id
else
    echo "- Choose audio id: skipped, use default"
fi
if [ -z "$audio_id" ]; then
    audio_id=$default_audio_id
fi
audio_line=$(cat $tmp_file | grep "audio only" | grep $audio_id)

echo -e "\n"
echo "- Choosed audio format: $audio_line"
echo "- Choosed video format: $video_line"

# -- download
# [download] 1 2.webm has already been downloaded
# [download] Destination:  1 2.webm 
echo "- Downloading audio file $audio_id ..."
audio_file_name=$(ytdlp -f $audio_id "$url" | grep "\[download\]" | tee /dev/tty | head -n 1 | sed "s/\[download\] \(Destination: \)*\(.*\.\([^ ]*\)\).*/\2/")
echo "- audio file: $audio_file_name"

video_file_basename="${audio_file_name%.*} [video]"
video_file_name="$video_file_basename.mp4"

echo "- Downloading video file $video_id..."
# * do not use this name, 'cause audio & video might both have the same extension name
old_video_file_name=$(ytdlp -f $video_id "$url" -o "$video_file_name" | tee /dev/tty | grep "\[download\]" | head -n 1 | sed "s/\[download\] \(Destination: \)*\(.*\.\([^ ]*\)\).*/\2/")
echo "- video file: $video_file_name"

# * following commands not tested
# -- merge
echo "- Merging video stream & audio stream ..."
echo "- * Note that it is super slow with CPU, and if it is <= 4k resolution, you can modify this command to enable GPU acceleration."
new_video_file_name="$video_file_basename [merged].mp4"
ffmpeg -i "$video_file_name" -i "$audio_file_name" -c:v copy -c:a aac -strict experimental "$new_video_file_name"
# -- convert
if [ "$is_convert" = "y" ]; then
    echo "- Converting video into h264 format..."
    converted_video_file_name="$video_file_basename [merged] [h264].mp4"
    ffmpeg -i $new_video_file_name $converted_video_file_name
else
    echo "- Convert: skipped"
fi
