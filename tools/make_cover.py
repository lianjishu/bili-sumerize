# -*- coding: utf-8 -*-
"""把任意尺寸的封面图压成适合内嵌 HTML 的小图（离线可用）。

用法:
  python make_cover.py <in.jpg> <out.jpg> [width] [quality]

默认 640px 宽 / q82，实测约 60KB，base64 后 ~80KB，可以放心内联。
"""
import sys

from PIL import Image

src = sys.argv[1]
dst = sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 640
Q = int(sys.argv[4]) if len(sys.argv) > 4 else 82

im = Image.open(src).convert("RGB")
w, h = im.size
if w > W:
    im = im.resize((W, round(h * W / w)), Image.LANCZOS)
im.save(dst, "JPEG", quality=Q, optimize=True, progressive=True)

import os
print(f"{src} {w}x{h} -> {dst} {im.size[0]}x{im.size[1]} {os.path.getsize(dst)} B")
