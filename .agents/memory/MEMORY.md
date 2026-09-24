# MEMORY.md — BiliSumerize 项目长期约定

> 本文件在 `.agents/memory/`（2026-09-23 由 `.workbuddy/` 更名）。
> WorkBuddy 不再自动注入本目录内容，**Agent 开工先读仓库根目录 AGENTS.md**，再读本文件。
> 若 `.workbuddy/` 目录被 WorkBuddy 自动重建，其中内容是自动生成的，真实记忆以本文件为准。

## 项目性质

把 B 站视频做成可离线打开的单页产物。三个内容系列（2026-09-23 起多系列并存）：

1. `jyy-generatice-se/` — jyy 南大《生成式软件工程》系列（可视化笔记 + 文字讲义，全 6 集已完成）。
2. `hw-dong/`（2026-09-23 起）— UP 主 **hw-dong** 的视频：`url.txt` 放链接，
   每视频产出 **`transcript_<BV号>.html` 文字稿**（书面化，不做 SVG/截图/切片）；
   中间产物在 `hw-dong/work/`。
3. `道草日记/<视频标题>/`（2026-09-23 起）— UP 主道草日记：每视频一个子目录
   （`url.txt` + `transcript_<BV号>.html` + `work/`），首集 BV16aeP6iEec 已完成。
4. `圣徒城的小诺/`（2026-09-24 起）— UP 主**圣徒城的小诺**：`url.txt` 放链接，
   每视频产出 **`bili_summary_<BV号>.html` 可视化笔记 + `lecture_notes_<BV号>.html` 讲义**，
   中间产物在 `圣徒城的小诺/work/`。首集 BV1PKh86zEhX（AI 编程模型/基座横评）已完成。
5. `马克的技术工坊/`（2026-09-24 起）— UP 主**马克的技术工作坊**（目录名少一个「作」字，
   用户指定；视频里自称「马克」）：`url.txt` 放链接，同样产出 **总结 + 讲义**。
   首集 BV154426xEha（AI 编程全流程，7 个官方章节）已完成。

**称谓约定**：jyy 系列是大学课程 → 用「讲师」；**其余 UP 主/播客类系列一律用「UP 主」**，
正文与讲义都不得出现「讲师」。

工具链（bin/models/tools/cookies）2026-09-23 起统一放**仓库根目录**，全系列共用。
**多系列并存后，动手前先确认用户指的是哪个系列哪个 `url.txt`**（曾把 hw-dong 与道草日记两个请求串台）。

## 目录约定（2026-09-23 重组后）

```
BiliSumerize/
├── AGENTS.md            # 项目入口说明（agent 必读）
├── bili_cookies.txt     # B 站 cookies（Firefox 提取），跨系列共用
├── bin/                 # ffmpeg.exe + ffprobe.exe（跨系列共用）
├── models/              # faster-whisper-large-v3-turbo（跨系列共用，1.6G，勿删）
├── tools/               # 跨系列通用脚本（唯一事实来源，见下）
├── .agents/             # memory/ + skills/（原 .workbuddy 更名而来）
├── jyy-generatice-se/
│   ├── urllist.txt      # 集数索引：<编号>-<标题> [0X-Raw/26生成式软件工程/NJU]: <URL>
│   └── <编号>/          # 每集一个目录，编号 = urllist.txt 的行号
│       ├── bili_summary_<BV号>.html    # 可视化笔记交付物
│       ├── lecture_notes_<BV号>.html   # 文字版讲义
│       ├── screenshots/                # full.png / _overview.png / slices/ / els/
│       └── work/                       # 该集材料：音频、转写、分章源文件、校验报告
├── hw-dong/             # url.txt + transcript_*.html + work/
└── 道草日记/            # <视频标题>/ 子目录：url.txt + transcript_*.html + work/
└── 圣徒城的小诺/         # url.txt + bili_summary_*.html + lecture_notes_*.html + screenshots/ + work/
```

**编号必须以 `urllist.txt` 为准**，不要凭标题里的 `0X-Raw` 或其它编号推。
实例：BV1CQt365EzW = 「2-提示词工程」→ 目录 `2/`（曾一度被说成 3，确认后改回 2）。

## tools/ 脚本（均为 CLI 参数化，路径不要在脚本里写死）

