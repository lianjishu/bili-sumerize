# -*- coding: utf-8 -*-
"""SVG 守卫：静态拦截“HTML 闯出标签”，并可选与浏览器 DOM 比对 <text> 数量。

用法:
  python svg_guard.py page.html                # 静态检查
  python svg_guard.py page.html --dump counts.json  # 另存每张图的 <text> 数量
"""
import json
import re
import sys

# HTML 解析器在 <svg> 内遇到这些标签会强制弹出 SVG 命名空间，
# 导致该标签之后的整个 SVG 被丢弃、文字泄漏到图外。
BREAKOUT = (
    "b|big|blockquote|body|br|center|code|dd|div|dl|dt|em|embed|h1|h2|h3|h4|h5|h6|"
    "head|hr|i|img|li|listing|menu|meta|nobr|ol|p|pre|ruby|s|small|span|strike|"
    "strong|sub|sup|table|tt|u|ul|var|font|form|input|iframe|object|select|textarea|button"
)

path = sys.argv[1]
html = open(path, encoding="utf-8").read()
svgs = re.findall(r"<svg\b.*?</svg>", html, re.S)

bad = []
for i, s in enumerate(svgs):
    m = re.search(r'aria-label="([^"]*)"', s)
    label = m.group(1) if m else f"svg#{i}"
    for mm in re.finditer(rf"<({BREAKOUT})\b", s):
        bad.append((i, label, mm.group(1)))

text_counts = [len(re.findall(r"<text\b", s)) for s in svgs]
figs = len(re.findall(r"<figure>", html))

print(f"文件: {path}")
print(f"<svg> 数量: {len(svgs)}   <figure> 数量: {figs}")
if bad:
    print(f"✗ SVG 内出现 HTML 闯出标签 {len(bad)} 处：")
    for i, label, tag in bad:
        print(f"    svg#{i} [{label}] -> <{tag}>")
    print("  修法：换成 <tspan>（可带 font-family / fill 做行内强调）")
else:
    print("✓ SVG 内无 HTML 闯出标签")

if "--dump" in sys.argv:
    out = sys.argv[sys.argv.index("--dump") + 1]
    json.dump({"svg_count": len(svgs), "text_counts": text_counts},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"每图 <text> 数量已写入 {out}")
    print(f"  {text_counts}")

sys.exit(1 if bad else 0)
