# 影视工作台（Film Studio）工作区

<!-- 本文件由 film-studio 插件的 /new-drama 建项时生成，是本工作区的创作规范 -->

这是一个 AI 影视创作工作区，支持三种创作形态：**短剧 / 电影短片 / 动漫番剧**。通过 film-studio 插件的 11 个影视专业 agent 和分阶段命令，完成从创意到平台发布的全流程：剧本 → 分镜 → 设定图 → 视频生成 → 配乐 → 审片 → 粗剪 → 剪映精剪（自动生成草稿）→ 平台发布。

## 创作形态（project.json 的 format.medium）

建项时选定，编剧/导演/美术/摄影/运营按形态自动切换法则：

| medium | 形态 | 创作法则要点 | 视觉基调 | 主发布平台 |
|---|---|---|---|---|
| `short-drama` | 短剧 | 黄金3秒、高反转密度、卡点钩子 | 写实、竖屏近景 | 抖音/快手 |
| `short-film` | 电影短片 | 三幕结构、视听叙事、留白 | 电影感、横屏、景别丰富 | B站/视频号 |
| `anime` | 动漫番剧 | 情绪峰值、内心独白、章节感 | 二次元画风（style-bible 锁定流派，逐字复用防漂移） | B站 + 抖音切片 |

老项目 project.json 无 medium 字段时默认 `short-drama`。

## 剪辑增强选项（project.json 的 editing 块，默认全关）

- `episode_overlap`（集间交叉衔接）：开启后每集开头重放上一集最后镜头的结尾几秒（默认 4s，
  存为 `sh00-recap.mp4`），方便观众衔接；第 1 集不适用
- `intro_outro`（片头/片尾）：开启后每集首尾加全剧复用的片名卡/引导卡（`projects/<片名>/assets/intro.mp4`、`outro.mp4`，
  首次启用时由剪辑师按 style-bible 风格生成）
- 两项在 `/new-drama` 建项时询问（默认不选）；中途想开关，直接让制片人改 project.json 即可；
  剪辑师（粗剪）与精剪师（精剪工程）都会读取此配置，开启片头时字幕时间轴相应偏移

## 创作流水线

```
/new-drama 建项 → /script 剧本 →【门禁① 剧本定稿】→ /storyboard 分镜 → /design 设定图
→【门禁② 设定图定稿】→ /shoot 视频生成 →【门禁③ 积分报价确认】→ /review 审片 → /edit 粗剪
→ /finalcut 剪映精剪（自动生成草稿，剪映中微调导出）→ /publish 发布 →【门禁④ 发布确认】
                                    /music 配乐（剧本定稿后即可并行，Suno 生成 BGM）
```

- 四个门禁必须得到用户明确确认才能通过，其余阶段自动推进。
- `/studio-status` 随时查看所有项目进度和即梦积分余额。
- 用户可以随时单独调用某个 agent 做局部修改（如"让编剧改第 3 集台词"），不必走完整流水线。

## Agent 团队

| Agent | 角色 | 职责 |
|---|---|---|
| producer | 制片人 | 建项、进度跟踪、积分预算、门禁把关 |
| screenwriter | 编剧 | 大纲、人物小传、分集剧本、台词（按形态切换创作法则） |
| director | 导演 | 分镜表：景别、运镜、时长、节奏（按形态调整镜头语言） |
| art-director | 美术指导 | 角色/场景设定图（Gemini 网页端），视觉一致性 |
| cinematographer | 摄影指导 | 分镜 → Seedance 2.0 提示词 → shotlist.json |
| video-generator | 视频生成师 | 按 shotlist 调 dreamina CLI 生成、轮询、下载 |
| composer | 配乐师 | Suno 网页端生成 BGM + 对位说明 |
| editor | 剪辑师 | ffmpeg 统一编码、粗剪拼接（保留原声）、精剪交付包 |
| finalcut | 精剪师 | pyJianYingDraft 自动生成剪映草稿：转场、BGM 对位、字幕轨、滤镜 |
| reviewer | 审片人 | 抽帧质检、一致性检查、回炉清单 |
| operator | 运营 | 发布文案、封面图、半自动发布抖音等平台（门禁④） |

## 生成引擎分工（按任务类型）

- **设定图**（角色三视图、场景概念图）→ Gemini 网页端 Nano Banana（`agent-browser` 浏览器自动化，省即梦积分）；不可用时降级 `dreamina text2image` 并告知用户。
  **Gemini 出图右下角有水印，入库前必须用 `tools/clean_refimg.py` 清理并肉眼复查**——带水印的参考图会被 Seedance 复刻进视频且无法补救；原始图放 `03-design/_raw/`，只有清理过的图才能进 `characters/`、`scenes/`
