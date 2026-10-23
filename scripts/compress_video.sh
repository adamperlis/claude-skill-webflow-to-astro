#!/usr/bin/env bash
# Re-encode a background video at the same size, frame rate and look, and
# say how close it is. Tries x264 CRF 26 and 28 (slow preset, no audio,
# faststart) and prints each file's size and SSIM against the original.
# Keep the smallest with SSIM >= 0.985; at that point the difference doesn't
# show in a muted loop. Needs ffmpeg and ffprobe (built with libx264).
#   compress_video.sh public/videos/hero.mp4 [out-dir]
set -e
src=$1; out=${2:-$(dirname "$src")}
[[ -f $src ]] || { echo "usage: $0 <video> [out-dir]"; exit 1; }
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,bit_rate -show_entries format=duration,size -of default=nw=1 "$src"
name=$(basename "$src")
for crf in 26 28; do
  dst=$out/${name%.*}-crf$crf.mp4
  ffmpeg -loglevel error -y -i "$src" -an -c:v libx264 -preset slow -crf $crf -profile:v high -pix_fmt yuv420p -movflags +faststart "$dst"
  ssim=$(ffmpeg -i "$dst" -i "$src" -lavfi "[0:v][1:v]ssim" -f null - 2>&1 | grep -o 'All:[0-9.]*' | tail -1)
  echo "crf $crf: $(( $(wc -c < "$dst") / 1024 / 1024 )) MiB, SSIM ${ssim#All:}  → $dst"
done
