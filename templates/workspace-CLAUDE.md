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

## 整体视频风格（一次选定、全剧锁定）

建项时在 medium 之上再选一个**具体画风预设**（`project.json` 的 `format.style`），像小云雀那样定好整体风格后所有镜头/所有集保持一致。预设含写实都市 / 电影质感 / 韩剧清冷 / 港风复古 / 国风水墨 / 古装华丽 / 赛博朋克 / 2D手绘 / 3D卡通 / 油画厚涂 / 自定义（完整库见插件 `templates/style-presets.md`）。

- **机制**：选定预设的 **STYLE LOCK 英文关键词块**写进 `03-design/style-bible.md`（单一真源）；美术每条出图提示词、摄影每条视频提示词都**逐字前置** STYLE LOCK，精剪调色也按其"调色意图"选校验过的滤镜——三处合力锁风格。动漫的"锁定二次元流派"就是本机制的 `anime-2d` 预设
- **一致性边界**：含角色镜头靠 @引用设定图承载主要风格、STYLE LOCK 加固；`text2video` 空镜无图锚点，STYLE LOCK 是唯一载体（漂移风险最大，务必原样前置）。是"强一致"非逐帧像素级
- **改风格时机**：/design 出图前可自由改；出了设定图/视频再改＝那些产物作废重做（同画幅约束）。老项目无 `format.style` 按 medium 取默认

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
→【门禁② 设定图定稿】→ /shoot 视频生成 →【门禁③ 积分报价确认】→ /review 审片
→ /finalcut 精剪成片（剪映/达芬奇时间线，非破坏性、直接用原始片段）→ /publish 发布 →【门禁④ 发布确认】
                        /edit 粗剪预览（可选，快速看节奏）      /music 配乐（剧本定稿后即可并行）
