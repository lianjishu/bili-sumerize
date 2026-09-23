# -*- coding: utf-8 -*-
"""跨集通用：把某集的模板 + 分章正文拼装成最终单页 HTML，并做结构回归检查。

用法:
  python build.py <work_dir> <out_html> [--theme KEY]

约定 <work_dir> 内含: template.html / ch1.html / ch2.html / ch3.html / cover.jpg
模板里用 __CHAPTERS__ 与 __COVER_B64__ 两个占位符。

--theme KEY 会用 tools/theme.py 里的配色方案（A 纸墨暖白 / B 极简冷白 /
C 莫兰迪灰调 / D 石墨夜）对整页换色；不指定则用源文件的原始配色。
"""
import base64
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(2)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
THEME = None
if "--theme" in sys.argv:
    THEME = sys.argv[sys.argv.index("--theme") + 1]
    args = [a for a in args if a != THEME]

WORK = os.path.abspath(args[0])
OUT = os.path.abspath(args[1])
NCH = int(os.environ.get("N_CHAPTERS", "3"))


def read(name):
    p = os.path.join(WORK, name)
    if not os.path.exists(p):
        sys.exit(f"缺少必需文件: {p}")
    return open(p, encoding="utf-8").read()


tpl = read("template.html")
chaps = [read(f"ch{i}.html") for i in range(1, NCH + 1)]
cover = base64.b64encode(open(os.path.join(WORK, "cover.jpg"), "rb").read()).decode()

if THEME:
    import theme as T
    if THEME not in T.SCHEMES:
        sys.exit(f"未知配色 {THEME}，可选: {list(T.SCHEMES)}")
    sc = T.SCHEMES[THEME]
    tpl, chaps = T.themed_parts(tpl, chaps, sc)
    print(f"配色: [{THEME}] {sc['name']}  {sc['desc']}")

html = tpl.replace("__CHAPTERS__", "\n".join(chaps)).replace(
    "__COVER_B64__", f"data:image/jpeg;base64,{cover}")
assert "__CHAPTERS__" not in html and "__COVER_B64__" not in html, "占位符未替换干净"
open(OUT, "w", encoding="utf-8").write(html)

# ---------- 体检 ----------
checks = {
    "文件字节": os.path.getsize(OUT),
    "svg 数量": len(re.findall(r"<svg ", html)),
    "figure 数量": len(re.findall(r"<figure>", html)),
    "figcaption 数量": len(re.findall(r"<figcaption>", html)),
    "小节数量": len(re.findall(r'class="sub" id=', html)),
    "时间戳链接": len(re.findall(r'class="tslink" href="([^"]+)"', html)),
    "块 q": len(re.findall(r'class="blk q"', html)),
    "块 pit": len(re.findall(r'class="blk pit"', html)),
    "块 steps": len(re.findall(r'class="blk steps"', html)),
    "块 concl": len(re.findall(r'class="blk concl"', html)),
    "块 eye": len(re.findall(r'class="blk eye"', html)),
    "blockquote": len(re.findall(r"<blockquote>", html)),
}
print(f"OUT: {OUT}")
for k, v in checks.items():
    print(f"  {k}: {v}")

# 外部资源引用（离线可用性）
ext = re.findall(r'(?:src|href)="(https?://[^"]+)"', html)
print(f"  外部 src/href 引用: {len(ext)} 条")
for u in sorted(set(re.sub(r"\?.*$", "", u) for u in ext)):
    print(f"    - {u}")

# ---------- 结构性回归检查 ----------
# HTML 解析器在 <svg> 里遇到 "breakout" 标签会强行退出 SVG 命名空间，
# 导致 SVG 后半段被吞掉、文字漏到图外。必须静态拦截。
BREAKOUT = (
    "b|big|blockquote|body|br|center|code|dd|div|dl|dt|em|embed|h1|h2|h3|h4|h5|h6|"
    "head|hr|i|img|li|listing|menu|meta|nobr|ol|p|pre|ruby|s|small|span|strike|"
    "strong|sub|sup|table|tt|u|ul|var|font|form|input|iframe|object|select|textarea|button"
)
svgs = re.findall(r"<svg\b.*?</svg>", html, re.S)
bad = []
for i, s in enumerate(svgs):
    label = (re.search(r'aria-label="([^"]*)"', s) or [None, f"svg#{i}"])[1]
    for m in re.finditer(rf"<({BREAKOUT})\b", s):
        bad.append((label, m.group(1)))
print(f"\n  SVG 数量（源码）: {len(svgs)}")
print(f"  {'✓ SVG 内无 HTML 闯出标签' if not bad else f'✗ SVG 内出现 HTML 闯出标签 {len(bad)} 处：{bad[:10]}'}")

text_counts = [len(re.findall(r"<text\b", s)) for s in svgs]
json.dump({"svg_count": len(svgs), "text_counts": text_counts, "breaks": bad,
           "file_size": os.path.getsize(OUT), "out": OUT},
          open(os.path.join(WORK, "build_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"  每图 <text> 数量: {text_counts}")

sys.exit(1 if bad else 0)
