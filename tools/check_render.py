# -*- coding: utf-8 -*-
"""DOM 级渲染体检：文字重叠、超框、横向溢出、空白区块。"""
import json
import sys
from urllib.request import url2pathname

from playwright.sync_api import sync_playwright

def to_url(p):
    """本地路径自动转 file:// URL；已经是 http/https/file 的照原样返回。"""
    if p.startswith(("http://", "https://", "file://")):
        return p
    from pathlib import Path
    return Path(p).resolve().as_uri()



url = sys.argv[1]
width = int(sys.argv[2]) if len(sys.argv) > 2 else 1440

JS = r"""
() => {
  const rep = {page:{}, svgTextOverlaps:[], svgTextOutOfBox:[], hOverflow:[], emptyBlocks:[]};

  // 页面尺寸
  rep.page.scrollW = document.documentElement.scrollWidth;
  rep.page.scrollH = document.documentElement.scrollHeight;
  rep.page.viewportW = window.innerWidth;

  const inter = (a,b) => {
    const x = Math.min(a.right,b.right) - Math.max(a.left,b.left);
    const y = Math.min(a.bottom,b.bottom) - Math.max(a.top,b.top);
    return (x>0 && y>0) ? x*y : 0;
  };

  // 1) SVG 内文字互相重叠
  document.querySelectorAll('svg').forEach((svg, si) => {
    const label = (svg.getAttribute('aria-label')||'svg') + ' #' + si;
    const texts = [...svg.querySelectorAll('text')].map(t => ({
      t: (t.textContent||'').trim().slice(0,26),
      r: t.getBoundingClientRect()
    })).filter(o => o.r.width>0 && o.r.height>0);
    for (let i=0;i<texts.length;i++){
      for (let j=i+1;j<texts.length;j++){
        const a=texts[i], b=texts[j];
        // 跳过完全包含关系（同一锚点的换行文本不该算重叠）
        const ov = inter(a.r,b.r);
        if (ov > 8) {
          rep.svgTextOverlaps.push({svg:label, a:a.t, b:b.t, area:Math.round(ov)});
        }
      }
    }
    // 2) 文字超出 svg 画布
    const sb = svg.getBoundingClientRect();
    texts.forEach(o => {
      if (o.r.left < sb.left-1 || o.r.right > sb.right+1 ||
          o.r.top < sb.top-1 || o.r.bottom > sb.bottom+1) {
        rep.svgTextOutOfBox.push({svg:label, text:o.t,
          dx:Math.round(Math.min(o.r.left-sb.left, sb.right-o.r.right)),
          dy:Math.round(Math.min(o.r.top-sb.top, sb.bottom-o.r.bottom))});
      }
    });
  });

  // 3) 横向溢出
  document.querySelectorAll('body *').forEach(el=>{
    const r = el.getBoundingClientRect();
    if (r.width>0 && (r.right > window.innerWidth + 2 || r.left < -2)) {
      const tag = el.tagName.toLowerCase();
      if (tag==='svg' && r.right <= window.innerWidth+2) return;
      rep.hOverflow.push({tag, cls:(el.className||'').toString().slice(0,40),
        l:Math.round(r.left), r:Math.round(r.right)});
    }
  });
  // 去重
  const seen = new Set();
  rep.hOverflow = rep.hOverflow.filter(o=>{
    const k = o.tag+'|'+o.cls+'|'+o.l;
    if (seen.has(k)) return false; seen.add(k); return true;
  }).slice(0,25);

  // 4) 疑似空白块（figure 内容极矮）
  document.querySelectorAll('figure, .blk, .toc-card').forEach(el=>{
    const r = el.getBoundingClientRect();
    const txt = (el.textContent||'').trim();
    if (r.height > 0 && (r.height < 30 || (txt.length < 4 && el.tagName.toLowerCase()==='figure'))) {
      rep.emptyBlocks.push({tag:el.tagName.toLowerCase(), h:Math.round(r.height), chars:txt.length});
    }
  });

  // 5) 章节锚点 y 坐标（便于切片定位）
  rep.anchors = [...document.querySelectorAll('section[id], .sub[id]')].map(el=>({
    id: el.id, y: Math.round(el.getBoundingClientRect().top + window.scrollY)
  }));
  rep.figures = [...document.querySelectorAll('figure')].map((el,i)=>({
    i, y: Math.round(el.getBoundingClientRect().top + window.scrollY),
    h: Math.round(el.getBoundingClientRect().height),
    label: (el.querySelector('svg')?.getAttribute('aria-label')||'').slice(0,30)
  }));

  // 6) 每个 SVG 在浏览器里实际存在的 <text> 数量（与源码比对，可发现断图）
  rep.svgTextInDom = [...document.querySelectorAll('figure svg')].map((svg,i)=>({
    i,
    label: (svg.getAttribute('aria-label')||'').slice(0,30),
    texts: svg.querySelectorAll('text').length,
    // 该 figure 内、但不在 svg 里的裸文本（断图漏字的信号）
    strayText: [...svg.parentElement.querySelectorAll(':scope > *:not(svg):not(figcaption):not(caption)')]
      .map(e=>(e.textContent||'').trim()).filter(t=>t.length>12)
  }));
  return rep;
}
"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True,
                          args=["--hide-scrollbars", "--force-device-scale-factor=1"])
    pg = b.new_page(viewport={"width": width, "height": 1000}, device_scale_factor=1)
    pg.goto(to_url(url), wait_until="load", timeout=60000)
    pg.wait_for_timeout(2000)
    rep = pg.evaluate(JS)
    b.close()

print("== 页面 ==")
print(json.dumps(rep["page"], ensure_ascii=False))
print(f"\n== SVG 文字重叠 ({len(rep['svgTextOverlaps'])}) ==")
for o in rep["svgTextOverlaps"][:30]:
    print(f"  [{o['svg']}] '{o['a']}' ×  '{o['b']}'  area={o['area']}")
print(f"\n== SVG 文字超框 ({len(rep['svgTextOutOfBox'])}) ==")
for o in rep["svgTextOutOfBox"][:30]:
    print(f"  [{o['svg']}] '{o['text']}' dx={o['dx']} dy={o['dy']}")
print(f"\n== 横向溢出 ({len(rep['hOverflow'])}) ==")
for o in rep["hOverflow"][:25]:
    print(f"  <{o['tag']} class='{o['cls']}'> l={o['l']} r={o['r']}")
print(f"\n== 疑似空白块 ({len(rep['emptyBlocks'])}) ==")
for o in rep["emptyBlocks"][:20]:
    print(f"  {o}")

# ---------- 定位 build_report.json / render_report.json ----------
# 本集目录约定: <episode>/work/build_report.json + <episode>/screenshots/
from pathlib import Path

if url.startswith("file://"):
    html_dir = Path(url2pathname(url[7:])).parent
elif not url.startswith(("http://", "https://")):
    html_dir = Path(url).resolve().parent
else:
    html_dir = Path.cwd()

WORK_DIR = next((d for d in (html_dir / "work", html_dir.parent / "work", Path.cwd())
                 if (d / "build_report.json").exists()), html_dir)
REPORT_SRC = WORK_DIR / "build_report.json"
REPORT_OUT = (html_dir / "work") if (html_dir / "work").is_dir() else WORK_DIR

# ---------- 源码 vs DOM 的 <text> 数量比对（断图检测） ----------
print("\n== SVG 结构完整性（源码 <text> 数 vs 浏览器 DOM 实测） ==")
try:
    src = json.load(open(REPORT_SRC, encoding="utf-8"))
    exp = src["text_counts"]
    got = rep["svgTextInDom"]
    bad = 0
    if src.get("breaks"):
        print(f"  ✗ 源码含 HTML 闯出标签: {src['breaks'][:6]}")
        bad += 1
    for g in got:
        e = exp[g["i"]] if g["i"] < len(exp) else -1
        if e != g["texts"]:
            print(f"  ✗ 图 #{g['i']} [{g['label']}] 源码 {e} 个 <text>，DOM 只有 {g['texts']} 个 → 断图")
            bad += 1
        if g["strayText"]:
            print(f"  ✗ 图 #{g['i']} [{g['label']}] 图内出现裸文本（漏出 SVG）: {g['strayText'][:2]}")
            bad += 1
    print(f"  比对 {len(got)} 张图 → {'全部一致 ✓' if bad == 0 else f'{bad} 处异常'}")
except FileNotFoundError:
    print(f"  (未找到 {REPORT_SRC}，跳过；先跑 build.py 生成)")

REPORT_OUT.mkdir(parents=True, exist_ok=True)
json.dump(rep, open(REPORT_OUT / "render_report.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nfigures:", len(rep["figures"]), " anchors:", len(rep["anchors"]))
print(f"saved {REPORT_OUT / 'render_report.json'}")
