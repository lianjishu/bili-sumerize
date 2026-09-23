# -*- coding: utf-8 -*-
"""主题引擎：把一套配色应用到「模板 + 分章正文」，生成变体单页 HTML。

配色不是直接改每个颜色，而是走 role 映射：
  结构色 12 个（底色/面板/描边/文字）
  + 6 个强调色槽位 A1..A6（原页面分别是 青/紫/琥珀/红/绿/蓝）
  + 2 个版式开关（hero 光晕、块底渐变）
原页面里所有 rgba() 都是强调色的 alpha 变体，按 rgb 反查槽位后替换，保留 alpha。

用法:
  python theme.py <work_dir> <out_dir> [scheme_key ...]
"""
import base64
import os
import re
import sys

WORK = None      # 由 __main__ 设置；作为库导入时不解析 argv
OUTDIR = None
NCH = int(os.environ.get("N_CHAPTERS", "3"))

# ---------------------------------------------------------------- 配色方案
SCHEMES = {
    "A": {
        "name": "纸墨暖白",
        "desc": "暖白纸感 · 低饱和书卷色 · 平涂无渐变",
        "struct": {
            "bg": "#f6f2ea", "bg2": "#fffdf8", "panel": "#fffefb", "panel2": "#f1ece1",
            "node": "#f5f0e6", "line": "#e4dbc9", "line2": "#c9bda4", "trace": "#ece4d5",
            "tx": "#2b2721", "tx2": "#5c554a", "tx3": "#8f877a", "cover": "#e8e0d1",
        },
        "acc": {"A1": "#35707f", "A2": "#7c6096", "A3": "#ad7a29",
                "A4": "#b1514a", "A5": "#4f7a4e", "A6": "#3f6a94"},
        "glow": False, "grad": "flat",
    },
    "B": {
        "name": "极简冷白",
        "desc": "纯白文档感 · 蓝青主色系 · 三色语义 · 平涂 · 前景按 WCAG 4.5 压深",
        "struct": {
            "bg": "#ffffff", "bg2": "#fafbfc", "panel": "#f5f7f9", "panel2": "#eceff3",
            "node": "#f3f6f9", "line": "#e4e9ee", "line2": "#a9b5c2", "trace": "#eef2f6",
            "tx": "#1b2430", "tx2": "#56606d", "tx3": "#677181", "cover": "#e9edf1",
        },
        "acc": {"A1": "#2f6fb5", "A2": "#277c8d", "A3": "#946a17",
                "A4": "#c0483f", "A5": "#2b805c", "A6": "#4475a7"},
        "glow": False, "grad": "flat",
    },
    "C": {
        "name": "莫兰迪灰调",
        "desc": "低饱和高级灰 · 灰青灰紫灰金 · 平涂 · 前景按 WCAG 4.5 压深",
        "struct": {
            "bg": "#f1efeb", "bg2": "#f8f7f4", "panel": "#fbfaf7", "panel2": "#eceae3",
            "node": "#f3f1ec", "line": "#dcd7cc", "line2": "#a89f8f", "trace": "#e8e4da",
            "tx": "#2e2c27", "tx2": "#55504a", "tx3": "#706b62", "cover": "#e6e3db",
        },
        "acc": {"A1": "#5a757a", "A2": "#81697f", "A3": "#846d47",
                "A4": "#93655c", "A5": "#64755f", "A6": "#60718b"},
        "glow": False, "grad": "flat",
    },
    "D": {
        "name": "石墨夜",
        "desc": "中性石墨底 · 去掉霓虹与光晕 · 降饱和 · 平涂",
        "struct": {
            "bg": "#131417", "bg2": "#181a1e", "panel": "#1d2024", "panel2": "#23262b",
            "node": "#1f2227", "line": "#2b2f35", "line2": "#3c424a", "trace": "#24272c",
            "tx": "#e9eaec", "tx2": "#a7abb2", "tx3": "#767b84", "cover": "#0d0e10",
        },
        "acc": {"A1": "#5fa8bd", "A2": "#a08ec8", "A3": "#d3a445",
                "A4": "#cd6f68", "A5": "#72bd8f", "A6": "#6f9ed6"},
        "glow": False, "grad": "flat",
    },
}

# 原页面颜色 -> role。结构色
STRUCT_OLD = {
    "#0a0e13": "bg", "#0f151d": "bg2", "#141d28": "panel", "#18232f": "panel2",
    "#111a24": "node", "#1c2836": "trace", "#1d2a3a": "trace",
    "#233240": "line", "#31465c": "line2",
    "#e9eff7": "tx", "#adbccd": "tx2", "#77879a": "tx3",
    "#000": "cover", "#000000": "cover",
}
# 强调色槽位（原色 -> 槽位）
ACC_OLD = {
    "#46c6e0": "A1", "#a98bfa": "A2", "#f0b429": "A3",
    "#f8736e": "A4", "#3fd68c": "A5", "#5b9cf8": "A6",
}
ACC_RGB = {  # 用于反查 rgba()
    (70, 198, 224): "A1", (169, 139, 250): "A2", (240, 180, 41): "A3",
    (248, 115, 110): "A4", (63, 214, 140): "A5", (91, 156, 248): "A6",
}
STRUCT_RGB = {(0, 0, 0): "cover"}


