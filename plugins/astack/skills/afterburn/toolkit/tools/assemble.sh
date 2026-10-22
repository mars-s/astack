#!/bin/zsh
# Join rendered scenes in film order, add fine temporal grain over the whole cut, mux a soundtrack.
#   assemble.sh <film dir> "<scene order, e.g. A B D E>" <soundtrack.wav or -> <out.mp4> [grain, default 5]
# Scenes are <film dir>/frames/<scene>/f_####.png from lib.render(). Grain 0 turns it off; the style table in
# tactics.py suggests a value per style.
set -e
dir=$1; order=($=2); snd=$3; out=$4; grain=${5:-5}
list=$dir/out/frames.txt; mkdir -p $dir/out; : > $list
for s in $order; do for f in $dir/frames/$s/f_*.png; do echo "file '${f:A}'" >> $list; echo "duration 0.0333333" >> $list; done; done
n=$(grep -c '^file' $list); echo "frames: $n ($(( n / 30 )).$(( (n % 30) * 10 / 30 )) s)"
vf="fps=30,format=yuv420p"; [[ $grain != 0 ]] && vf="fps=30,noise=alls=${grain}:allf=t,format=yuv420p"
if [[ $snd == - ]]; then
  nice -n 19 ffmpeg -v error -y -f concat -safe 0 -i $list -vf $vf -c:v libx264 -preset slow -crf 15 -threads 2 -movflags +faststart $out
else
  nice -n 19 ffmpeg -v error -y -f concat -safe 0 -i $list -i $snd -vf $vf -c:v libx264 -preset slow -crf 15 -threads 2 \
    -c:a aac -b:a 256k -shortest -movflags +faststart $out
fi
ffprobe -v error -show_entries format=duration -of csv=p=0 $out
