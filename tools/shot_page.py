# -*- coding: utf-8 -*-
"""Chrome headless 整页截图（Playwright 复用本机 Chrome）。"""
import sys

from playwright.sync_api import sync_playwright

def to_url(p):
    """本地路径自动转 file:// URL；已经是 http/https/file 的照原样返回。"""
    if p.startswith(("http://", "https://", "file://")):
        return p
    from pathlib import Path
    return Path(p).resolve().as_uri()



url = sys.argv[1]
out = sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 1440
height = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
wait_ms = int(sys.argv[5]) if len(sys.argv) > 5 else 1800

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chrome",
        headless=True,
        args=["--hide-scrollbars", "--force-device-scale-factor=1",
              "--disable-lcd-text", "--font-render-hinting=none"],
    )
    page = browser.new_page(
        viewport={"width": width, "height": height},
        device_scale_factor=1,
    )
    page.goto(to_url(url), wait_until="load", timeout=60000)
    page.wait_for_timeout(wait_ms)
    try:
        page.evaluate("() => document.fonts && document.fonts.ready")
    except Exception:
        pass
    page.wait_for_timeout(400)
    dims = page.evaluate(
        "() => ({sw: document.documentElement.scrollWidth,"
        " sh: document.documentElement.scrollHeight,"
        " bw: document.body.scrollWidth,"
        " bh: document.body.scrollHeight})"
    )
    print("dims:", dims, flush=True)
    page.screenshot(path=out, full_page=True)
    print("saved:", out, flush=True)
    browser.close()