| 脚本 | 用途 |
|---|---|
| `transcribe_whisper.py <audio> <out.json>` | faster-whisper 转写 + 覆盖率校验 |
| `build.py <work_dir> <out_html> [--theme KEY]` | 拼装单页 HTML（占位符 `__CHAPTERS__` / `__COVER_B64__`）+ 结构回归检查；`--theme` 指定配色 |
| `shot_full.py <html> <out.png> [w] [seg_h]` | 分段 clip 截取再拼接的整页图（**不要用一次性 full_page**） |
| `shot_page.py` / `shot_element.py` | 普通整页 / 元素级截图 |
| `check_render.py <html> [w]` | DOM 级体检：文字重叠、超框、横向溢出、源码-DOM text 数比对 |
| `slice_crop.py <full.png> <outdir> [h] [overlap]` | ffmpeg crop 切片，默认 1600px 高 / 100px 重叠 |
| `scan_blank_sheet.py` | 空白带扫描 + 缩略总览图 |
| `svg_guard.py <html>` | 拦截 SVG 内 HTML 闯出标签（会把整张图打断） |
| `theme.py <work_dir> <out_dir> [keys]` | 换配色：12 结构色 + 6 强调色 role 映射 + 光晕/渐变开关 |
| `theme_preview.py <theme_dir> <out_dir>` | 每个配色变体出样张（首屏 + 正文区） |
| `theme_check_svgs.py <html> <out.png> [N]` | 抽 N 张 figure 拼版，核对配色下 SVG 可读性 |
| `sync_skill.py [--check]` | 把技能沉淀到项目 + 同步脚本镜像（见下） |

## 技能沉淀（两级）

流程知识已沉淀为技能 `video-to-offline-notes`，**两级都存在**：

