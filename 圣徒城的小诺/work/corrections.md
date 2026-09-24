# ASR 勘误映射表 — BV1PKh86zEhX

`transcript.json`（faster-whisper large-v3-turbo，coverage 99.99%）与自备 SRT 双源交叉比对。
两源对同一处词形有分歧时，以**语义 + 语境 + 两源互证**定夺；仍不能确定的保留原文并加注。

## A. 模型 / 产品名（确定性高）

| ASR 原文（Whisper） | SRT 写法 | 判定 |
|---|---|---|
| B站的各位小伙伴 / 圣图城的小诺 | 圣屠城的小诺 | 圣徒城的小诺（UP 名，以频道名 `圣徒城的小诺` 为准） |
| GPT6、ZVT6、GBT6、GPT6 ASTRA | GBT6、GBT6ASRA | **GPT-6**；`ASTRA` → **Astra**（GPT-6 的版本/档位名） |
| GPT5.6、GPT5.6SO | GPT5.6、Gb t5.6 | **GPT-5.6**；`SO` → **SOTA** |
| GPT Luna / Terra | GPTLUNA / TARA | **GPT Luna** / **GPT Terra** |
| Cloud Ops 5 / Cloud 系列 | cloud obs5 / COUD欧布四五 | **Claude Opus 5**；`Cloud 系列` → **Claude 系列** |
| Fibro 5 / Fibro 5.1 | fib5 / FBL5.1 | **Claude Fable 5 / Fable 5.1**（音近 Fable，两源均碎，见 B 类存疑） |
| Deepseek V4.1 Flash | deep sk v4.1flash | **DeepSeek V4.1 Flash** |
| DS V4.1 Flash 的 Sentime | DSSV4.1flash的生态位 | **生态位**（Sentime 为生态位误识别） |
| GAM5.3 / G1 5.2 / JM5.3 / Giamh 5.3 / 加盟5.3 | GMM5.3 / GMM5.2 | **GLM-5.3** / **GLM-5.2** |
| Glock 4.6 / GROUCK4.6 / Grog | GROCK / GROUCK | **Grok 4.6**（`Grog Build` → **Grok Build**） |
| KIMI K3 | KIMIK3 | **Kimi K3** |
| minimax M3 / M4 | mini max m3 | **MiniMax M3** |
| 千问 3.8 / 千文 3.8 · 千问 3.8 27B / 2107B | 千户3.8 / 千问3.82107B | **通义千问 3.8**；小模型参数量存疑（27B / 210B / 207B，见 B 类） |
| CM3.8 Flash | 3.8flash | **Gemini 3.8 Flash**（两源均碎，据上下文「与 Gemini 3.8 Flash 同列」推定） |
| Gemini 3.8 Flash / 詹密奈 / 詹密奈系列 | GEMINI3.8flash / 詹密奈系列 | **Gemini 3.8 Flash**（「詹密奈」= Gemini 音译残留） |
| Anti-Gravity | ANTIGRAVITY | **Antigravity**（用于跑 Gemini 的客户端） |
| 美国大豆包 | 美国大豆包煎饼袋 | **「美国的大模型」的戏称**，作者式玩笑，**保留原样不"改正"** |

## B. 开发框架 / 基座

| ASR 原文 | 判定 |
|---|---|
| CodeX / code ax / Code s s | **Codex**（OpenAI 的 coding agent 框架） |
| Cloud Code / CouldCode / cloud code | **Claude Code** |
| OpenCode / Open code | **OpenCode** |
| Zcode / z code | **Zcode**（GLM / 智谱的 CLI 框架） |
| Kimi CLI / KIMI Code | **Kimi CLI** / **Kimi Code** |
| Grok Build | **Grok Build** |
| Deep Seek Harness / Dipsick Harness | **DeepSeek Harness** |
| CC | **Claude Code** 的口头简称（原文「把它接到 CC 里面来用」） |
| Cooder / coder | **通义千问 Coder** 代码模型 |
| 哈里斯 / Harness | **Harness**（agent 框架的代称，原文两种说法混用） |
| 插线化 / 插件化 | **插件化** |
| 千言化 | **前沿化**（「设计是比较前沿化的」） |
| Response 这种 Codex 的专属端点 | **Responses API**（Codex 的专属端点） |
| 之谱的 Zcode | **智谱的 Zcode** |

