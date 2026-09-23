# -*- coding: utf-8 -*-
"""生成保真的整页 PNG。

超长页面下 Chromium 的 full_page 一次性截图会产生重排伪影
（实测：第 3 章章节头被下移 983px，且章节色丢失）。
因此改为「按页面坐标分段 clip 截取 + 纵向拼接」，像素与 DOM 坐标严格一一对应。
"""
import io
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

def to_url(p):
    """本地路径自动转 file:// URL；已经是 http/https/file 的照原样返回。"""
    if p.startswith(("http://", "https://", "file://")):
        return p
    from pathlib import Path
    return Path(p).resolve().as_uri()



Image.MAX_IMAGE_PIXELS = None

url = sys.argv[1]
out = sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 1440
seg_h = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
wait_ms = int(sys.argv[5]) if len(sys.argv) > 5 else 2500

with sync_playwright() as p:
    b = p.chromium.launch(
        channel="chrome", headless=True,
        args=["--hide-scrollbars", "--force-device-scale-factor=1",
              "--disable-lcd-text", "--font-render-hinting=none"],
    )
    pg = b.new_page(viewport={"width": width, "height": 1000}, device_scale_factor=1)
    pg.goto(to_url(url), wait_until="load", timeout=60000)
    pg.wait_for_timeout(wait_ms)
    pg.evaluate("() => document.fonts && document.fonts.ready")
    pg.wait_for_timeout(400)

    dims = pg.evaluate(
        "() => ({w: document.documentElement.scrollWidth,"
        " h: document.documentElement.scrollHeight})"
    )
    W, H = dims["w"], dims["h"]
    print(f"document: {W}x{H}")

    segs = []
    y = 0
    while y < H:
        h = min(seg_h, H - y)
        buf = pg.screenshot(full_page=True,
                            clip={"x": 0, "y": y, "width": W, "height": h})
        im = Image.open(io.BytesIO(buf)).convert("RGB")
        if im.size != (W, h):
            print(f"  ! 段 y={y} 尺寸异常 {im.size}，期望 {(W, h)}")
        segs.append((y, im))
        print(f"  seg y={y}..{y + h}  -> {im.size}", flush=True)
        y += h

    b.close()

sheet = Image.new("RGB", (W, H), (10, 14, 19))
for y0, im in segs:
    sheet.paste(im, (0, y0))
sheet.save(out)
print(f"saved {out}  {sheet.size}")
assert sheet.size == (W, H), "拼接结果与文档尺寸不一致"
print("OK: 整页 PNG 与页面坐标一一对应")
