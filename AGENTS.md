# AGENTS.md — BiliSumerize 项目入口

> 任何 Agent（无论用什么工具）打开本仓库，先读本文件。
> 它是项目的唯一入口说明书；更细的长期约定在 `.agents/memory/MEMORY.md`。

## 项目性质

把 B 站长视频做成**可离线打开的单页 HTML 产物**。两类产物：

1. **文字稿** `transcript_<BV号>.html` — 口播书面化，无 SVG/截图，最常用
2. **可视化笔记** `bili_summary_<BV号>.html` — 含动态 SVG 图解 + 整页截图切片

目前三个内容系列（各自独立目录，工具链共用根目录）：

| 目录 | 内容 |
|---|---|
| `jyy-generatice-se/` | jyy 南大《生成式软件工程》全 6 集（可视化笔记 + 文字讲义），集编号 = `urllist.txt` 行号 |
| `hw-dong/` | UP 主 hw-dong 的视频，链接在 `hw-dong/url.txt` |
| `道草日记/` | UP 主道草日记，每个视频一个子目录（`<标题>/url.txt` + 产物） |

## 目录结构

```
BiliSumerize/
├── AGENTS.md            # 本文件（agent 入口）
├── tools/               # 通用 Python 脚本（13 个，CLI 参数化，勿写死路径）
├── bin/                 # ffmpeg.exe + ffprobe.exe（Windows 版）
├── models/              # faster-whisper-large-v3-turbo（本地模型，1.6G，勿删）
├── bili_cookies.txt     # B 站 cookies（Firefox 导出，跨系列复用）
├── jyy-generatice-se/   # jyy 系列：urllist.txt + 每集一个编号目录
│   └── <编号>/          # bili_summary_*.html / lecture_notes_*.html / screenshots/ / work/
├── hw-dong/             # hw-dong 系列：url.txt + transcript_*.html + work/
├── 道草日记/             # 道草日记系列：<视频标题>/ 目录，内含 url.txt + transcript_*.html + work/
└── .agents/             # Agent 上下文（记忆 / 技能 / 提示词）
    ├── memory/          # MEMORY.md 长期约定 + YYYY-MM-DD.md 每日日志（追加式）
    ├── skills/          # 项目级技能（video-to-offline-notes；scripts/ 是 tools/ 的镜像）
    └── Prompt.txt       # 最初的流程提示词（历史参考）
```

## 工具链速查

**视频 → 文字稿/笔记的完整流程**：加载技能 `.agents/skills/video-to-offline-notes/SKILL.md`
（用户级同名技能在 `~/.workbuddy/skills/`，两者内容保持一致）。

常用命令（工作目录 = 各系列自己的目录，`work/` 放中间产物）：

```bash
# 元数据 / 音频（curl 不可用，下载一律 yt-dlp / python urllib）
/e/Projects/Repo/yt-dlp/release/yt-dlp_x86.exe --cookies ../../bili_cookies.txt ...
bin/ffmpeg.exe -y -i audio_raw.m4a -vn -c:a libmp3lame -b:a 192k -ar 44100 -ac 2 audio.mp3

# Whisper 转写（GPU，覆盖率应 ≥99.9%）
WHISPER_MODEL="models/faster-whisper-large-v3-turbo" WHISPER_DEVICE=cuda WHISPER_CTYPE=float16 \
  python tools/transcribe_whisper.py audio.mp3 transcript.json

# 渲染体检（交付前必跑，应全零）
python tools/check_render.py <out.html> 1440
```

其他脚本：`build.py`（拼装页面）/ `shot_full.py`（分段截图，禁一次性 full_page）/ `slice_crop.py` / `svg_guard.py` / `theme.py`（换配色）等，用法见各脚本 docstring 或技能正文。

## 硬性约定（踩坑沉淀，勿违反）

1. **curl 本机不可用** → yt-dlp / python urllib。
2. **编号以索引文件为准**（jyy 集 = `urllist.txt` 行号），不要从标题猜。
3. 反讽/戏仿类视频（如道草日记）**不要"改正"作者故意写的荒诞破绽**；存疑 ASR 词用切片 + 换 initial_prompt 双轮重转确认，仍存疑就保留原文加注。
4. 中间产物放各系列的 `work/` 子目录；交付物放系列目录根部。
5. 交付前必跑 `tools/check_render.py`，结果应全零。
6. `tools/` 是脚本唯一来源；`.agents/skills/*/scripts/` 只是镜像，**不要直接改镜像**——改完 tools 后运行 `python tools/sync_skill.py` 同步，`--check` 验证。
7. `.agents/memory/YYYY-MM-DD.md` 为追加式日志；长期约定沉淀进 `.agents/memory/MEMORY.md`。
8. 完成 15+ 工具调用的多步任务后，考虑把新流程更新进技能。

## 关于 .agents/（对 WorkBuddy 的特别说明）

本目录由原 `.workbuddy/` 更名而来。WorkBuddy 不再自动注入其中的记忆与项目技能——
**请 Agent 主动读取**：开工先读 `.agents/memory/MEMORY.md`，收尾写当日日志。
