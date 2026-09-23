# -*- coding: utf-8 -*-
"""为每个配色变体生成样张：横幅+首屏 与 一个含 SVG/各类块的正文区，纵向拼接。

用法: python theme_preview.py <theme_dir> <out_dir>
"""
import os
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

TDIR = os.path.abspath(sys.argv[1])
OUTDIR = os.path.abspath(sys.argv[2])
W = 1440
os.makedirs(OUTDIR, exist_ok=True)

variants = sorted(f for f in os.listdir(TDIR)
                  if f.startswith("theme_") and f.endswith(".html"))
print("variants:", variants)

items = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True,
                          args=["--hide-scrollbars", "--force-device-scale-factor=1",
                                "--disable-lcd-text", "--font-render-hinting=none"])
    pg = b.new_page(viewport={"width": W, "height": 1000}, device_scale_factor=1)
    for f in variants:
        path = os.path.join(TDIR, f)
        from pathlib import Path
        pg.goto(Path(path).resolve().as_uri(), wait_until="load", timeout=60000)
        pg.wait_for_timeout(1800)
        pg.evaluate("() => document.fonts && document.fonts.ready")
        pg.wait_for_timeout(300)
        h = pg.evaluate("() => document.documentElement.scrollHeight")
        # 正文取样区：1.4 小节起点（含 tslink / q / pit / figure+SVG / concl）
        y_body = pg.evaluate(
            "() => Math.round(document.querySelector('#s14').getBoundingClientRect().top"
            "  + window.scrollY)") - 24
        key = f[6]
        out = os.path.join(OUTDIR, f"preview_{key}.png")
        buf = pg.screenshot(full_page=True, clip={"x": 0, "y": 0, "width": W, "height": 1080})
        top = Image.open(__import__("io").BytesIO(buf)).convert("RGB")
        buf = pg.screenshot(full_page=True, clip={"x": 0, "y": y_body, "width": W, "height": 1180})
        body = Image.open(__import__("io").BytesIO(buf)).convert("RGB")
        sheet = Image.new("RGB", (W, top.size[1] + body.size[1] + 16), (128, 128, 128))
        sheet.paste(top, (0, 0))
        sheet.paste(body, (0, top.size[1] + 16))
        sheet.save(out)
        print(f"  {key}: h={h} s14_y={y_body} -> {out} {sheet.size}", flush=True)
        items.append((key, out))
    b.close()

# 2x2 首屏拼版，供快速比对
top_imgs = [(k, Image.open(o).crop((0, 0, W, 1080))) for k, o in items]
cw, ch = 720, 540
sheet = Image.new("RGB", (cw * 2, ch * 2), (60, 60, 60))
for i, (k, im) in enumerate(top_imgs):
    sheet.paste(im.resize((cw, ch), Image.LANCZOS), ((i % 2) * cw, (i // 2) * ch))
cs = os.path.join(OUTDIR, "_contact.png")
sheet.save(cs)
print("contact sheet ->", cs, sheet.size)
