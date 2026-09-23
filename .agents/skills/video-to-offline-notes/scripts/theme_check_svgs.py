# -*- coding: utf-8 -*-
"""把若干个 figure 区域拼成一张检查图，用于快速核对配色下的 SVG 可读性。

用法: python theme_check_svgs.py <html> <out.png> [scale]
"""
import io
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

html = Path(os.path.abspath(sys.argv[1])).resolve().as_uri()
out = os.path.abspath(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 6
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.62
W = 1440

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True,
                          args=["--hide-scrollbars", "--force-device-scale-factor=1",
                                "--disable-lcd-text", "--font-render-hinting=none"])
    pg = b.new_page(viewport={"width": W, "height": 1000}, device_scale_factor=1)
    pg.goto(html, wait_until="load", timeout=60000)
    pg.wait_for_timeout(2000)
    total = pg.evaluate("() => document.querySelectorAll('figure').length")
    step = max(1, total // N)
    idx = list(range(0, total, step))[:N]
    boxes = pg.evaluate(
        "(idx) => idx.map(i => { const f = document.querySelectorAll('figure')[i];"
        " const r = f.getBoundingClientRect();"
        " return {y: Math.round(r.top + window.scrollY), h: Math.round(r.height),"
        " label: (f.querySelector('svg')?.getAttribute('aria-label')||'').slice(0,26)}; })", idx)
    tiles = []
    for bx in boxes:
        h = min(bx["h"], 860)
        buf = pg.screenshot(full_page=True,
                            clip={"x": 0, "y": bx["y"], "width": W, "height": h})
        im = Image.open(io.BytesIO(buf)).convert("RGB")
        tiles.append((bx, im.resize((int(W * scale), int(im.size[1] * scale)), Image.LANCZOS)))
    b.close()

LAB, GAP, COLS = 28, 12, 2
cw = tiles[0][1].size[0]
col_h = [0] * COLS
for i, (_, im) in enumerate(tiles):
    c = i % COLS
    col_h[c] += im.size[1] + LAB + GAP
H = max(col_h) + GAP
sheet = Image.new("RGB", (cw * COLS + GAP * (COLS + 1), H), (120, 120, 120))
d = ImageDraw.Draw(sheet)
ycur = [GAP] * COLS
for i, (bx, im) in enumerate(tiles):
    c = i % COLS
    x = GAP + c * (cw + GAP)
    y = ycur[c]
    d.rectangle([x, y, x + cw, y + LAB - 3], fill=(62, 62, 62))
    d.text((x + 8, y + 7), f"{bx['label']}   h={bx['h']}", fill=(235, 235, 235))
    sheet.paste(im, (x, y + LAB))
    ycur[c] = y + LAB + im.size[1] + GAP

sheet.save(out)
print(f"-> {out} {sheet.size}  取样 {len(tiles)}/{total} 张")
for bx in boxes:
    print(f"   {bx['label']:28} y={bx['y']:6} h={bx['h']}")
