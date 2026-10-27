#!/bin/bash
# Full render in chunks (resumable: finished chunks are kept), picture only, then the soundtrack muxed in and
# loudness-normalised to -14 LUFS / -1.5 dBTP like render.sh. The 3D runs on software GL here (~5 s a frame),
# so a chunk at a time lets a stopped render pick up where it was. usage: ./render_chunks.sh <name> [chunk=300]
set -e; cd "$(dirname "$0")"; n=${1:-reel}; step=${2:-300}
B=${BROWSER:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}
npx tsc -p .
bu=out/.bundle; rm -rf $bu; npx remotion bundle src/index.ts --out-dir $bu --log=error >/dev/null
total=$(python3 -c "import json; w=json.load(open('src/words.json')); print(round((w[-1]['e'] + 1.2) * 30))")  # TOTAL in src/lib.ts
mkdir -p out/chunks/$n; : > out/chunks/$n/list.txt
for ((a=0; a<total; a+=step)); do
  b=$((a+step-1)); ((b>=total)) && b=$((total-1)); c=out/chunks/$n/$(printf %05d $a).mp4
  [ -s $c ] || npx remotion render $bu Film $c --frames=$a-$b --muted --codec h264 --crf 16 --concurrency=${CONCURRENCY:-2} --browser-executable=$B --gl=swangle --timeout=120000 --log=error
  echo "file '$(pwd)/$c'" >> out/chunks/$n/list.txt; echo "$(date +%H:%M) frames $a-$b done of $total"
done
ffmpeg -v error -y -f concat -safe 0 -i out/chunks/$n/list.txt -c copy out/$n.video.mp4
m=$(ffmpeg -hide_banner -nostats -i public/soundtrack.wav -af loudnorm=I=-14:TP=-2:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
v() { printf '%s' "$m" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i out/$n.video.mp4 -i public/soundtrack.wav -map 0:v -map 1:a -c:v copy -af "loudnorm=I=-14:TP=-2:LRA=11:measured_I=$(v input_i):measured_TP=$(v input_tp):measured_LRA=$(v input_lra):measured_thresh=$(v input_thresh):offset=$(v target_offset):linear=true,aresample=192000,alimiter=limit=0.75:attack=1:release=50:level=false,aresample=48000" -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart out/$n.mp4
echo out/$n.mp4