## C. 通用术语

| ASR 原文 | 判定 |
|---|---|
| 指令秩序 / 指令咨询 / 指令信息 | **指令遵循** |
| 主绘画 / 单个绘画 / 单绘画 | **主对话** / **单个会话** / **单会话** |
| 上下纹 / 伤害纹 | **上下文** |
| 子弹里 / 纸代理 / AZEN / A整 / a ent | **子代理** / **子代理** / **Agent** |
| 开发机座 | **开发基座** |
| 自我验收不稳 | **自我验收不稳**（原话如此，保留） |
| 毛坯化 | **毛坯化**（原话如此，指功能能跑但粗糙，保留） |
| 漂移 / 飘移 | **漂移** |
| 多摩汉 / 多么太 / 多么太爱 / 多模态 | **多模态** |
| Agent Sparm 能力 | **Agent / Agentic 能力** |
| 抽卡 | **抽卡**（原话，指一次性直出、靠运气出好效果，保留） |
| 降制 / 降智 | **降智** |
| region / 验证 | **验证**（「没有什么太多 region」= 没有太多验证） |
| 浮腹的 / 服负载 | **服务负载** |
| 屏替 | **平替** |
| 情话 / 青蛙 / 生态位 | **生态位** |
| 学一类的教训 / 血与泪的教训 | **血与泪的教训** |
| 常任务 / 长任务 | **长任务** |
| 擦枪人意 / 差强人意 | **差强人意** |
| 不经验 / 不惊艳 | **不惊艳** |
| 一次性指令值出 | **一次性指令直出** |
| 对抗审查 | **对抗审查**（保留） |
| 缓存命中率 | **缓存命中率** |
| 缓存量很多 | **缓存量很多**（指单会话下 KV cache 命中多、单价低） |
| 异步通信 / 一步通信 | **异步通信** |
| 分拍拍工作 | **分派工作** |
| 主规划执行执入了一个任务 | **主代理直接植入了一个任务** |
| 史山 / 屎山 | **屎山**（代码库） |
| 龙虾 | **「龙虾」**（原文如此，指某类玩法/工具，无法确定所指，**保留原样并加注**） |
| 制作视频补义 / 不易 | **制作视频不易** |
| 闲雨上 | **闲鱼上** |
| 六七百币 | **六七百 B**（指模型参数量级 600–700B） |
| 700 多币 | **700 多 B** |
| 500B 以上 / 外壁以下 | **500B 以上** / **500B 以下** |
| 几个 T | **几个 T**（训练数据/参数规模） |
| token plan / coin plan | **token plan** / **Coding Plan** |
| 五小时限制、7 天限制 | **5 小时限制、7 天限制** |
| 视觉还原 / 开放能力 / 显像速的很快 | **视觉还原** / **开发能力** / **响应速度很快** |
| 后圈线水平 | **后训练水平** |
| 干掉一周的限额 | **干掉一周的限额** |
| 触顶 | **触顶** |
| 战斗 / 开发测 | **开发侧** |
| 空闲 / 生态 | **生态** |
| 开（到）50 万上下文 | **（开到）50 万上下文** |

## D. 存疑项（保留原文并加注，不下断言）

1. `ASTRA`（GPT-6 ASTRA）——两源一致，且不像误识别，**按 Astra 保留**。
2. `Fable 5 / Fable 5.1`——两源分别为 `fib5/FBL5.1`，均碎片化；音近 Fable，且语境为「比 Opus 5 更强」，**保留 "Fable" 但标注为听写推定**。
3. `千问 3.8 27B / 210B`——Whisper 作 `27B`，SRT 作 `2107B`。**标注为存疑**，正文写「小参数版本（听写作 27B）」。
4. `龙虾`——SRT 亦作「龙虾」，两源一致，但无法确定所指（可能是某工具/项目的昵称）。**原样保留 + 注**。
5. `美国大豆包`——SRT 作「美国大豆包煎饼袋」。**戏谑说法，原样保留 + 注**。
6. `GPT-20 倍`——SRT 作「GBT20倍」。语境为订阅套餐档位，**原样保留 + 注**。
7. `Codex 里配置了大量的子代理`——两源一致，非误识别。
