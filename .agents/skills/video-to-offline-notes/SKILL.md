---
name: video-to-offline-notes
description: 把长视频（B站/YouTube 等 yt-dlp 支持的站点）做成「可离线打开的单页 HTML 精读笔记」并交付整页截图与切片。当用户给出视频 URL 并要求：抓完整元数据、下载最佳音频转 mp3、Whisper 转写、按章节结构化提炼、动态生成 SVG 图解、生成内联 CSS/SVG 的单页 HTML、Chrome headless 整页截图校验、ffmpeg crop 切片时使用。内含本机 Windows 环境下已验证的命令、镜像源与四个必踩的坑（Chrome cookie 加密、超长页截图伪影、SVG 内 HTML 标签闯出、CUDA 版 ctranslate2 的模型下载）。
agent_created: true
---

# 长视频 → 离线单页精读笔记

## 适用

用户给一个视频 URL + 一段「元数据 / 转 mp3 / Whisper / 拆章 / 动态 SVG / 单页 HTML / headless 截图 / 切片」的流程要求。
全程产出物：`<out>/<slug>.html`（离线单页）、`screenshots/full.png`（整页图）、`screenshots/slices/`（带重叠切片）。

## 归档约定（本机 BiliSumerize 项目，务必先看）

工作区 `E:\Projects\VibeCoding\BiliSumerize`，**根目录 AGENTS.md 是项目入口**（先读它）。
通用工具链全在仓库根目录，各内容系列是独立子目录：

```
BiliSumerize/
├── AGENTS.md          # 项目入口说明（agent 必读）
├── bili_cookies.txt   # B 站 cookies，跨系列复用
├── bin/               # ffmpeg + ffprobe（跨系列共用）
├── models/            # faster-whisper-large-v3-turbo（跨系列共用）
├── tools/             # 通用脚本（本 skill scripts/ 的规范副本）
├── .agents/           # 项目记忆 memory/ + 项目技能 skills/（原 .workbuddy 更名）
├── jyy-generatice-se/ # jyy 系列：urllist.txt（集编号 = 行号）+ <编号>/ 每集一目录
│   └── <编号>/        #   bili_summary_*.html / lecture_notes_*.html / screenshots/ / work/
├── hw-dong/           # hw-dong 系列：url.txt + transcript_*.html + work/
└── 道草日记/           # 道草日记系列：<视频标题>/ 目录（url.txt + transcript_*.html + work/）
```

- **编号/归档位置以索引文件为准**（jyy 集 = `urllist.txt` 行号），别用标题里的 `0X-Raw`
  编号或凭印象推；拿不准就问一句——放错集再挪很烦（本集 BV1CQt365EzW 曾被指定成 `3`，实为行号 `2`）。
  一个仓库多个系列时，先确认用户指的是哪个系列哪个 `url.txt`（曾把 hw-dong 和道草日记两个请求串台）。
- 新视频开工前先看 `tools/` `bin/` `models/` 是否已存在，缺了才重新下载。
- `tools/` 里的脚本都是 CLI 参数化的，**不要在脚本里写死路径**：
  `build.py <work_dir> <out_html>`、`shot_full.py <html> <out.png> [w] [seg_h]`、
  `slice_crop.py <full.png> <outdir> [slice_h] [overlap]`、`check_render.py <html> [width]`、
  `svg_guard.py <html>`、`transcribe_whisper.py <audio> <out.json>`、`scan_blank_sheet.py`、
  `theme.py <work_dir> <out_dir> [keys]`（换配色）、`theme_preview.py`、`theme_check_svgs.py`。
- 改了 `tools/` 里的脚本，运行 `python tools/sync_skill.py` 同步本 skill 的 `scripts/` 副本。

## 环境事实（本机 Windows，先按这个找，找不到再装）

