# -*- coding: utf-8 -*-
"""对指定元素做局部截图，用于精确核对渲染。"""
import sys

from playwright.sync_api import sync_playwright

def to_url(p):
    """本地路径自动转 file:// URL；已经是 http/https/file 的照原样返回。"""
    if p.startswith(("http://", "https://", "file://")):
        return p
    from pathlib import Path
    return Path(p).resolve().as_uri()



url = sys.argv[1]
outdir = sys.argv[2]
selectors = sys.argv[3:]

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True,
                          args=["--hide-scrollbars", "--force-device-scale-factor=1"])
    pg = b.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
    pg.goto(to_url(url), wait_until="load", timeout=60000)
    pg.wait_for_timeout(2000)
    for i, sel in enumerate(selectors):
        el = pg.query_selector(sel)
        if el is None:
            print(f"  MISS {sel}")
            continue
        box = el.bounding_box()
        name = f"{outdir}/el_{i:02d}_{sel.strip('#.').replace(' ', '_').replace('>', '_')}.png"
        el.screenshot(path=name)
        print(f"  OK  {sel:26} y={box['y']:.0f} h={box['height']:.0f} -> {name}")
    b.close()
