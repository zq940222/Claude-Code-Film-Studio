# 影视工作台（Film Studio）

**中文** | [English](README.en.md)

![version](https://img.shields.io/badge/version-2.1.0-blue) ![platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Windows%20%7C%20macOS-lightgrey)

在 Claude Code 中完成影视创作全流程的 AI 工作台，支持三种创作形态：**短剧 / 电影短片 / 动漫番剧**。从一句话创意到平台发布——剧本 → 分镜 → 角色/场景设定图 → 视频生成 → 配乐 → 审片 → 粗剪 → 剪映精剪（自动生成草稿）→ 平台发布。

由 11 个影视专业 agent 分工协作（编剧/导演/美术/摄影/运营按创作形态自动切换法则），通过分阶段 slash 命令推进，内置四道人工确认门禁（防止积分误消耗和误发布）。

> 本项目原名 short-drama-studio（短剧工作台），v2.0.0 起更名 film-studio 并扩展为多形态；旧仓库地址自动重定向。

## 安装（Claude Code 插件）

本仓库是标准 Claude Code 插件（自托管 marketplace），命令行两步安装：

```bash
claude plugin marketplace add zq940222/Claude-Code-Film-Studio
claude plugin install film-studio@film-studio
```

或在 Claude Code 会话内：

```
/plugin marketplace add zq940222/Claude-Code-Film-Studio
/plugin install film-studio@film-studio
```

安装后重启会话生效。默认装到用户级（所有目录可用）；只想在某个项目用加 `--scope project`。

- **更新**：`claude plugin update film-studio`（新版本发布后）
- **卸载**：`claude plugin uninstall film-studio`
- **锁定版本**：`claude plugin marketplace add zq940222/Claude-Code-Film-Studio@v2.0.0`
- **从旧版迁移**（装过 short-drama-studio 的）：`claude plugin marketplace update short-drama-studio` 后按提示走 renames 迁移；或直接卸载旧插件、按上面命令重装

安装后在**任意工作目录**运行 `/new-drama`：首次会自动初始化工作区（复制创作规范 CLAUDE.md 和工具脚本），然后建项开拍。命令带插件命名空间时写作 `/film-studio:new-drama`，无重名时直接 `/new-drama` 即可。

## 环境要求

| 依赖 | 说明 | 验证方式 |
|---|---|---|
| `dreamina` CLI | 即梦官方 AIGC CLI，负责视频生成（Seedance 2.0） | `dreamina user_credit` 能返回余额即已登录；未登录先 `dreamina login` |
| Google 账号（Chrome 已登录） | 美术指导通过浏览器自动化操作 Gemini 网页端画设定图（不耗即梦积分） | 浏览器能正常打开 gemini.google.com 并对话 |
| Suno 账号（浏览器已登录） | 配乐师通过浏览器自动化操作 Suno 网页端生成背景音乐 | 浏览器能正常打开 suno.com/create 并生成 |
| 剪映（JianyingPro，Windows/macOS 均可） | 精剪师自动生成剪映草稿；5.9 草稿兼容最完整，≤6.8 支持自动导出（仅 Windows；macOS 手动导出），新版草稿加密支持有限 | 本机已安装剪映，能打开草稿 |
| Python 3.8+ 与 `pyJianYingDraft` | 剪映草稿生成 + 跨平台工具脚本（Windows 命令用 `python`，macOS 用 `python3`） | `python -c "import pyJianYingDraft"` 不报错（`python -m pip install pyJianYingDraft`） |
| 抖音创作者中心（浏览器已登录） | 运营 agent 半自动发布（发布前必经用户确认） | 浏览器能打开 creator.douyin.com 且已登录 |
| （可选）DaVinci Resolve Studio | 精剪推荐路径：官方 Python API 自动建时间线 + 自动渲染导出；外部脚本控制仅 Studio 付费版支持，未装则精剪走剪映 | Resolve 运行中且 `import DaVinciResolveScript` 可连接 |
| `ffmpeg` / `ffprobe` | 本地转码与拼接（Windows: winget/scoop；macOS: `brew install ffmpeg`） | `ffmpeg -version` |
| `agent-browser` | 浏览器自动化 CLI（Gemini 设定图 / Suno 配乐 / 抖音发布均依赖） | `agent-browser --help` |

> 首次使用某些即梦视频模型可能返回 `AigcComplianceConfirmationRequired`，需先去即梦 Web 端完成一次内容安全授权。

## 快速开始

```
1. 安装插件后，在任意工作目录启动 Claude Code
2. /new-drama        # 首次自动初始化工作区，然后建项：选创作形态（短剧/电影短片/动漫番剧）、题材、画幅、每集时长、集数
3. /script           # 剧本创作，迭代到你满意 →【门禁① 定稿确认】
4. /storyboard       # 剧本拆分镜表（镜号/景别/运镜/时长/画面/台词）
5. /design           # 角色三视图 + 场景设定图 →【门禁② 定稿确认】
6. /shoot            # 报积分预估 →【门禁③ 确认】→ 批量生成视频镜头（即梦视频自带声音）
7. /music            # Suno 生成背景音乐（剧本定稿后即可做，可与生成/审片并行）
8. /review           # 抽帧质检，不合格镜头回炉（回 /shoot 重拍）
9. /edit             # ffmpeg 粗剪（保留原声），快速预览节奏
10. /finalcut        # 自动生成剪映草稿：转场+BGM对位+台词字幕+滤镜 → 剪映中微调导出
11. /publish         # 发布文案+封面 → 半自动上传抖音 →【门禁④ 确认】→ 发布
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
| `/music` | Suno 网页端生成 BGM + 对位说明 | - |
| `/review` | 抽帧质检、一致性检查、回炉清单 | 回炉需再过门禁③ |
| `/edit` | 统一转码、粗剪拼接（保留原声）、精剪交付包 | - |
| `/finalcut` | 自动组装精剪工程：Resolve Studio（推荐，可自动渲染）或剪映草稿（默认） | - |
| `/publish` | 发布文案、封面图、半自动发布抖音等平台 | ④ 发布前确认 |
| `/studio-status` | 全项目进度 + 积分余额总览 | - |

## Agent 团队

| Agent | 角色 | 职责 |
|---|---|---|
| producer | 制片人 | 建项、进度、积分预算、门禁把关 |
| screenwriter | 编剧 | 大纲、人物小传、分集剧本（按形态切换：短剧法则/电影叙事/动漫章节感） |
| director | 导演 | 分镜表：景别、运镜、时长、节奏（按形态调整镜头语言），兼顾 AI 生成可行性 |
| art-director | 美术指导 | 设定图与全片视觉一致性（style-bible，动漫形态锁定画风流派） |
| cinematographer | 摄影指导 | 分镜 → Seedance 2.0 提示词 → shotlist.json |
| video-generator | 视频生成师 | 调 dreamina 提交/轮询/下载/重试，实时记账 |
| composer | 配乐师 | Suno 网页端生成 BGM、对位说明 |
| editor | 剪辑师 | ffmpeg 统一编码、粗剪拼接（保留原声）、精剪交付包 |
| finalcut | 精剪师 | 自动组装精剪工程（Resolve API 或剪映草稿）：转场、BGM 对位、字幕轨、滤镜 |
| reviewer | 审片人 | 抽帧质检：畸变、角色一致性、连贯性 |
| operator | 运营 | 发布文案、封面图、半自动发布（抖音/快手/视频号） |

每个 agent 可单独调用，不必走完整流水线，例如：

- "让编剧把第 3 集结尾的反转改得更狠"
- "让审片人重新检查 ep01 的 sh05"
- "让剪辑师把 sh03 从成片里去掉重新拼"
- "让精剪师把 ep01 的字幕字号调大重新出草稿"
- "让运营重新写 3 个更炸的标题"

## 生成引擎分工

- **设定图** → Gemini 网页端 Nano Banana（浏览器自动化，免积分）；不可用时降级 `dreamina text2image` 并明确告知。
  Gemini 出图右下角有水印，入库前自动用 `tools/clean_refimg.py` 清理并复查，避免水印被 Seedance 复刻进视频
- **视频** → 即梦 Seedance 2.0（生成的视频**自带声音**：台词/音效，全流程保留音轨）：
  - 含角色镜头 → `multimodal2video`（引用角色设定图，保证跨镜头角色一致性）
  - 纯场景空镜 → `text2video`
  - 精确首尾画面 → `frames2video`
  - 默认走 VIP 通道防排队：常规镜头 `seedance2.0fast_vip`，重点镜头 `seedance2.0_vip`；不赶时间想省积分可退回非 VIP 通道
- **背景音乐** → Suno 网页端（浏览器自动化）；BGM 作为独立素材交付，不混入粗剪
- **精剪** → 双路径：检测到 **DaVinci Resolve Studio**（推荐）走官方 Python API 建时间线、可自动渲染导出；
  否则默认 `pyJianYingDraft` 生成剪映草稿（转场/BGM 对位/字幕轨/滤镜），剪映中微调导出——没装 Resolve 不影响任何流程
- **平台发布** → 抖音创作者中心等网页端（浏览器自动化，发布前门禁④确认）
- **文生文**（剧本/分镜/提示词/发布文案）→ Claude 本体

## 项目目录结构

```
projects/<片名>/
├── project.json           # 项目档案：创作形态(medium)、画幅、时长、集数、各阶段状态、积分消耗记录
├── 01-script/             # outline.md、characters.md、ep01.md ...
├── 02-storyboard/         # ep01-storyboard.md ...
├── 03-design/             # style-bible.md、characters/、scenes/
├── 04-footage/ep01/       # shotlist.json（任务清单兼生成日志）+ sh01.mp4 ... + ep01.srt + bgm/
├── 05-final/              # <剧名>-ep01-粗剪.mp4 + delivery-ep01.md + finalcut-ep01.md（精剪说明）
└── 06-publish/ep01/       # copy.md（发布文案）+ cover.png（封面）+ publish-log.md（发布记录）
```

## 防烧钱机制

1. 未过门禁③确认，任何 agent 不得提交消耗积分的生成任务
2. 积分单价不凭空假设：首次建议只生成 1 镜校准单价，之后按实际消耗报价
3. 生成失败自动重试仅 1 次，绝不无限重试
4. 每个 submit_id 即时写入 shotlist.json，任务不丢失，中断后 `/studio-status` 可收割

## 范围说明（交付边界）

- ✅ 粗剪预览（`/edit`）：顺序硬切拼接，**保留即梦原声（台词/音效）**，快速看节奏
- ✅ 精剪工程（`/finalcut`）：自动组装转场、BGM 对位、台词字幕轨、滤镜/调色建议——
  Resolve 路径确认时间线后可**授权自动渲染成片**；剪映路径打开草稿微调（常见微调点：转场、字幕断句、BGM 音量）后**由用户导出**
- ✅ 发布物料与半自动发布（`/publish`）：候选标题、话题标签、封面图、上传填单，**点击发布前必经确认**
- ✅ 可选剪辑增强（**默认全关**，建项时选或随时让制片人开）：集间交叉衔接（每集开头重放上集结尾几秒）、片头/片尾卡（全剧复用的片名卡/引导卡）
- ❌ 剪映账号 VIP 素材、平台登录操作 → 永远由用户本人完成

### 四道门禁

| 门禁 | 位置 | 保护什么 |
|---|---|---|
| ① 剧本定稿 | /script 末尾 | 后续所有阶段的返工成本 |
| ② 设定图定稿 | /design 末尾 | 成片角色一致性 |
| ③ 积分报价确认 | /shoot 生成前 | 即梦积分（唯一大额消耗点） |
| ④ 发布确认 | /publish 点击发布前 | 对外发布不可撤回 |

## 仓库结构

```
.claude-plugin/            # 插件 manifest + 自托管 marketplace
agents/                    # 11 个专业 agent 定义
skills/                    # 11 个阶段 slash 命令
templates/                 # 工作区规范模板（/new-drama 建项时复制为工作区 CLAUDE.md）
tools/                     # concat.py（转码拼接）+ clean_refimg.py（水印清理），跨平台，建项时复制进工作区
VERSION / CHANGELOG.md     # 版本号与更新日志
requirements.txt           # Python 依赖（pyJianYingDraft）
docs/superpowers/specs/    # 设计文档（含修订记录）
```

## 版本管理

工作台遵循[语义化版本](https://semver.org/lang/zh-CN/)（详见 [CHANGELOG.md](CHANGELOG.md)）：
主版本号 = 不兼容的流程/目录变更；次版本号 = 新增 agent/命令/能力；修订号 = 修复与文档。
每个版本都有对应的 git tag（`v1.0.0`、`v1.1.0`…）。插件用户升级：`claude plugin update film-studio`；
需要锁定旧版本时用 `claude plugin marketplace add <repo>@v<版本>`。
