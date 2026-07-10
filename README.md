# 短剧工作台（Short Drama Studio）

在 Claude Code 中完成短剧创作全流程的 AI 工作台：从一句话创意到成片——剧本 → 分镜 → 角色/场景设定图 → 视频生成 → 审片 → 剪辑成片。

由 8 个影视专业 agent 分工协作，通过分阶段 slash 命令推进，内置三道人工确认门禁防止积分误消耗。

## 环境要求

| 依赖 | 说明 | 验证方式 |
|---|---|---|
| `dreamina` CLI | 即梦官方 AIGC CLI，负责视频生成（Seedance 2.0） | `dreamina user_credit` 能返回余额即已登录；未登录先 `dreamina login` |
| Google 账号（Chrome 已登录） | 美术指导通过浏览器自动化操作 Gemini 网页端画设定图（不耗即梦积分） | 浏览器能正常打开 gemini.google.com 并对话 |
| `ffmpeg` / `ffprobe` | 本地转码与拼接 | `ffmpeg -version` |
| `agent-browser` | 浏览器自动化 CLI（Gemini 网页端自动化用） | `agent-browser --help` |

> 首次使用某些即梦视频模型可能返回 `AigcComplianceConfirmationRequired`，需先去即梦 Web 端完成一次内容安全授权。

## 快速开始

```
1. 在本目录启动 Claude Code（agents 和 skills 在会话启动时自动加载）
2. /new-drama        # 建项：选题材、画幅（9:16 / 16:9）、每集时长、集数
3. /script           # 剧本创作，迭代到你满意 →【门禁① 定稿确认】
4. /storyboard       # 剧本拆分镜表（镜号/景别/运镜/时长/画面/台词）
5. /design           # 角色三视图 + 场景设定图 →【门禁② 定稿确认】
6. /shoot            # 报积分预估 →【门禁③ 确认】→ 批量生成视频镜头
7. /review           # 抽帧质检，不合格镜头回炉（回 /shoot 重拍）
8. /edit             # ffmpeg 拼接成片，输出到 05-final/
```

随时可用 `/studio-status` 查看所有项目进度、积分余额，并收割挂起的生成任务。

**建议**：第一个项目先做 2-3 个镜头的迷你集，跑通流程并校准积分单价，再上正式剧集。

## 命令一览

| 命令 | 阶段 | 门禁 |
|---|---|---|
| `/new-drama` | 新建项目，生成标准目录和 project.json | - |
| `/script` | 大纲、人物小传、分集剧本 | ① 剧本定稿 |
| `/storyboard` | 分镜表 + 时长核算 | - |
| `/design` | 角色/场景设定图（Gemini 网页端优先） | ② 设定图定稿 |
| `/shoot` | 提示词 → 积分报价 → 批量生成 → 下载 | ③ 报价确认（唯一大额耗积分环节） |
| `/review` | 抽帧质检、一致性检查、回炉清单 | 回炉需再过门禁③ |
| `/edit` | 统一转码、拼接、输出成片 | - |
| `/studio-status` | 全项目进度 + 积分余额总览 | - |

## Agent 团队

| Agent | 角色 | 职责 |
|---|---|---|
| producer | 制片人 | 建项、进度、积分预算、门禁把关 |
| screenwriter | 编剧 | 大纲、人物小传、分集剧本（黄金3秒、反转密度等短剧法则） |
| director | 导演 | 分镜表：景别、运镜、时长、节奏，兼顾 AI 生成可行性 |
| art-director | 美术指导 | 设定图与全剧视觉一致性（style-bible） |
| cinematographer | 摄影指导 | 分镜 → Seedance 2.0 提示词 → shotlist.json |
| video-generator | 视频生成师 | 调 dreamina 提交/轮询/下载/重试，实时记账 |
| editor | 剪辑师 | ffmpeg 统一编码、拼接成片 |
| reviewer | 审片人 | 抽帧质检：畸变、角色一致性、连贯性 |

每个 agent 可单独调用，不必走完整流水线，例如：

- "让编剧把第 3 集结尾的反转改得更狠"
- "让审片人重新检查 ep01 的 sh05"
- "让剪辑师把 sh03 从成片里去掉重新拼"

## 生成引擎分工

- **设定图** → Gemini 网页端 Nano Banana（浏览器自动化，免积分）；不可用时降级 `dreamina text2image` 并明确告知
- **视频** → 即梦 Seedance 2.0：
  - 含角色镜头 → `multimodal2video`（引用角色设定图，保证跨镜头角色一致性）
  - 纯场景空镜 → `text2video`
  - 精确首尾画面 → `frames2video`
  - 默认 `seedance2.0fast`（性价比），重点镜头 `seedance2.0`（质量）
- **文生文**（剧本/分镜/提示词）→ Claude 本体

## 项目目录结构

```
projects/<剧名>/
├── project.json           # 项目档案：画幅、时长、集数、各阶段状态、积分消耗记录
├── 01-script/             # outline.md、characters.md、ep01.md ...
├── 02-storyboard/         # ep01-storyboard.md ...
├── 03-design/             # style-bible.md、characters/、scenes/
├── 04-footage/ep01/       # shotlist.json（任务清单兼生成日志）+ sh01.mp4 ...
└── 05-final/              # 成片 <剧名>-ep01.mp4
```

## 防烧钱机制

1. 未过门禁③确认，任何 agent 不得提交消耗积分的生成任务
2. 积分单价不凭空假设：首次建议只生成 1 镜校准单价，之后按实际消耗报价
3. 生成失败自动重试仅 1 次，绝不无限重试
4. 每个 submit_id 即时写入 shotlist.json，任务不丢失，中断后 `/studio-status` 可收割

## 范围说明

本工作台交付**无声成片**（画面 + 硬切剪辑）。配音、配乐、字幕建议在剪映 / Premiere 中完成。

## 仓库结构

```
CLAUDE.md                  # 工作台总规范（Claude Code 自动加载）
.claude/agents/            # 8 个专业 agent 定义
.claude/skills/            # 8 个阶段 slash 命令
tools/concat.ps1           # ffmpeg 统一转码 + 拼接脚本
docs/superpowers/specs/    # 设计文档
projects/                  # 你的短剧项目（视频产物不入 git）
```
