# 影视工作台（Film Studio）工作区

<!-- 本文件由 film-studio 插件的 /new-drama 建项时生成，是本工作区的创作规范 -->

这是一个 AI 影视创作工作区，支持四种创作形态：**短剧 / 电影短片 / 动漫番剧 / 创意段子**。通过 film-studio 插件的 12 个影视专业 agent 和分阶段命令，完成从创意到平台发布的全流程：剧本 → 分镜 →（白模预演）→ 设定图 → 视频生成 → 配乐 → 审片 → 粗剪 → 剪映精剪（自动生成草稿）→ 平台发布。

## 创作形态（project.json 的 format.medium）

建项时选定，编剧/导演/美术/摄影/运营按形态自动切换法则：

| medium | 形态 | 创作法则要点 | 视觉基调 | 主发布平台 |
|---|---|---|---|---|
| `short-drama` | 短剧 | 黄金3秒、高反转密度、卡点钩子 | 写实、竖屏近景 | 抖音/快手 |
| `short-film` | 电影短片 | 三幕结构、视听叙事、留白 | 电影感、横屏、景别丰富 | B站/视频号 |
| `anime` | 动漫番剧 | 情绪峰值、内心独白、章节感 | 二次元画风（style-bible 锁定流派，逐字复用防漂移） | B站 + 抖音切片 |
| `sketch` | 创意段子 | 黄金1秒抓梗、一条一个梗核翻三番、结尾反转/玩梗CTA | 真人日常感或卡通夸张，竖屏为主 | 抖音+B站双主打（话术按平台切：B站三连/抖音关注） |

老项目 project.json 无 medium 字段时默认 `short-drama`。

**sketch 的结构语义**：「集」即「条」——每条剧情独立成篇可乱序看，但角色/人设全项目共用（一个项目=一个账号人设宇宙，设定图设计一次全部复用）。

## 商单机制（sponsor brief，与形态解耦——段子最常用，任何形态可用）

某条接了品牌推广时：brief（产品/卖点/口播词/禁忌）落 `01-script/ep{NN}-sponsor.md`（单一真源），
project.json 的 `sponsors.ep{NN}` 记品牌名与状态摘要（`briefed → script_ok → published`）。无商单的条=纯涨粉内容，零负担。

- **植入方式（剧本级两式）**：神转折（默认，整条铺垫到广告揭晓、广告即包袱）/ 明示口播（人物自嘲式对镜头念广告）；由编剧写进剧本走正常管线
- **门禁扩展（不加新门禁）**：门禁①定稿需商单核对单（卖点覆盖/口播词逐字/禁忌零出现）+ 提醒品牌方过稿；门禁④发布需确认平台商单报备（星图/花火）+ 文案广告声明，未确认不发布
- **产品外观必须图锚定**：向用户要产品官方图（清水印后存 `03-design/props/`），产品露出镜头 @引用它——纯文字描述产品必走样
- **边界**：接单/谈价/结算在星图/花火平台与线下完成，工作台只管内容侧（详见插件仓库 ADR-0002）

## 整体视频风格（一次选定、全剧锁定）

建项时在 medium 之上再选一个**具体画风预设**（`project.json` 的 `format.style`），像小云雀那样定好整体风格后所有镜头/所有集保持一致。预设库按 **真人 / 2D / 3D** 三类组织、十余个可选（国产都市写实、韩剧都市柔光、日式生活自然、90年代写实电影、美式复古好莱坞、武侠江湖写实、霓虹赛博、2D手绘、3D卡通…）+ 自定义——**完整清单以插件 `templates/style-presets.md` 为准**（会随需扩充，此处不逐一枚举以免过时）。

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
        /previz 白模预演（可选，分镜后；锁复杂运镜，不耗积分）
        /edit 粗剪预览（可选，快速看节奏）      /music 配乐（剧本定稿后即可并行）