```

- **成片走 `/finalcut`**（非破坏性，直接引用原始 sh*.mp4，最终只渲染一次，质量最好）。
  `/edit` 是可选的粗剪预览（无损拼接，仅供快速看节奏），不是成片；它还会输出给人工精剪的完整交付包。
- 四个门禁必须得到用户明确确认才能通过，其余阶段自动推进。
- `/studio-status` 随时查看所有项目进度和即梦积分余额。
- 用户可以随时单独调用某个 agent 做局部修改（如"让编剧改第 3 集台词"），不必走完整流水线。

## Agent 团队

| Agent | 角色 | 职责 |
|---|---|---|
| producer | 制片人 | 建项、进度跟踪、积分预算、门禁把关 |
| screenwriter | 编剧 | 大纲、人物小传、分集剧本、台词（短剧靠台词直给+内心独白叙事；逐句标 `【对白】/【独白】`，动漫另用 `【旁白】`） |
| director | 导演 | 分镜表：景别、运镜、时长、节奏；台词/音效列区分对白(同期)与内心独白(后期配音) |
| art-director | 美术指导 | 角色/场景设定图 + 首尾帧/多帧关键帧（Gemini 网页端）；维护 style-bible 风格锁，视觉一致性 |
| cinematographer | 摄影指导 | 分镜 → Seedance 2.0 提示词 → shotlist.json |
| video-generator | 视频生成师 | 按 shotlist 调 dreamina CLI 生成、轮询、下载 |
| composer | 配乐师 | Suno 网页端生成 BGM + 对位说明 |
| editor | 剪辑师 | ffmpeg 统一编码、粗剪拼接（保留原声）、精剪交付包 |
| finalcut | 精剪师 | pyJianYingDraft 自动生成剪映草稿：转场、BGM 对位、字幕轨、内心独白配音、滤镜 |
| reviewer | 审片人 | 抽帧质检、一致性检查、回炉清单 |
| operator | 运营 | 发布文案、封面图、半自动发布抖音等平台（门禁④） |

## 生成引擎分工（按任务类型）

- **设定图**（角色三视图、场景概念图）→ Gemini 网页端 Nano Banana（`agent-browser` 浏览器自动化，省即梦积分）；不可用时降级 `dreamina text2image` 并告知用户。
  **Gemini 出图右下角有水印，入库前必须用 `tools/clean_refimg.py` 清理并肉眼复查**——带水印的参考图会被 Seedance 复刻进视频且无法补救；原始图放 `03-design/_raw/`，只有清理过的图才能进 `characters/`、`scenes/`
- **视频片段** → 即梦 `dreamina` CLI（Seedance 2.0 家族）。**用满即梦能力：单次可 4-15 秒、可在一条提示词里用时间码切多节拍（导演切镜）、可多帧串连贯段落、可调分辨率——别把每个镜头都做成 4s 单动作短片**：
  - 即梦网页端功能名 ↔ CLI 模式：**全能参考=`multimodal2video`、智能多帧=`multiframe2video`、首尾帧=`frames2video`**
  - 纯场景空镜 → `text2video`
  - 含角色镜头（全能参考）→ `multimodal2video`（引用角色设定图保证一致性，image≤9；连续戏用 8-15s 长镜+时间码多节拍讲，一致性与原声都保住）
  - 精确控制首尾画面（首尾帧）→ `frames2video`；单图动起来/尾帧衔接 → `image2video`
  - 一段连续动作有 2-20 张关键帧图（智能多帧）→ `multiframe2video`（切镜插值成连贯段落，**静音、无模型/分辨率参数**，音轨由精剪补）
  - **关键帧来源**：首尾帧/智能多帧需要镜头专属关键帧（非角色/场景设定图）——由美术指导按 shotlist 的 `keyframes_needed` 用 Gemini 出图（省积分、走水印清理）落 `03-design/keyframes/`；衔接首帧由视频生成师用 ffmpeg 从上一镜抽尾帧
  - **分辨率**：`multimodal2video` 与整个 seedance2.0 家族封顶 **720p**；**1080p 只在 `image2video`/`frames2video` 的 3.5pro/3.0pro 上有，且放弃全能 @引用**——故 1080p 只给空镜/静物，反复出场角色一律留在 720p 的 multimodal 路线保一致性
  - **模型默认走 VIP 通道防排队**：常规镜头 `seedance2.0fast_vip`，重点镜头 `seedance2.0_vip`；
    非 VIP 通道（`seedance2.0fast`/`seedance2.0`）仅在用户明确要求省积分且不赶时间时用
  - **音轨**：multimodal/text/image/frames 系自带声音（台词/音效），全流程保留；`multiframe2video` 静音属正常，音轨在精剪阶段补齐——**全流程必须保留音轨，但静音由精剪补齐，不因缺音轨重生成烧积分**
- **背景音乐** → Suno 网页端（`agent-browser` 浏览器自动化）；BGM 是精剪素材，不混入粗剪
- **精剪** → 检测到 DaVinci Resolve Studio（**推荐**，官方 Python API，可自动渲染导出）则优先征询使用；
  否则默认 `pyJianYingDraft` 生成剪映草稿（不推销 Resolve），用户在剪映中微调导出
- **平台发布** → 抖音创作者中心等网页端（`agent-browser` 浏览器自动化，半自动：发布前门禁④确认）
- **文生文**（剧本/分镜/提示词/发布文案）→ Claude 本体
- Seedance 提示词写作规范见 `seedance-prompt-en` 技能

## 项目目录规范

```
projects/<片名>/
├── project.json           # 项目档案：创作形态(medium)、画风预设(style)、画幅、时长、集数、剪辑增强(editing)、各阶段状态
├── 01-script/             # outline.md, characters.md, ep01.md ...
├── 02-storyboard/         # ep01-storyboard.md ...
├── 03-design/             # characters/<角色>-*.png, scenes/<场景>-*.png, keyframes/ep{NN}-sh{NN}-*.png（首尾帧/多帧关键帧）, style-bible.md（含风格锁 STYLE LOCK，全剧风格单一真源）
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
3. 每个下载文件必须过可用性质检（ffprobe：完整性/时长/画幅/**音轨**），通过才置 `status=success`、才重命名为 `sh{NN}.mp4`——不轻信 CLI 的 success 状态。**音轨检查按 mode 判定**：静音模式（`multiframe2video`/标了 `silent` 的镜头）不要求音轨、缺音轨正常；自带音轨模式若缺音轨只记 warning 交精剪补音，**缺音轨绝不触发重生成烧积分**。
4. **重生成（烧积分）每镜最多 1 次**，再失败停下报告，不得无限重试烧积分；重下载（免费，修传输问题）不受此限。
5. `/shoot` 前必须 `dreamina user_credit` 检查余额；首次生成后记录实际消耗，校准后续报价（积分单价不得凭空假设）。
6. 遇到 `AigcComplianceConfirmationRequired` 错误：停下，提示用户去即梦 Web 端完成内容安全授权后重试。
7. **未经门禁④确认，绝不点击任何平台的发布按钮**（含"确认定时发布"）；平台账号登录永远由用户本人完成。

## 交付边界

- `/edit` 粗剪：顺序硬切拼接、保留即梦原声、无字幕，快速预览用
- `/finalcut` 精剪：自动组装精剪工程（转场、BGM 对位、台词字幕、内心独白字幕、滤镜）——Resolve 路径可授权自动渲染成片；剪映路径**最终微调和导出由用户在剪映中完成**。
  **内心独白配音**：对白用即梦原声、不重配；内心独白自动做字幕，声音走剪映「文本朗读」一键生成（这一步在剪映里人工点，脚本无法代触发）——不点则独白只有字幕没声音（动漫的旁白同此处理）
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
