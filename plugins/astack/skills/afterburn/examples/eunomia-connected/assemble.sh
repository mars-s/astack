#!/bin/zsh
# Join the rendered scenes in film order, add fine temporal grain over the whole cut, mux the soundtrack.
#   ./assemble.sh   (run from video/eunomia-connected/v2 after every scene has rendered and audio.mjs has run)
set -e
cd "${0:A:h}"
list=out/frames.txt; : > $list
for s in A B D E G H I; do
  for f in frames/$s/f_*.png; do echo "file '${PWD}/$f'" >> $list; echo "duration 0.0333333" >> $list; done
done
n=$(grep -c '^file' $list); echo "frames: $n ($(( n / 30 )).$(( (n % 30) * 10 / 30 )) s)"
nice -n 19 ffmpeg -v error -y -f concat -safe 0 -i $list -i out/eunomia-v2-soundtrack.wav \
  -vf "fps=30,noise=alls=5:allf=t,format=yuv420p" -c:v libx264 -preset slow -crf 15 -threads 2 \
  -c:a aac -b:a 256k -shortest -movflags +faststart out/eunomia-connected-v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 out/eunomia-connected-v2.mp4
