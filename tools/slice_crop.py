# -*- coding: utf-8 -*-
"""用 ffmpeg crop 把整页长图切成带重叠的横条切片。

用法: python slice.py full.png out_dir [slice_h] [overlap]
"""
import os
import subprocess
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

src = sys.argv[1]
outdir = sys.argv[2]
slice_h = int(sys.argv[3]) if len(sys.argv) > 3 else 1600
overlap = int(sys.argv[4]) if len(sys.argv) > 4 else 100

FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")

os.makedirs(outdir, exist_ok=True)
w, h = Image.open(src).size
print(f"source: {w}x{h}")

step = slice_h - overlap
if step <= 0:
    raise SystemExit("overlap 必须小于 slice_h")

i = 0
y = 0
paths = []
while y < h:
    sh = min(slice_h, h - y)
    if sh < 40:  # 尾部太短就并入上一片
        break
    out = os.path.join(outdir, f"slice_{i:02d}_y{y}.png")
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", src,
         "-vf", f"crop={w}:{sh}:0:{y}", "-frames:v", "1", out],
        check=True,
    )
    paths.append(out)
    print(f"  {out}  y={y}..{y + sh}")
    i += 1
    if y + sh >= h:
        break
    y += step

print(f"total slices: {len(paths)}")