- yt-dlp：`E:\Projects\Repo\yt-dlp\release\yt-dlp_x86.exe`（另一份源码在 `E:\Projects\Repo\yt-dlp`，可直接读 `yt_dlp/*.py` 查行为）
- ffmpeg/ffprobe：本机无预装 → 现已在 `BiliSumerize/bin/`（314MB）；重建则解压到该目录
- Python：托管环境 `C:\Users\ASUS\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（有 faster-whisper / playwright / pillow / av）
- Chrome：`C:\Program Files\Google\Chrome\Application\chrome.exe`（Playwright 用 `channel="chrome"` 复用，不下载浏览器）
- GPU：RTX 4060 Laptop 8G，ctranslate2 可用 `float16`
- **curl 在本机基本不可用**（静默失败/极慢）→ 一律用 `python -c` + `urllib` 下载
- **`rm` 被沙箱接管**：删除失败会让整条 `&&` 链中断。要重新下载就**换文件名**，不要先删

## 变体：只要「文字稿」（不做可视化笔记）

用户明确说「文字稿 / 文字版 / 转成书面稿」时，**砍掉 SVG、截图、切片全部环节**，只走 1→3 步：

1. 元数据 + 音频 + Whisper 转写（流程同上，产出 `transcript.json` / `transcript_plain.txt`）。
2. **通读全文建立勘误映射**再动笔：口播视频（尤其带口音的）ASR 专有名词全崩，先扫一遍
   把「台湾讲→谭浩强」「冷压→K&R」这类错词列成表，书面化时按映射修正。
   **反讽/戏仿文本特殊规则**：作者故意写的荒诞破绽（如「Made in 巴黎」）不要"改正"；
   存疑 ASR 词用切片 + 换 initial_prompt 双轮重转确认，确认是原文就保留并加注。
3. 书面化整理成单页 HTML（无 SVG、纯文字 + 引文块 + 时间戳回跳链接 `?t=秒`）：
   - 无官方章节时**按内容脉络自拟 6~9 节**，每节头放时间戳，TOC 可跳转；
   - 观点只做书面润色，**不增删观点**；up 主引用的他人视频/评论放灰色引文块并标注来源；
   - 争议言论保留原意并注明「up 主个人观点/原话如此」；
   - 页脚放「转写勘误对照表」+ 音频/转写校验参数。
4. 交付前跑 `check_render.py`（无 SVG 时它只查横向溢出/空白块，仍然值得跑）。

命名建议 `transcript_<BV号>.html`，与可视化笔记 `bili_summary_<BV号>.html` 区分。

## 步骤

### 1. 元数据 + 音频

```bash
YT=/e/Projects/Repo/yt-dlp/release/yt-dlp_x86.exe
$YT --cookies bili_cookies.txt --no-warnings --dump-single-json "<URL>" > meta.json
```

**坑 1：Chrome cookies 取不到。** 新版 Chrome 用 App-Bound Encryption，`--cookies-from-browser chrome`
报 `Failed to decrypt with DPAPI`（yt-dlp issue 10927）。两条路：

1. **优先 Firefox**（明文 sqlite，最省事）：
   `$YT --cookies-from-browser firefox --cookies bili_cookies.txt --skip-download "<URL>"`
   → 得到可复用的 `bili_cookies.txt`，后续所有调用都带它。
2. 只有 Chrome 时，绕过库锁：把 `.../User Data/Default/Network/Cookies` 与 `.../User Data/Local State`
   复制到临时目录，再 `--cookies-from-browser "chrome:<tmp>/cprof/Default"`（yt-dlp 用 dirname 找 Local State）。
   *但这仍会被 ABE 拦住，只对旧版 Chrome 有效——实测失败，别在这上面耗时间。*

B 站优先 `-f 30280`（最高音轨，约 126 kbps AAC），不要用 `-x`（需要 ffmpeg 才能后处理，先把 m4a 抓下来）：
`$YT --cookies bili_cookies.txt -f 30280 -o "audio_raw.%(ext)s" "<URL>"`
元数据里 `chapters` 字段 = 官方章节，**直接拿来当拆章骨架**，不要自己编。

### 2. ffmpeg

`https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip`
≈195MB，GitHub 直连 2MB/s；`gyan.dev` 实测 0.15MB/s（慢 13 倍，别用）。
解压 `ffmpeg.exe` + `ffprobe.exe` 到 `BiliSumerize/bin/`（跨系列复用，已就位）。

```bash
FFMPEG=bin/ffmpeg.exe
$FFMPEG -y -i audio_raw.m4a -vn -c:a libmp3lame -b:a 192k -ar 44100 -ac 2 audio.mp3
bin/ffprobe.exe -v error -show_entries format=duration,bit_rate -of json audio.mp3
```
**时长校验**（与元数据比对，>5% 判异常/重下）：B 站 m4a 与转出的 mp3 通常 0.000% 偏差。

### 3. Whisper 转写（GPU）

**坑 2：模型下载。** faster-whisper 的 `turbo` 别名指向 `mobiuslabsgmbh/faster-whisper-large-v3-turbo`
（见 `faster_whisper/utils.py`）。直连 HF 会 401，且 `HF_ENDPOINT` 有时不生效 →
**直接用 urllib 从 `https://hf-mirror.com/<repo>/resolve/main/<file>` 下 5 个文件**
（config.json / model.bin / preprocessor_config.json / tokenizer.json / vocabulary.json，共约 1.6GB）
到 `BiliSumerize/models/faster-whisper-large-v3-turbo/`（已就位），
然后**把本地目录当模型路径传**，绕开所有下载逻辑。