| 级别 | 路径 | 用途 |
|---|---|---|
| 用户级 | `C:\Users\ASUS\.workbuddy\skills\video-to-offline-notes\` | 跨项目复用 |
| 项目级 | `.agents\skills\video-to-offline-notes\` | 跟着本仓库走，含「本项目专属」附录 |

**唯一事实来源与同步**：

- 脚本唯一来源 = `tools/*.py`（14 个，`sync_skill.py` 本身不入镜像）
- 技能里的 `scripts/`（两处各 13 个）是**镜像，不要直接改**
- 改完脚本执行：
  ```bash
  python tools/sync_skill.py          # 同步
  python tools/sync_skill.py --check  # 查漂移（不一致则退出码 1）
  ```
- 技能正文（通用部分）唯一来源 = 用户级 `SKILL.md`；
  项目级 `SKILL.md` = 用户级正文 + `sync_skill.py` 里的 `PROJECT_ADDENDUM` 自动追加。
  两边 `SKILL.md` **都不要手改**：改通用正文改用户级那份，改项目附录改 `sync_skill.py` 常量。

## 换配色的关键约束（重要）

页面里 28 张 SVG 的**颜色写死在 SVG 属性里**（如 `fill="#0f151d"`），
只改 CSS 变量会导致深色 SVG 留在浅色页面上。必须走 `theme.py` 的 role 映射：
- 结构色 12 个：bg `#0a0e13` / bg2 `#0f151d` / panel `#141d28` / panel2 `#18232f`
  / node `#111a24` / trace `#1c2836`+`#1d2a3a` / line `#233240` / line2 `#31465c`
  / tx `#e9eff7` / tx2 `#adbccd` / tx3 `#77879a` / cover `#000`
- 强调色 6 槽位 A1..A6 = `#46c6e0`青 `#a98bfa`紫 `#f0b429`琥珀 `#f8736e`红 `#3fd68c`绿 `#5b9cf8`蓝
  （章节色 c1/c2/c3 即 A1/A2/A3）
- 所有 `rgba()` 都是强调色的 alpha 变体，按 rgb 反查槽位、保留 alpha
- 「丑」的一半来自版式：`glow=False` 去 hero 光晕、`grad="flat"` 把块底渐变拍平
- 生成后必须断言无残留旧色

已备 4 套候选（`2/_theme/`）：A 纸墨暖白 / B 极简冷白 / C 莫兰迪灰调 / D 石墨夜（深色精修）。

## 全 6 集已完成，统一配色 C 莫兰迪灰调（2026-09-23 最终）

**最终配色 = C 莫兰迪灰调**，全部 6 集以 `--theme C` 构建。
（曾来回：先按口头选择做 C → 口头对比说 B 更好读 → 改成 B → 用户看到 `theme_C.html`
实际样张后明确指「用这个主题」，**定回 C**。
**教训：口头偏好会反复，以用户指着样张说的那次为准；但无论选哪套，交付前都要跑 WCAG
体检（`theme.report_contrast`）——C 与 B 初版都不达标，都是压深后才合规。**）

| 集 | 标题 | BV 号 | 章节 | 小节 | HTML |
|---|---|---|---|---|---|
| 1 | 欢迎来到未来 | BV1pb8o6yE8f | 3 | — | 268 KB |
| 2 | 提示词工程 | BV1CQt365EzW | 3 | — | 253 KB |
| 3 | 软件仓库管理 | BV1kybV6DE47 | 3 | — | 208 KB |
| 4 | 软件仓库管理 (2) | BV1Q6en6NEUo | 3 | — | 175 KB |
| 5 | 软件的来龙去脉 | BV1Nyeq6qEt8 | **4** | 36 | 199 KB |
| 6 | 需求和架构 (1) | BV1Rch76WEfQ | **4** | 34 | 214 KB |

源文件 `work/template.html` + `ch*.html` **保持原深色不动**，配色只是构建参数，随时可换。

## 文字版讲义（lecture_notes_*，2026-09-23 起全 6 集齐备）

每集在可视化笔记之外还有一份**文字版精读讲义** `<集>/lecture_notes_<BV号>.html`：

- 样板与唯一结构参考 = `2/lecture_notes_BV1CQt365EzW.html`（hero+目录+章节 article
  + 每章小结/思考题 + 附录 A 术语表 / B 时间戳索引 / C prompt 范例或论断速查）
- 写作底稿 = `work/chap*.txt` 全文精读改写（书面化、修正 ASR，禁止虚构），
  术语修正以可视化笔记 footer 勘误表为基准（可扩展）
- 4 章集的 CSS 需自加第 4 强调色 c4（`--c4:#2e7d32; --c4bg:#e9f4ec`，WCAG 安全绿）
- 时间戳链接 `?t=秒`；BV 号从 meta.json 逐字复制（ep6 大小写坑）
- 交付前跑 `check_render.py`（venv python：`~/.workbuddy/binaries/python/envs/default/Scripts/python.exe`）
- 批量生成模式：每集派一个并行子代理 + **主会话亲自复检**（Agent 回传可能为空）

### 4 章布局的两条硬约束（第 5、6 集踩过）

1. **第 4 个章节色必须复用已登记槽位 `#3fd68c`**（→A5→主题 C 的 `#64755f`）。
   `colorize` 只能映射已登记颜色，自创 hex 会在构建后残留旧色。构建后 `grep` 旧色应为 0。
2. **4 色时间线色带只 162–328px 宽**，标题/时间段/描述必须分行 + 收窄字号，
   否则 `check_render.py` 报 SVG 文字重叠（第 5 集 2 处，收到 11.5/10/9.5 并拆行后归零）。

### 交付前的自动哨兵

- **构建日志的「外部 src/href 引用」列表**：若出现两条 BV 链接（如 `…fQ` 与 `…fq`），
  说明分章 HTML 里 BV 号大小写写错（第 6 集 37 处踩过）。逐字对照 `urllist.txt` 即可发现。
- **`check_render.py`** 全零：文字重叠 / 超框 / 横向溢出 / 空白块 / 源码-DOM `<text>` 一致。

**交付前必须做的对比度体检**：低饱和/浅色方案肉眼好看但实测常不达标。
- C 初版：tx3 仅 2.94，6 个强调色 2.5～2.9
- B 初版：tx3 在 panel 上 2.86、A2 3.87、A3 2.94、A5/A6 4.06
- 修法：保色相压明度，把 tx3 与 A1–A6 全部压到 ≥4.5（`theme.report_contrast` 可复核）
- 前提：这 6 个强调色在页面里**没有用作实心形状填充**（全走 rgba 淡色），压深只影响文字与描边
- 顺带压深 `line2`：它同时充当 SVG 箭头填充与 `.ch-num` 颜色，纯白底上原色偏淡

## 已验证的环境坑（勿重复踩）

1. 本机 **curl 不可用** → 一律 `python -c` + `urllib` 下载。
2. **`rm` 被沙箱接管**且失败会中断 `&&` 链 → 重下换文件名，别先删。
3. **Chrome cookies 取不到**（App-Bound Encryption）→ 用 **Firefox** 提取。
4. ffmpeg 源用 BtbN GitHub release（2MB/s）；gyan.dev 仅 0.15MB/s。
5. faster-whisper 的 `turbo` 别名 → `mobiuslabsgmbh/faster-whisper-large-v3-turbo`；
   直连 HF 会 401，用 `hf-mirror.com` 逐文件下载后当本地路径传。
6. HTML 解析器遇到 `<svg>` 内的 `code/span/div/p/...` 会弹出 SVG 命名空间，
   **之后再无 SVG** → 行内强调必须用 `<tspan>`。
7. 超长页 `full_page=True` 一次性截图会错位（实测偏移 983px 且丢章节色），
   且缩略图看不出来 → 必须用 `shot_full.py` 的分段拼接法。
8. `shot_full.py` / `slice_crop.py` 都吃**位置参数**（`--width` 会 ValueError）；
   `slice_crop.py` 靠环境变量 `FFMPEG_BIN` 找 ffmpeg，不设会 `WinError 2`：
   `FFMPEG_BIN=<repo>/bin/ffmpeg.exe python ../tools/slice_crop.py <full.png> <outdir> 1200 100`
9. **`tools/transcribe_whisper.py` 的 PROMPT 写死了 jyy 课程术语** → 换视频另存一份改
   PROMPT（如 `work/transcribe_nuo.py` / `work/transcribe_mark.py`），不要直接改 tools。
   给横评类视频放大模型名/产品名词表可显著降低专名错字率。
10. **正文里禁止写 `**加粗**`** —— 模板只认 `<strong>`，`**` 会原样显示在页面上。
    （圣徒城那份曾遗留 4 处，2026-09-24 已修源码 + 重建 + 重截图。）
11. **SVG 里相邻两行的行距要 ≥20px**（字号 11.5）。把 `y=185 / y=196` 这种
    11px 行距塞进 60px 高的框，`check_render.py` 必报重叠（area 400+）。
12. **官方 chapters 数 = 章节色数**：设计系统只有 6 个 accent，7 章时让末章复用第 1 章
    的颜色（「首尾都是全局视角」），并写进图注 —— 不要自造第 7 个 hex，否则
    将来跑 `theme.py` 会漏映射、残留旧色。
13. **多章页面的 TOC 卡片数不是 3 的倍数**时，给最后一张加 `grid-column:1/-1` 跨满整行，
    否则会留一个孤立的 card。

## git push 静默失败 exit 128 → 先查 `http_proxy`（2026-09-24）

**症状**：`git push` 返回 exit 128 且 **stdout/stderr 全空**，
但 `git ls-remote` / `git credential fill` / 带凭据的 HTTP 请求都正常 —— 极易误判成凭据坏了。

**根因**：本机环境变量里有 `http_proxy=http://127.0.0.1:9982`（**注意 `http_proxy` 也在，
不只有 `https_proxy`**）。git 走该代理访问 `git-receive-pack` 拿到 401 后，
回头调 `git credential-manager get` 时**静默退出**，凭据从未回填重试。

**解法**（已验证）：
```powershell
Remove-Item Env:\http_proxy,Env:\https_proxy,Env:\HTTP_PROXY,Env:\HTTPS_PROXY -ErrorAction SilentlyContinue
```
`NO_PROXY=gitee.com` **无效**，必须真删变量。推成功后 `git status -sb` 应无 `ahead`。

**排查方法**：`GIT_CURL_VERBOSE=1` + `GIT_TRACE=1` 重定向到文件；
或用 python `subprocess.run(capture_output=True)` 调 git 拿真实退出码
（PowerShell 会把 git 的 stderr 包成 `NativeCommandError` 并吞掉内容）。

## 无第二信源时的「定点复转」（2026-09-24 起）

若视频 **既无 CC 字幕、也无 UP 附带的字幕文件**，就写一个窄窗复转脚本
（`work/recheck.py`：`clip_timestamps=[start, start+dur]` + 环境变量传 `WHISPER_PROMPT`），
对存疑专名做 2 轮不同提示词的重转：
- 两轮一致 → 采信
- 两轮不同 → 结合上下文音近推定，标**存疑**
- 仍无法判定 → 保留原文并加注

实例（BV154426xEha）：`ChairGPT→ChatGPT`、`覆盖倒→覆盖到`、`断板→短板`、
`交付体验→交互体验`（均改）；`网答/网达→访达（Finder）`（音近推定，存疑）。

## 双源 ASR 交叉校验（2026-09-24 起，模型名密集的视频默认启用）

若 UP 主**随附件提供了字幕**（如 vCaptions SRT），把它当**独立第二转写源**与 Whisper 逐条比对：
- 两源一致 → 直接采信
- 两源分歧 → 进勘误表；模型名以官方为准，其余标「存疑」不擅改
- 两源都写成同一荒诞词 → 多半是作者口语梗，按规则**保留原文加注**

实例：BV1PKh86zEhX 的 `Fibro 5 / FBL5.1`→`Fable 5`（存疑）、
`千问 3.8 27B vs 2107B`（两源不一致，存疑）、`美国大豆包`（作者戏称，保留）。