```

- **成片走 `/finalcut`**（非破坏性，直接引用原始 sh*.mp4，最终只渲染一次，质量最好）。
  `/edit` 是可选的粗剪预览（无损拼接，仅供快速看节奏），不是成片；它还会输出给人工精剪的完整交付包。
- 四个门禁必须得到用户明确确认才能通过，其余阶段自动推进。商单条在门禁①④各多一组检查项（商单核对单 / 报备+广告声明），不新增门禁。
- `/studio-status` 随时查看所有项目进度和即梦积分余额；需要图形化观测可另装独立仪表盘
  [film-studio-dashboard](https://github.com/zq940222/film-studio-dashboard)（本地 web 应用，选定本工作区目录即可只读观测，不影响流程与门禁）。
- 用户可以随时单独调用某个 agent 做局部修改（如"让编剧改第 3 集台词"），不必走完整流水线。

## Agent 团队

| Agent | 角色 | 职责 |
|---|---|---|
| producer | 制片人 | 建项、进度跟踪、积分预算、门禁把关 |
| screenwriter | 编剧 | 大纲、人物小传、分集剧本、台词（短剧靠台词直给+内心独白叙事；逐句标 `【对白】/【独白】`，动漫另用 `【旁白】`）；商单条按 brief 做神转折/口播植入并附商单核对单 |
| director | 导演 | 分镜表：景别、运镜、时长、节奏；台词/音效列区分对白(同期)与内心独白(后期配音)；复杂运镜可标 `【白模】` 交预演 |
| previz-artist | 白模师 | Blender 白模预演（可选）：给复杂运镜/精确空间/走位的镜头搭灰白代理场景+相机动画，渲成运镜参考视频 |
| art-director | 美术指导 | 角色/场景设定图 + 首尾帧/多帧关键帧（Gemini 网页端）；维护 style-bible 风格锁，视觉一致性 |
| cinematographer | 摄影指导 | 分镜 → Seedance 2.0 提示词 → shotlist.json；回炉时按审片反馈修订提示词（prompt_history 追溯） |
| video-generator | 视频生成师 | 按 shotlist 调 dreamina CLI 生成、轮询、下载 |
| composer | 配乐师 | Suno 网页端生成 BGM + 对位说明 |
| editor | 剪辑师 | ffmpeg 统一编码、粗剪拼接（保留原声）、精剪交付包 |
| finalcut | 精剪师 | pyJianYingDraft 自动生成剪映草稿：转场、BGM 对位、字幕轨、内心独白配音、滤镜 |
| reviewer | 审片人 | 抽帧质检、一致性检查、互动审片（人工反馈优先、落 rework_reasons）、回炉清单；商单条核对产品外观/口播词/禁忌 |
| operator | 运营 | 发布文案、封面图、半自动发布抖音等平台（门禁④）；互动话术按平台切（B站三连/抖音关注）；商单条查报备+广告声明 |

## 生成引擎分工（按任务类型）

### 降级链（单一真源；每种能力主用不可用时按序往下走）

| 能力 | 主用 | 备用 | 兜底 |
|---|---|---|---|
| 设定图 `image` | Gemini 网页端 Nano Banana（免积分） | `dreamina text2image`（**耗积分**，必须告知用户） | 停下，请用户自备参考图 |
| 视频 `video` | 即梦 Seedance 2.0（`dreamina` CLI） | **无备选** | 停下告知用户 |
| 配乐 `music` | Suno 网页端 | 用户自备 BGM（放进 `04-footage/ep{NN}/bgm/`） | 无 BGM 交付，精剪留空音轨 |
| 精剪 `nle` | DaVinci Resolve Studio（检测到才用） | 剪映草稿（`pyJianYingDraft`，默认路径） | `/edit` 人工精剪交付包 |
| 发布 `publish` | 抖音创作者中心网页端 | 手动上传（交付文案+封面+成片路径给用户） | — |

**降级的三条硬规则**：

1. **只有"主用不可用"才降级**——未登录、被风控、网页改版、CLI 报错、依赖缺失、连续 2 次失败。
   慢、麻烦、要多点几下**都不是**降级理由
2. **每次降级必须一句话告知用户**：降到了什么、代价是什么（耗积分／画质／一致性／要手动）、怎么恢复主用。
   静默降级是本工作台最不能接受的行为——用户会以为拿到的是主用路径的质量
3. **视频生成没有备选，不可用就停下**。风格锁、角色一致性、原声音轨全部建立在 Seedance 上，
   中途换引擎等于整片重做——宁可停在这里等，也不要换

想固化偏好（例如"设定图别用 Gemini，直接即梦"），让制片人写进 `project.json` 的 `providers` 块，
格式 `{"image": {"primary": "dreamina-text2image", "fallback": []}}`，之后不再每集重问。

### 各能力细则

- **设定图**（角色三视图、场景概念图）→ Gemini 网页端 Nano Banana（`agent-browser` 浏览器自动化，省即梦积分）；不可用时降级 `dreamina text2image` 并告知用户。
  **Gemini 出图右下角有水印，入库前必须用 `tools/clean_refimg.py` 清理并肉眼复查**——带水印的参考图会被 Seedance 复刻进视频且无法补救；原始图放 `03-design/_raw/`，只有清理过的图才能进 `characters/`、`scenes/`
- **视频片段** → 即梦 `dreamina` CLI（Seedance 2.0 家族）。**用满即梦能力：单次可 4-15 秒、可在一条提示词里用时间码切多节拍（导演切镜）、可多帧串连贯段落、可调分辨率——别把每个镜头都做成 4s 单动作短片**。
  **两级切镜都要规划**：片段内部靠时间码多节拍（≥8s 镜头必须多节拍+显式切镜动词，标【一镜到底】才显式禁切）；
  片段之间靠分镜表"衔接"列（定场/动接动/景别跳变/视线引导/无缝衔接/转场…），摄影译进提示词与 `transition_in`、审片查执行、精剪定转场：
  - 即梦网页端功能名 ↔ CLI 模式：**全能参考=`multimodal2video`、智能多帧=`multiframe2video`、首尾帧=`frames2video`**
  - 纯场景空镜 → `text2video`
  - 含角色镜头（全能参考）→ `multimodal2video`（引用角色设定图保证一致性，image≤9；连续戏用 8-15s 长镜+时间码多节拍讲，一致性与原声都保住）
  - **复杂运镜/精确空间/明确走位/一镜到底调度** → `multimodal2video` + `--video` 白模参考（先走 `/previz` 出白模）：
    运镜由白模硬控制而非文字描述；提示词必须写**三句式**（复刻句/分工句/**禁灰面句**），漏禁灰面句会把 3D 灰模质感复刻进成片
  - 精确控制首尾画面（首尾帧）→ `frames2video`；单图动起来/尾帧衔接 → `image2video`
  - 一段连续动作有 2-20 张关键帧图（智能多帧）→ `multiframe2video`（切镜插值成连贯段落，**静音、无模型/分辨率参数**，音轨由精剪补）
  - **关键帧来源**：首尾帧/智能多帧需要镜头专属关键帧（非角色/场景设定图）——由美术指导按 shotlist 的 `keyframes_needed` 用 Gemini 出图（省积分、走水印清理）落 `03-design/keyframes/`；衔接首帧由视频生成师用 ffmpeg 从上一镜抽尾帧
  - **分辨率**：`multimodal2video` 与整个 seedance2.0 家族封顶 **720p**；**1080p 只在 `image2video`/`frames2video` 的 3.5pro/3.0pro 上有，且放弃全能 @引用**——故 1080p 只给空镜/静物，反复出场角色一律留在 720p 的 multimodal 路线保一致性
  - **模型默认走 VIP 通道防排队**：常规镜头 `seedance2.0fast_vip`，重点镜头 `seedance2.0_vip`；
    非 VIP 通道（`seedance2.0fast`/`seedance2.0`）仅在用户明确要求省积分且不赶时间时用
  - **音轨**：multimodal/text/image/frames 系自带声音（台词/音效），全流程保留；`multiframe2video` 静音属正常，音轨在精剪阶段补齐——**全流程必须保留音轨，但静音由精剪补齐，不因缺音轨重生成烧积分**
- **白模预演**（可选，`/previz`）→ 本地 **Blender**（`tools/blender_blockout.py` 按 `blockout.json` 搭灰白代理场景+相机动画，
  Workbench 渲帧、ffmpeg 封装）。**零即梦积分**；产物 `03-previz/ep{NN}/sh{NN}-blockout.mp4` 必须与该镜**同画幅、同时长**，
  只锁运镜/空间/走位、不锁风格。没装 Blender 就跳过，不影响其余流程
- **背景音乐** → Suno 网页端（`agent-browser` 浏览器自动化）；BGM 是精剪素材，不混入粗剪
- **精剪** → 检测到 DaVinci Resolve Studio（**推荐**，官方 Python API，可自动渲染导出）则优先征询使用；
  否则默认 `pyJianYingDraft` 生成剪映草稿（不推销 Resolve），用户在剪映中微调导出
- **平台发布** → 抖音创作者中心等网页端（`agent-browser` 浏览器自动化，半自动：发布前门禁④确认）
- **文生文**（剧本/分镜/提示词/发布文案）→ Claude 本体
## 内置规范技能（agent 开工前加载，你也可以直接问）

| 技能 | 内容 | 谁在用 |
|---|---|---|
| `seedance-prompt` | @引用役割语法、时间码切镜专章、运镜/景别中英对照、白模三句式 | 摄影指导、白模师 |
| `edit-rhythm` | 四形态平均镜长基准、开场黄金时间、切点选择、节奏曲线、转场取舍、`transition_in` 对应表 | 导演、剪辑师、精剪师、审片人 |
| `sound-design` | 三层音轨分工、响度与 ducking 目标、音效时机与音桥、即梦原声的三个坑 | 配乐师、精剪师、审片人 |
| `subtitle-craft` | **竖屏字幕安全区**（防被平台 UI 遮挡）、字号行数、按气口断句、驻留时长、SRT 写法 | 精剪师、审片人 |

**节奏在分镜阶段就定死了**（镜头长度提交生成时即固定，剪辑救不回来）——所以 `edit-rhythm` 的主要读者是导演，
不是剪辑师。节奏不对要回 `/storyboard` 改再重拍，不是在时间线上硬凑。

## 项目目录规范

```
projects/<片名>/
├── project.json           # 项目档案：创作形态(medium)、画风预设(style)、画幅、时长、集数、剪辑增强(editing)、商单摘要(sponsors，可选)、各阶段状态
├── 01-script/             # outline.md, characters.md, ep01.md ...（商单条另有 ep{NN}-sponsor.md 商单 brief）
├── 02-storyboard/         # ep01-storyboard.md ...
├── 03-design/             # characters/<角色>-*.png, scenes/<场景>-*.png, keyframes/ep{NN}-sh{NN}-*.png（首尾帧/多帧关键帧）, props/<产品名>.png（商单产品官方图）, style-bible.md（含风格锁 STYLE LOCK，全剧风格单一真源）
├── 03-previz/ep01/        # （可选）blockout.json 白模规格 + sh{NN}-blockout.mp4 白模参考视频 + previz-report.md
├── 04-footage/ep01/       # shotlist.json + sh01.mp4 ... + ep01.srt + bgm/（Suno BGM + 对位说明）
├── 05-final/              # <剧名>-ep01-粗剪.mp4 + delivery-ep01.md + finalcut-ep01.md（精剪说明）
├── 06-publish/ep01/       # copy.md（发布文案）+ cover.png（封面）+ publish-log.md（发布记录）
└── history/gates.jsonl    # 门禁确认留痕（只追加，一行一条 JSON）
```

- 镜头命名：`ep{两位集号}` / `sh{两位镜号}`，如 `04-footage/ep01/sh03.mp4`
- `project.json.status` 各阶段取值：`pending | in_progress | approved | done`；可选的 `status.previz` 另有 `skipped`（跳过白模，不影响流程）
- `03-*` 是"视觉预备"层：设定图 `03-design/` 与白模预演 `03-previz/` 并列同层（白模是可选阶段产物）
- `shotlist.json` 是摄影指导与视频生成师之间的交接件，也是生成日志（记录 submit_id、状态、产物路径），生成过程中必须实时更新
- `project.json` 的 `ledger` 是**积分账本**：`entries` 只追加不改写，四种流水 `estimate`（门禁③报价）→
  `reserve`（用户确认后预留）→ `actual`（实测核销，唯一影响 `credits.spent` 的一项）→ `release`（预留没用完的释放）；
  `unit_price` 记实测均价与可信度，**`confidence` 是 `unknown` 时不许凭空报单价**
- `history/gates.jsonl` 是**门禁留痕**（只追加）：每次门禁获确认追加一行
  `{"ts":"...","gate":"3","stage":"footage","action":"approved","detail":"ep01 4 镜，预留 400 积分"}`。
  会话中断、换机器、隔几天回来时，凭它 + shotlist 的实时状态就能回答"哪些门禁过了、哪批积分预留过、
  生成推进到哪一镜"——**不必重问用户，也不会重复付一次积分**

### 档案校验（改完 project.json / shotlist.json 随手跑一次）

```bash
python tools/validate_project.py                  # 全部项目
python tools/validate_project.py projects/<片名>   # 单个项目
```

（Windows 用 `python`，macOS 用 `python3`。零第三方依赖。）
它把下面「硬性安全规则」里几条最贵的变成机器可查：画幅与 project.json 不一致、
引用了 `_raw/` 里未清水印的图、白模与该镜时长/画幅对不上、`submitted` 却没有 submit_id、
**没过门禁就进了生成阶段**、账本与 `credits.spent` 对不上。
**`/shoot` 提交生成前必须跑一次且零 ERROR。**

## 硬性安全规则

1. **未经门禁③确认，绝不提交任何消耗积分的视频生成任务。**
2. 每次提交生成任务后立即把 submit_id 写入 shotlist.json，防止任务丢失。
3. 每个下载文件必须过可用性质检（ffprobe：完整性/时长/画幅/**音轨**），通过才置 `status=success`、才重命名为 `sh{NN}.mp4`——不轻信 CLI 的 success 状态。**音轨检查按 mode 判定**：静音模式（`multiframe2video`/标了 `silent` 的镜头）不要求音轨、缺音轨正常；自带音轨模式若缺音轨只记 warning 交精剪补音，**缺音轨绝不触发重生成烧积分**。
4. **重生成（烧积分）每镜最多 1 次**，再失败停下报告，不得无限重试烧积分；重下载（免费，修传输问题）不受此限。
5. `/shoot` 前必须 `dreamina user_credit` 检查余额；首次生成后记录实际消耗，校准后续报价（积分单价不得凭空假设）。
6. 遇到 `AigcComplianceConfirmationRequired` 错误：停下，提示用户去即梦 Web 端完成内容安全授权后重试。
7. **未经门禁④确认，绝不点击任何平台的发布按钮**（含"确认定时发布"）；平台账号登录永远由用户本人完成。
8. **白模必须与该镜同画幅、同时长**，否则不许提交生成（照错白模生成必错）——重渲白模免费，重生成烧积分；
   白模提示词的**禁灰面句不可省**（漏了会把 3D 灰模质感复刻进成片，属必回炉的双倍浪费）。
9. **提交生成前必须跑 `python tools/validate_project.py projects/<片名>` 且零 ERROR**（免费、几秒钟）——
   上面第 3、8 条和门禁顺序它都查；机器查一遍比烧完积分才发现便宜得多。
10. **降级必须告知**：任何能力走了备用路径（设定图降级到即梦、配乐降级到自备/无 BGM、发布降级到手动上传），
    都要一句话告诉用户降到了什么、代价是什么。**静默降级是本工作台最不能接受的行为**；
    视频生成没有备选，即梦不可用就停下，绝不换引擎。

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
- （可选）**Blender 3.6+**（[blender.org](https://www.blender.org)，免费）：只有 `/previz` 白模预演用到，未装不影响任何其他流程。
  Blender 自带 Python，无需装包；不在 PATH 时用完整路径调用——
  Windows `"C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"`、macOS `/Applications/Blender.app/Contents/MacOS/Blender`
- （可选）DaVinci Resolve **Studio**：装了并运行时精剪走官方 API（外部脚本控制仅 Studio 版支持，免费版不行）；未装不影响任何流程
- 剪映草稿目录：Windows `%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft`；macOS `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft`
- `ffmpeg` 在 PATH 中（Windows: winget/scoop；macOS: `brew install ffmpeg`）；拼接用工作区 `tools/concat.py`（建项时由插件复制而来）
- 封面中文字体：Windows `C:/Windows/Fonts/msyhbd.ttc`；macOS `/System/Library/Fonts/PingFang.ttc`
- 路径含中文/空格时注意加引号；脚本示例统一用正斜杠路径（两平台通用）