```bash
WHISPER_MODEL="models/faster-whisper-large-v3-turbo" \
WHISPER_DEVICE=cuda WHISPER_CTYPE=float16 \
  python tools/transcribe_whisper.py audio.mp3 transcript.json
```
- 中文用 `large-v3-turbo` + `language="zh"`；英文才用 `small.en` + 翻中文。
- 静态裁剪：`condition_on_previous_text=False`（防止长音频复读循环）、`vad_filter=True`、
  `initial_prompt` 塞课程专有名词（否则专有名词全崩）。
- 98 分钟音频在 4060 上约 3.5 分钟（27.8× 实时）。
- **完整性校验**：`last_segment_end / audio_duration` 应 ≥99.9%，否则说明尾部被截。

### 4. 写页面

- 结构：hero（标题/UP/时长/标签/封面）+ 时间线总览 + 素材链路与校验 + 逐章小节 + 页脚（ASR 修正表）。
- 封面转 base64 data URI 内嵌，页面才真正离线可用（用 PIL 压到 640px、q82 约 60KB）。
- 时间戳回跳链接：`https://www.bilibili.com/video/BVxxxx?t=<秒数>`。
- 每小节：时间戳 + 问题 / 陷阱 / 步骤 / 结论 / 关键引用 / 视觉锚点，**按内容类型选块，不要每节都套满四种**。
- SVG 按内容形态生成：流程→步骤路径；概念→分层/关系；时间变化→时间线；对比→矩阵；
  风险误区→决策树/检查表；数据→简图；因果→链路。**每张图必须含本章真实关键词、箭头与标签**，
  不能是装饰图。用 `<tspan>` 做行内强调，别用 HTML 标签（见坑 3）。
- 章节头用不同强调色（第 1/2/3 章 = 青/紫/琥珀），可当截图对齐的探针。

**坑 3：SVG 里绝不能出现 HTML 的“闯出标签”。**
HTML 解析器在 `<svg>` 内遇到 `b|code|span|div|br|p|em|strong|font|ul|ol|li|table|h1..h6|i|small|img|...`
会**强制弹出 SVG 命名空间**：该标签之后的整个 SVG 被丢弃，文字变成页面正文泄漏到图外。
`<tspan>` / `<title>` / `<desc>` / `<a>` / `<image>` / `<style>` 是安全的。
→ 提交前必须跑 `scripts/svg_guard.py`（静态拦标签 + 源码/DOM `<text>` 数量比对）。

### 4.5 换配色（用户觉得丑时的正确做法）

不要靠手改某几个颜色——页面里 28 张 SVG 把颜色**写死在 SVG 属性里**（`fill="#0f151d"` 之类），
只换 CSS 变量会让深色 SVG 留在浅色页面上，非常难看。

正确做法是 **role 映射**（`tools/theme.py`）：

- 原页面只有 **12 个结构色 + 6 个强调色**，所有 `rgba()` 都是强调色的 alpha 变体。
- 结构色：`#0a0e13`bg / `#0f151d`bg2(figure+SVG底) / `#141d28`panel / `#18232f`panel2
  / `#111a24`node / `#1c2836`+`#1d2a3a`trace / `#233240`line / `#31465c`line2
  / `#e9eff7`tx / `#adbccd`tx2 / `#77879a`tx3 / `#000`cover
- 强调色 6 槽位：A1`#46c6e0`青 / A2`#a98bfa`紫 / A3`#f0b429`琥珀 / A4`#f8736e`红
  / A5`#3fd68c`绿 / A6`#5b9cf8`蓝（同时承担章节色 c1/c2/c3 = A1/A2/A3）
- 转换顺序：先按 hex 直查映射，再正则抠 `rgba(r,g,b,a)` 按 rgb 反查槽位、保留 alpha。
- 版式开关（「丑」往往不只是色相问题）：
  `glow=False` 去掉 hero 的双 radial-gradient 光晕；
  `grad="flat"` 把块的 `linear-gradient(180deg,rgba(x,.07),rgba(x,.02))` 拍成纯色
  —— 这两条对「太花」的改善最大。
- 生成后必须断言**无残留旧色**，否则说明有颜色漏映射（如写死的 3 位 hex）。
- `tools/theme.py <work_dir> <out_dir> [A B C D...]` 生成变体；
  `tools/theme_preview.py <theme_dir> <out_dir>` 出样张；
  `tools/theme_check_svgs.py <html> <out.png> [N] [scale]` 抽 N 张 figure 拼版，
  专门核对浅色主题下 SVG 的可读性（这是换浅色时唯一靠肉眼才能发现的风险）。