def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def colorize(text, sc):
    """把一段 HTML/CSS 里的颜色按 scheme 映射。"""
    st, acc = sc["struct"], sc["acc"]

    def sub_hex(m):
        h = m.group(0).lower()
        hl = h if len(h) == 7 else "#" + "".join(c * 2 for c in h[1:])
        if hl in STRUCT_OLD:
            return st[STRUCT_OLD[hl]]
        if hl in ACC_OLD:
            return acc[ACC_OLD[hl]]
        return m.group(0)

    text = re.sub(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", sub_hex, text)

    def sub_rgba(m):
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        alpha = m.group(4)
        slot = ACC_RGB.get((r, g, b)) or STRUCT_RGB.get((r, g, b))
        if slot is None:
            return m.group(0)
        base = acc[slot] if slot.startswith("A") else st[slot]
        R, G, B = hex2rgb(base)
        return f"rgba({R},{G},{B},{alpha})"

    text = re.sub(
        r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)", sub_rgba, text)
    return text


def apply_layout(text, sc):
    """版式开关：hero 光晕、块底渐变。"""
    if not sc["glow"]:
        text = re.sub(
            r"\.hero\{padding:56px 0 34px;border-bottom:1px solid var\(--line\);background:\s*"
            r"radial-gradient\([^;]*?\),\s*radial-gradient\([^;]*?\)\}",
            ".hero{padding:56px 0 34px;border-bottom:1px solid var(--line);background:var(--bg)}",
            text, flags=re.S)
    if sc["grad"] == "flat":
        # linear-gradient(180deg, rgba(x,.07), rgba(x,.02)) -> rgba(x,.07)
        text = re.sub(
            r"linear-gradient\(180deg,\s*(rgba\([^)]*?,\s*\.?\d+\))\s*,\s*rgba\([^)]*?\)\)",
            r"\1", text)
    return text


def banner(sc, key):
    sw = "".join(
        f'<span style="display:inline-block;width:26px;height:26px;border-radius:5px;'
        f'background:{sc["acc"][s]};border:1px solid rgba(128,128,128,.35)"></span>'
        for s in ("A1", "A2", "A3", "A4", "A5", "A6"))
    st = sc["struct"]
    meta = " · ".join(f'{k} {st[k]}' for k in ("bg", "panel", "line", "tx"))
    return f'''
<div style="background:{st['panel2']};border-bottom:2px solid {sc['acc']['A1']};
     padding:14px 40px;display:flex;align-items:center;gap:18px;flex-wrap:wrap;
     font-family:'Segoe UI','Microsoft YaHei',sans-serif">
  <span style="font-size:15px;font-weight:700;color:{st['tx']}">配色方案 {key} · {sc['name']}</span>
  <span style="font-size:12.5px;color:{st['tx2']}">{sc["desc"]}</span>
  <span style="display:flex;gap:5px">{sw}</span>
  <span style="font-size:11.5px;color:{st['tx3']};font-family:Consolas,monospace">{meta}</span>
</div>
'''


def build(key, sc, work, outdir, with_banner=True):
    """对 work 目录生成一个变体 HTML。"""
    tpl = open(os.path.join(work, "template.html"), encoding="utf-8").read()
    chaps = [open(os.path.join(work, f"ch{i}.html"), encoding="utf-8").read()
             for i in range(1, NCH + 1)]
    cover = base64.b64encode(
        open(os.path.join(work, "cover.jpg"), "rb").read()).decode()

    tpl, chaps = themed_parts(tpl, chaps, sc)
    if with_banner:
        # 横幅用的是目标色，必须在 colorize 之后插入（否则会被再次映射）
        tpl = tpl.replace("<body>", "<body>" + banner(sc, key), 1)

    html = tpl.replace("__CHAPTERS__", "\n".join(chaps))
    html = html.replace("__COVER_B64__", f"data:image/jpeg;base64,{cover}")

    out = os.path.join(outdir, f"theme_{key}.html")
    os.makedirs(outdir, exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)

    # 残留检查：不应再有旧主题的颜色
    left = set()
    for m in re.finditer(r"#[0-9a-fA-F]{6}\b", html):
        h = m.group(0).lower()
        if h in STRUCT_OLD or h in ACC_OLD:
            left.add(h)
    print(f"  [{key}] {sc['name']:8} -> {os.path.basename(out)}  "
          f"{os.path.getsize(out)/1024:.0f}KB  "
          f"{'✓ 无残留旧色' if not left else f'✗ 残留 {sorted(left)}'}")
    return out


def themed_parts(tpl, chaps, sc):
    """把一个模板 + 若干分章正文整体换色（供 build.py 复用）。"""
    parts = [apply_layout(colorize(p, sc), sc) for p in [tpl, *chaps]]
    return parts[0], parts[1:]


def contrast(hex1, hex2):
    """WCAG 对比度。"""
    def lum(h):
        def ch(c):
            c /= 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = hex2rgb(h)
        return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)
    a, b = lum(hex1), lum(hex2)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def report_contrast(key):
    sc = SCHEMES[key]
    st = sc["struct"]
    print(f"\n[{key}] {sc['name']} 对比度（WCAG，正文建议 ≥4.5，次要文字 ≥3.0）")
    for fg in ("tx", "tx2", "tx3"):
        for bgk in ("bg", "bg2", "panel"):
            r = contrast(st[fg], st[bgk])
            flag = "✓" if (r >= 4.5 if fg == "tx" else r >= 3.0) else "⚠"
            print(f"  {fg:4} on {bgk:7} {r:5.2f}  {flag}")
    for s in ("A1", "A2", "A3", "A4", "A5", "A6"):
        r = contrast(sc["acc"][s], st["bg2"])
        print(f"  {s} {sc['acc'][s]} on bg2  {r:5.2f}  {'✓' if r >= 3 else '⚠'}")


if __name__ == "__main__":
    WORK = os.path.abspath(sys.argv[1])
    OUTDIR = os.path.abspath(sys.argv[2])
    keys = sys.argv[3:] or list(SCHEMES)
    print(f"work={WORK}\nout={OUTDIR}")
    for k in keys:
        build(k, SCHEMES[k], WORK, OUTDIR, with_banner=True)
        report_contrast(k)