- **视频片段** → 即梦 `dreamina` CLI（Seedance 2.0 家族），**生成的视频自带声音（台词/音效），全流程必须保留音轨**：
  - 纯场景空镜 → `text2video`
  - 含角色镜头 → `multimodal2video`（引用角色设定图保证一致性，image≤9）
  - 精确控制首尾画面 → `frames2video`
  - **模型默认走 VIP 通道防排队**：常规镜头 `seedance2.0fast_vip`，重点镜头 `seedance2.0_vip`；
    非 VIP 通道（`seedance2.0fast`/`seedance2.0`）仅在用户明确要求省积分且不赶时间时用
- **背景音乐** → Suno 网页端（`agent-browser` 浏览器自动化）；BGM 是精剪素材，不混入粗剪
- **精剪** → 检测到 DaVinci Resolve Studio（**推荐**，官方 Python API，可自动渲染导出）则优先征询使用；
  否则默认 `pyJianYingDraft` 生成剪映草稿（不推销 Resolve），用户在剪映中微调导出
- **平台发布** → 抖音创作者中心等网页端（`agent-browser` 浏览器自动化，半自动：发布前门禁④确认）
- **文生文**（剧本/分镜/提示词/发布文案）→ Claude 本体
- Seedance 提示词写作规范见 `seedance-prompt-en` 技能

## 项目目录规范

```
projects/<片名>/
├── project.json           # 项目档案：创作形态(medium)、画幅、时长、集数、剪辑增强(editing)、各阶段状态
├── 01-script/             # outline.md, characters.md, ep01.md ...
├── 02-storyboard/         # ep01-storyboard.md ...
├── 03-design/             # characters/<角色>-*.png, scenes/<场景>-*.png, style-bible.md
├── 04-footage/ep01/       # shotlist.json + sh01.mp4 ... + ep01.srt + bgm/（Suno BGM + 对位说明）
├── 05-final/              # <剧名>-ep01-粗剪.mp4 + delivery-ep01.md + finalcut-ep01.md（精剪说明）
└── 06-publish/ep01/       # copy.md（发布文案）+ cover.png（封面）+ publish-log.md（发布记录）
```

- 镜头命名：`ep{两位集号}` / `sh{两位镜号}`，如 `04-footage/ep01/sh03.mp4`
- `project.json.status` 各阶段取值：`pending | in_progress | approved | done`
- `shotlist.json` 是摄影指导与视频生成师之间的交接件，也是生成日志（记录 submit_id、状态、产物路径），生成过程中必须实时更新

## 硬性安全规则

1. **未经门禁③确认，绝不提交任何消耗积分的视频生成任务。**
2. 每次提交生成任务后立即把 submit_id 写入 shotlist.json，防止任务丢失。
3. 生成失败自动重试仅 1 次，再失败停下报告，不得无限重试烧积分。
4. `/shoot` 前必须 `dreamina user_credit` 检查余额；首次生成后记录实际消耗，校准后续报价（积分单价不得凭空假设）。
5. 遇到 `AigcComplianceConfirmationRequired` 错误：停下，提示用户去即梦 Web 端完成内容安全授权后重试。
6. **未经门禁④确认，绝不点击任何平台的发布按钮**（含"确认定时发布"）；平台账号登录永远由用户本人完成。

## 交付边界

- `/edit` 粗剪：顺序硬切拼接、保留即梦原声、无字幕，快速预览用
- `/finalcut` 精剪：自动组装精剪工程（转场、BGM 对位、台词字幕、滤镜）——Resolve 路径可授权自动渲染成片；剪映路径**最终微调和导出由用户在剪映中完成**
- `/publish` 发布：文案 + 封面 + 半自动上传，发布点击前必须用户确认

## 环境（Windows / macOS 均支持）

- `dreamina` CLI 已登录（OAuth 设备流），`dreamina <子命令> -h` 查参数
- Gemini 网页端（设定图）、Suno 网页端（BGM）、抖音创作者中心（发布）需要浏览器已登录对应账号
- Python 3.8+：Windows 命令用 `python`，macOS 用 `python3`（下文 `python` 按此对应）
- `pyJianYingDraft`：`python -m pip install pyJianYingDraft`；剪映版本：5.9 草稿兼容最完整，≤6.8 支持自动导出（**仅 Windows**，macOS 需在剪映中手动导出），更新版本草稿加密支持有限
- （可选）DaVinci Resolve **Studio**：装了并运行时精剪走官方 API（外部脚本控制仅 Studio 版支持，免费版不行）；未装不影响任何流程
- 剪映草稿目录：Windows `%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft`；macOS `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft`
- `ffmpeg` 在 PATH 中（Windows: winget/scoop；macOS: `brew install ffmpeg`）；拼接用工作区 `tools/concat.py`（建项时由插件复制而来）
- 封面中文字体：Windows `C:/Windows/Fonts/msyhbd.ttc`；macOS `/System/Library/Fonts/PingFang.ttc`
- 路径含中文/空格时注意加引号；脚本示例统一用正斜杠路径（两平台通用）