- 让用户挑，不要替他定。给 3～4 套：浅色 2～3 套（暖纸 / 冷白 / 低饱和）+ 深色精修 1 套。
- **出候选项之前，就把每一套都压到合规**——不要只压自己猜他会选的那套。
  实测教训：只给低饱和那套做了对比度修正、其余按原始值出样张，用户比对后反而选了
  「更清楚」的白底那套（正文 15.65 vs 12.14）；而且他选中的那套**原本也有 5 处不达标**
  （tx3 在 panel 上 2.86、A2 3.87、A3 2.94、A5/A6 4.06），只是相对更亮而已。
  让用户在同一条起跑线上比较，否则他其实是在比**谁更没被我压深**，不是在比配色品味。
- **交付前必须量化对比度**（`theme.report_contrast` / WCAG）：
  低饱和方案（莫兰迪那类）预览时很好看，但前景色实测常常只有 2.5～3.0，
  远低于正文需要的 4.5。做法是**保色相、压明度**——把强调色和 tx3 往黑里调到 ≥4.65，
  灰调观感基本不变但真正可读。实测莫兰迪 6 个强调色从 2.5～2.9 压到 4.60 才算合格。
  另外确认这些强调色**没有用作实心形状填充**（都走 rgba 淡色），否则压深会把浅色文字压死。
- 别漏了 `line2`：它同时充当 SVG 箭头填充和 `.ch-num` 颜色，浅色底上需要单独压深
  （B 方案 #c8d1db → #a9b5c2），否则图里的连接箭头看不清。
- 选定后写进构建流程：`build.py <work_dir> <out_html> --theme C`，
  源文件保持原色不变，配色只是构建参数，随时可换。

### 5. 截图与切片**坑 4：超长页面的 `full_page=True` 一次性截图会产出错位图。**
实测 24254px 高的页面：第 3 章章节头被下移 983px 且章节色丢失（章节头边框从琥珀变回青），
即 PNG 与 DOM 页面坐标不再一一对应 → 按绝对 y 切片会切错内容，且**肉眼看缩略图看不出来**。
必须用 `shot_full.py`：**按页面坐标分段 `clip` 截取再纵向拼接**，最后断言 `sheet.size == (W,H)`。

```bash
T=tools                     # 本 skill scripts/ 下的同名脚本亦可
python $T/shot_full.py "<html>" screenshots/full.png 1440 4000
```
对齐自检：扫描章节头强调色的全宽横线，其 y 必须等于 DOM 实测 y（`getBoundingClientRect().top + scrollY`）。

切图（保留 ~100px 重叠，避免切断标题）：
```bash
FFMPEG_BIN=bin/ffmpeg.exe python $T/slice_crop.py \
  screenshots/full.png screenshots/slices 1600 100
```

读图检查（必做，且要读**多张切片**、不能只看缩略图）：渲染是否正确、有无重叠、有无空白带。
再用 `$T/check_render.py` 做 DOM 级体检（文字互相重叠 / 文字超 SVG 框 / 横向溢出 / 源码-DOM 文本数比对）。
正常结果应全为 0；只看缩略图会漏掉「图被截断」这类问题。

> 注意：Read 工具对图片按内容缓存。用 `ffmpeg crop` 生成**新文件名**再看，
> 别反复读同一个切片路径后靠印象判断（曾因此把错位的旧图当成正确渲染）。

## 判定标准

- 时长偏差 ≤5%、转写覆盖率 ≥99.9%
- SVG 内无闯出标签、源码 `<text>` 数 == DOM `<text>` 数
- 文字重叠 0、超框 0、横向溢出 0
- 无损段空白：连续空白带只允许出现在章节之间（约 120～170px 的 section 间隔）与页脚底部内边距
- 整页图尺寸 == 文档 `scrollHeight`


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
WHISPER_MODEL=models/faster-whisper-large-v3-turbo WHISPER_DEVICE=cuda WHISPER_CTYPE=float16   $P $T/transcribe_whisper.py $E/work/audio.mp3 $E/work/transcript.json

# 4 写 template.html + ch1..chN.html（用 yt-dlp 返回的 chapters 当骨架）

# 5 拼装（配色作为构建参数；本项目当前统一用 C 莫兰迪灰调）
$P $T/build.py $E/work $E/bili_summary_<BV>.html --theme C
$P $T/svg_guard.py $E/bili_summary_<BV>.html
$P $T/check_render.py $E/bili_summary_<BV>.html 1440

# 6 整页图 + 切片 + 总览
$P $T/shot_full.py $E/bili_summary_<BV>.html $E/screenshots/full.png 1440 4000
FFMPEG_BIN=$(pwd)/bin/ffmpeg.exe   $P $T/slice_crop.py $E/screenshots/full.png $E/screenshots/slices 1600 100
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
