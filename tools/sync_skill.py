# -*- coding: utf-8 -*-
"""把技能沉淀到本项目 + 同步脚本镜像，避免多份副本各自漂移。

唯一事实来源（single source of truth）：
  - 脚本：<repo>/tools/*.py
  - 通用技能正文：~/.workbuddy/skills/<name>/SKILL.md

本脚本产出：
  1. 用户级技能 scripts/  <- tools/          （跨项目复用）
  2. 项目级技能 .agents/skills/<name>/       （跟着项目走）
       SKILL.md = 用户级 SKILL.md + 下方 PROJECT_ADDENDUM
       scripts/ <- tools/

用法: python tools/sync_skill.py [--check]
      --check 只比对是否一致，不写入（CI / 提交前自检用）
"""
import hashlib
import os
import shutil
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NAME = "video-to-offline-notes"
TOOLS = os.path.join(REPO, "tools")
USER_SKILL = os.path.expanduser(os.path.join("~", ".workbuddy", "skills", NAME))
PROJ_SKILL = os.path.join(REPO, ".agents", "skills", NAME)

# 本项目专用的维护脚本，不参与技能镜像（它不是可移植技能的一部分）
EXCLUDE = {"sync_skill.py"}


def skill_scripts():
    return sorted(f for f in os.listdir(TOOLS)
                  if f.endswith(".py") and not f.startswith("_") and f not in EXCLUDE)

PROJECT_ADDENDUM = """

---

# 附：本项目专属（BiliSumerize）

> 本节由 `tools/sync_skill.py` 自动追加，手改会被覆盖。

## 仓库结构

```
BiliSumerize/
├── AGENTS.md                 # agent 入口说明书
├── tools/                    # ★ 脚本唯一事实来源
├── bin/                      # ffmpeg + ffprobe
├── models/                   # faster-whisper-large-v3-turbo
├── bili_cookies.txt          # 跨系列复用
├── .agents/
│   ├── memory/               # 项目记忆（MEMORY.md = 长期约定）
│   └── skills/<name>/        # 本技能的项目级副本（自动生成）
└── jyy-generatice-se/        # jyy 系列
    ├── urllist.txt           # 集数索引：<编号>-<标题> [0X-Raw/...]: <URL>
    └── <编号>/               # 每集一目录，编号 = urllist.txt 行号
        ├── bili_summary_<BV号>.html
        ├── screenshots/       # full.png / _overview.png / slices/ / els/
        ├── _theme/            # 配色变体与样张（试色归档）
        └── work/              # 音频、转写、分章源文件、模板、校验报告
```

## 脚本同步规则

**改脚本只改 `tools/*.py`**，然后跑：

```bash
python tools/sync_skill.py            # 同步到两处技能副本
python tools/sync_skill.py --check    # 只检查是否漂移
```

技能里的 `scripts/` 是**镜像**，不要直接编辑。

## 每一集的完整命令序列

设 `E=<编号>`（如 `2`），工作目录 `jyy-generatice-se/`：

```bash
YT=/e/Projects/Repo/yt-dlp/release/yt-dlp_x86.exe
T=tools
FF=bin/ffmpeg.exe
P=C:/Users/ASUS/.workbuddy/binaries/python/envs/default/Scripts/python.exe

# 1 元数据 + 音频（首次先取 cookies：--cookies-from-browser firefox --cookies bili_cookies.txt）
$YT --cookies bili_cookies.txt --dump-single-json "<URL>" > $E/work/meta.json
$YT --cookies bili_cookies.txt -f 30280 -o "$E/work/audio_raw.%(ext)s" "<URL>"

# 2 转 mp3 + 时长校验（与 meta.json 的 duration 比，>5% 判异常）
$FF -y -i $E/work/audio_raw.m4a -vn -c:a libmp3lame -b:a 192k -ar 44100 -ac 2 $E/work/audio.mp3
bin/ffprobe.exe -v error -show_entries format=duration -of json $E/work/audio.mp3

# 3 转写（模型走本地目录，绕开 HF 下载）
WHISPER_MODEL=models/faster-whisper-large-v3-turbo \
WHISPER_DEVICE=cuda WHISPER_CTYPE=float16 \
  $P $T/transcribe_whisper.py $E/work/audio.mp3 $E/work/transcript.json

# 4 写 template.html + ch1..chN.html（用 yt-dlp 返回的 chapters 当骨架）

# 5 拼装（配色作为构建参数；本项目当前统一用 C 莫兰迪灰调）
$P $T/build.py $E/work $E/bili_summary_<BV>.html --theme C
$P $T/svg_guard.py $E/bili_summary_<BV>.html
$P $T/check_render.py $E/bili_summary_<BV>.html 1440

# 6 整页图 + 切片 + 总览
$P $T/shot_full.py $E/bili_summary_<BV>.html $E/screenshots/full.png 1440 4000
FFMPEG_BIN=$(pwd)/bin/ffmpeg.exe \
  $P $T/slice_crop.py $E/screenshots/full.png $E/screenshots/slices 1600 100
$P $T/scan_blank_sheet.py $E/screenshots/full.png $E/screenshots/slices $E/screenshots/_overview.png

# 7 换配色（可选）：出变体与样张，用户挑完再用 --theme 重跑第 5~6 步
$P $T/theme.py $E/work $E/_theme A B C D
$P $T/theme_preview.py $E/_theme $E/_theme/preview
$P $T/theme_check_svgs.py $E/_theme/theme_B.html $E/_theme/preview/_svgcheck_B.png 6
```

## 本项目已产生的成果

| 编号 | 标题 | BV 号 | 状态 |
|---|---|---|---|
| 1 | 欢迎来到未来 | BV1pb8o6yE8f | **已完成**，配色 C |
| 2 | 提示词工程 | BV1CQt365EzW | **已完成**（原配色 B，后统一为 C） |
| 3 | 软件仓库管理 | BV1kybV6DE47 | **已完成**，配色 C |
| 4 | 软件仓库管理 (2) | BV1Q6en6NEUo | **已完成**，配色 C |
| 5 | 软件的来龙去脉 | BV1Nyeq6qEt8 | **已完成**，配色 C（4 章 36 小节） |
| 6 | 需求和架构 (1) | BV1Rch76WEfQ | **已完成**，配色 C（4 章 34 小节） |

**全部 6 集已完成**，每集产物 = `<编号>/bili_summary_<BV>.html` + `screenshots/`。

## 本项目已定约定

- **目录编号以 `urllist.txt` 行号为准**（不是标题里的 `0X-Raw` 编号）。
- 配色是构建参数，`work/template.html` + `ch*.html` 保持原深色源不动。
- **已定配色 C 莫兰迪灰调**（用户指定）；四套候选都在 `2/_theme/`，且**都已压到 WCAG ≥4.5**。
- 浅色主题下 `line2` 需单独压深（它同时是 SVG 箭头填充与 `.ch-num` 颜色）。
- **4 章集（5、6）第 4 个章节色必须复用已登记槽位 `#3fd68c`**（→A5→主题 C 的
  `#64755f`），不能自创未登记 hex，否则 `colorize` 映射不到，构建后会残留旧色。
- **分章 HTML 里的 BV 号必须与 `urllist.txt` 大小写完全一致**（曾把 `…fQ` 误写成
  `…fq`，构建日志的「外部引用」会暴露多余的第二个 BV 链接，逐字核对即可发现）。
- 4 章模板的时间线色带宽度有限（≈162–328px），标题/时间段/描述要**分行**且收窄字号，
  否则 `check_render.py` 会报 SVG 文字重叠（5、6 集均踩过，见其修复记录）。
"""


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def copy_scripts(dst_root):
    dst = os.path.join(dst_root, "scripts")
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in skill_scripts():
        shutil.copy2(os.path.join(TOOLS, f), os.path.join(dst, f))
        n += 1
    return n


