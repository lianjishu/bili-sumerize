# -*- coding: utf-8 -*-
"""整页缩略总览 + 空白行扫描。"""
import glob
import os
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

src = sys.argv[1]
slicedir = sys.argv[2]
sheet_out = sys.argv[3]

# ---------- 1) 空白行扫描 ----------
im = Image.open(src).convert("RGB")
w, h = im.size
bg = im.getpixel((6, h - 6))
small = im.resize((60, max(1, h // 8)), Image.NEAREST)
sw, sh = small.size
px = small.load()


def is_bg(p):
    return all(abs(p[i] - bg[i]) < 7 for i in range(3))


blank_rows = [y for y in range(sh) if all(is_bg(px[x, y]) for x in range(sw))]
# 合并连续区间
runs = []
for y in blank_rows:
    if runs and y - runs[-1][1] <= 1:
        runs[-1][1] = y
    else:
        runs.append([y, y])
runs = [(a * 8, b * 8, (b - a) * 8) for a, b in runs if (b - a) * 8 >= 120]
print(f"source {w}x{h}  bg={bg}")
print(f"连续空白带（>=120px）：{len(runs)}")
for a, b, ln in runs:
    print(f"  y {a}..{b}  高 {ln}px")

# 检查每片是否过空
print("\n切片前景占比：")
for p in sorted(glob.glob(os.path.join(slicedir, "*.png"))):
    s = Image.open(p).convert("RGB")
    s = s.resize((90, max(1, s.size[1] // 24)), Image.NEAREST)
    pxl = s.load()
    tot = s.size[0] * s.size[1]
    ink = sum(0 if is_bg(pxl[x, y]) else 1 for y in range(s.size[1]) for x in range(s.size[0]))
    print(f"  {os.path.basename(p)}  前景 {ink / tot * 100:5.1f}%")

# ---------- 2) 缩略总览 ----------
slices = sorted(glob.glob(os.path.join(slicedir, "*.png")))
cols = 6
cell_w, cell_h = 238, 265
rows = (len(slices) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (10, 14, 19))
for i, p in enumerate(slices):
    s = Image.open(p).convert("RGB").resize((cell_w - 6, cell_h - 22), Image.LANCZOS)
    x = (i % cols) * cell_w + 3
    y = (i // cols) * cell_h + 3
    sheet.paste(s, (x, y))
sheet.save(sheet_out)
print(f"\ncontact sheet -> {sheet_out}  {sheet.size}")