def main():
    check = "--check" in sys.argv
    base_md = os.path.join(USER_SKILL, "SKILL.md")
    if not os.path.exists(base_md):
        sys.exit(f"找不到通用技能正文: {base_md}")

    base = open(base_md, encoding="utf-8").read()
    proj_md = os.path.join(PROJ_SKILL, "SKILL.md")
    want_proj = base.split("\n---\n\n# 附：本项目专属")[0] + PROJECT_ADDENDUM

    print(f"repo       : {REPO}")
    print(f"tools (src): {TOOLS}  ({len([f for f in os.listdir(TOOLS) if f.endswith('.py')])} 个脚本)")

    drift = []
    # 两处技能副本的 scripts/ 都应等于 tools/
    for f in skill_scripts():
        for root, label in ((USER_SKILL, "user"), (PROJ_SKILL, "project")):
            d = os.path.join(root, "scripts", f)
            if os.path.exists(d) and md5(d) == md5(os.path.join(TOOLS, f)):
                continue
            drift.append((label, f))

    if check:
        if drift:
            print(f"\n✗ 有 {len(drift)} 处漂移：")
            for label, f in drift:
                print(f"    [{label}] scripts/{f}")
            sys.exit(1)
        print("\n✓ 两处技能副本与 tools/ 完全一致")
        return

    n1 = copy_scripts(USER_SKILL)
    n2 = copy_scripts(PROJ_SKILL)
    os.makedirs(PROJ_SKILL, exist_ok=True)
    open(proj_md, "w", encoding="utf-8").write(want_proj)
    print(f"\n  用户级 scripts/  <- {n1} 个")
    print(f"  项目级 scripts/  <- {n2} 个")
    print(f"  项目级 SKILL.md  = 通用正文 + 项目附录  ({len(want_proj)} 字符)")
    print(f"\n  {USER_SKILL}")
    print(f"  {PROJ_SKILL}")
    for label, f in drift:
        print(f"  (已修正漂移) [{label}] {f}")


if __name__ == "__main__":
    main()
