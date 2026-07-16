# 更新日志

## [2.8.0] - 2026-07-16

### 新增（风格化提示词——一次选定整体画风、全剧锁定，对标小云雀）
像小云雀（剪映/字节的 Seedance 2.0 短剧 Agent，支持 2D手绘/3D卡通/仿真真人）那样，建项时先定"整体视频风格"，之后所有镜头、所有集保持一致。
- **新增风格预设库 `templates/style-presets.md`**：~10 个命名预设——写实都市 / 电影质感 / 韩剧清冷 / 港风复古 /
  国风水墨 / 古装华丽 / 赛博朋克 / 2D手绘 / 3D卡通 / 油画厚涂 + 自定义；每个含一段 **STYLE LOCK 英文关键词块**、
  适用形态、调色意图。（预设是关键词+设定图画风实现，Seedance 无风格模型开关）
- **风格锁机制（单一真源 = style-bible.md）**：`/new-drama` 建项时按选定 `format.style` 把该预设的 STYLE LOCK 块
  **逐字**写进 `03-design/style-bible.md`；此后 **agent 只读 style-bible.md**（不读插件预设库，遵守"agent 不知插件根"）：
  - `art-director` 保留 STYLE LOCK 逐字、在其下补锚点，**每条出图提示词以 STYLE LOCK 开头**（设定图自带选定画风）
  - `cinematographer` **每条视频提示词逐字前置 STYLE LOCK**（`text2video` 空镜无图锚点时它是唯一风格载体）
  - `finalcut` 按预设"调色意图"选一个 `jianying_assets.py` 校验过的滤镜，调色也统一到选定风格
- **动漫的"锁定二次元流派防漂移"并入本通用机制**（即 `anime-2d` 预设）——单一机制，不再是动漫专属的平行规则
- **选风格时机**：`/new-drama` 选定（`project.json.format.style`），`/design` 出图前仍可改；出了设定图/视频再改＝作废重做（同画幅约束）。老项目无 `format.style` 按 medium 取默认
- 诚实边界：含角色镜头靠 @引用设定图承载主要风格、STYLE LOCK 加固；空镜靠 STYLE LOCK。整体"强一致"，非逐帧像素级
- 影响：`new-drama`/`design` 技能、`producer`（schema 加 `format.style`）、`art-director`、`cinematographer`、`finalcut`、工作区文档

## [2.7.0] - 2026-07-16

### 新增（短剧叙事优化——靠台词和内心独白讲故事，扬 AI 之长）
调研 2024-2026 微短剧爆款要素后优化：黄金3秒/强钩子/高频反转/每集结尾钩子/台词直给/情绪价值，
外加 2025"走心"转向（精品化、情感深度、逻辑自洽）。核心洞察：**AI 生成视频微表情/口型不可控，
靠脸传情既廉价又脆弱；而台词/内心独白是音频层面、可控可稳定交付**——所以"多台词+内心独白"
既贴合短剧类型、又扬 AI 之长（与本项目"特写克制/别怼脸"同向）。
- **`screenwriter` 编剧**：短剧法则新增"台词直给 + 内心独白"（以扬长避短为开篇）；情绪靠台词+内心独白承载，
  修正原"偏爱情绪面部特写"（保留 AI 可拍性约束）；**每句台词逐句标 `【对白】/【独白】`**，
  剧本末尾附独白清单；内心独白"适度用"（服务反差/内心戏，不刷屏）；**短剧一般不用第三方旁白解说**
  （`【旁白】` 标签保留给动漫等形态）
- **`director` 导演**：分镜台词/音效列区分**对白(同期声)** vs **内心独白(后期配音)**；
  内心独白镜头不必怼脸——可配空镜/反应/环境 B-roll，或用一个 8-15s 长镜承载整段独白（"听内心、看画面"）
- **`finalcut` 精剪师**：按标签分轨落地——**对白只做字幕**（即梦原声已含，不重配；仅静音模式/`qc_warning:缺音轨` 的对白镜例外，按独白补朗读）；
  `ep{NN}.srt` 仅放对白（与即梦原声对齐、供粗剪），内心独白作单独样式化字幕片段（居中偏上/斜体）避免与对白字幕重复；
  **内心独白做字幕 + 配音**：走**剪映「文本朗读」**一键生成 AI 配音（零依赖、中文音色好；
  pyJianYingDraft 无法脚本触发 TTS，故这步在剪映人工点一下，精剪说明会明确指引）；
  Resolve 路径无内置 TTS→独白先作字幕、配音需自录或外部 TTS（动漫的旁白同此处理）
- 同步：`cinematographer`（内心独白不进视频提示词，纯后期音轨）、`/script` `/storyboard` 技能、
  工作区角色职责与交付边界

## [2.6.0] - 2026-07-16

### 新增（把即梦能力吃满——告别"全是 4s 单动作短片"）
- **时长用满 4-15s，且要有分布**：`director` 导演不再默认最短镜——快切钩子 4-6s、常规 5-8s、
  情绪峰值/定场/氛围/连续调度镜 **8-15s**；分镜示例与时长核算同步更新，全片清一色 4s 视为译窄需回炉
- **导演视角切镜（长镜多节拍）**：`cinematographer` 摄影指导新增"时间码分段"提示词法——
  同场景连续戏合并成一个 8-15s 的 `multimodal2video` 生成单元，在一条提示词里用 `0-3s / 3-7s / 7-12s`
  切多个内部镜头（缓推→切近景→拉回中景）。这是**保住角色 @引用一致性与原声**的首选切镜方式，
  取代"把一场戏拆成三个各 4s 碎片"；`director` 分镜表可把连续节拍标注为同一"生成单元"交接
- **新增 `multiframe2video` 模式（备选切镜）**：2-20 张关键帧图插值成连贯长段落（每段 0.5-8s、总≥2s），
  适合连续动作/变身/位移；`video-generator` 增加提交命令（`--images` 逗号分隔、`--transition-prompt`/
  `--transition-duration` 按段重复）。注意该模式**静音、无 model/resolution 参数**、画幅由首图推断
- **三种即梦网页端功能全部打通并统一命名**（agent/技能/工作区一致标注）：
  **全能参考=`multimodal2video`、智能多帧=`multiframe2video`、首尾帧=`frames2video`**
- **新增关键帧工作流（让首尾帧/智能多帧真正可用）**：这两个模式需要镜头专属关键帧（非角色/场景设定图），
  流水线补上产帧环节——
  - `cinematographer` 在 shotlist 用 `keyframes_needed`/`first`/`last`/`first_from_prev` 声明各镜关键帧需求
  - `art-director` 美术指导新增第 5 项职责：按需用 Gemini 生成首帧/尾帧/多帧关键帧（省即梦积分、走水印清理），落 `03-design/keyframes/`
  - `video-generator` 对衔接性首帧用 `ffmpeg -sseof` 从上一镜成片抽尾帧当首帧（免费、精确接得上）；关键帧缺失即停不烧积分
  - `/shoot` 新增第 1.5 步"关键帧 prep"（有 `keyframes_needed` 才触发，在门禁③报价前完成）；工作区目录规范加 `03-design/keyframes/`
- **分辨率可调（诚实标注天花板）**：shotlist 新增 `resolution` 字段。`multimodal2video` 与整个 seedance2.0
  家族封顶 **720p**；**1080p 仅 `image2video`/`frames2video` 的 3.5pro/3.0pro 支持，且放弃全能 @引用**——
  故 1080p 只给空镜/静物等一致性不吃紧的镜头，反复出场角色一律留在 720p 的 multimodal 路线保一致性
- **完整能力矩阵入档**：cinematographer 内置"模式×一致性×时长×分辨率×模型×音轨"矩阵（以 `dreamina -h` 实测为准），
  选型有据；multimodal 的 `--video`（复刻运镜/动作/特效/节奏）、`--audio`（BGM 对位/卡点）进阶输入写明用法

### 变更（配合新模式的省钱与安全）
- **质检音轨门改为 mode-aware（关键，防止为静音镜白烧积分）**：`video-generator` 与工作区硬规则同步——
  静音模式（`multiframe2video`/标 `silent` 的镜头）不检查音轨、缺音轨正常；自带音轨模式若缺音轨
  **只记 `qc_warning` 交精剪补音，绝不因缺音轨触发重生成**（重生成既未必补回音轨又烧积分）。
  `tools/concat.py` 早已对无音轨片段补静音轨，静音镜下游拼接/精剪无碍，"全程保留音轨"由精剪补齐落实
- **入参校验按模型细化**：`video-generator` 按 mode/model 分别校验时长区间与分辨率组合（越界不提交、直接标 failed），
  并把 `multiframe2video` 一并纳入"画幅由输入图推断→画幅错不盲目重生成、改报用户换图/改 ratio"的清单
- `/shoot` 报价（门禁③）新增时长分布/分辨率分布提示，并提醒"越长越贵"，长镜集中在情绪/定场镜才合理

## [2.5.0] - 2026-07-15

### 新增（视频生成"可用性"保障——借鉴成熟渲染/生成流水线）
- **`video-generator` 视频生成师增加下载后质检门**：不再轻信即梦 CLI 的 `success` 状态，
  每个下载文件必须通过 ffprobe 校验才收货——**技术可用性**判定，不越界做画面创作质检（那归审片人 /review）：
  - 文件存在且非空、容器可解析（截断/损坏会被 ffprobe 报错拦下）
  - 含视频流、**含音轨**（即梦视频自带台词/音效，缺音轨即不可用，落实工作区"全程保留音轨"铁律）
  - 时长只查短缺（≥ 请求 −1.5s，防截断/半成品；超出正常，精剪会裁）、画幅比例 ≈ shotlist 的 ratio
  - 复用剪辑师同款 ffprobe 调用，跨平台一致
- **`status=success` 语义收紧为"下载完成且质检通过"**：先质检、通过再重命名为 `sh{NN}.mp4`，
  坏文件绝不进最终名污染下游剪辑（editor 收料检查因此更可靠，无需改动）
- **失败分类与省钱重试**：传输问题（零字节/截断/打不开）→ 用同一 submit_id **免费重下载**（≤3 次）；
  内容问题（缺音轨/时长严重不足/画幅错）与提交/轮询失败 → **重生成，烧积分，每镜最多 1 次**；
  终态错误（合规授权/积分不足/入参非法）不重试直接标 failed——杜绝"质检失败→自动重生成"的循环烧钱
- 汇报格式增加质检拦截明细（哪些镜头重下载、哪些重生成），让积分花在哪一目了然
- 同步更新 `/shoot` 流程说明与工作区规范（`workspace-CLAUDE.md` 硬性安全规则）

## [2.4.0] - 2026-07-13

### 新增
- **精剪吸收剪映专业素材库**：`finalcut` 精剪师现可用剪映内置的海量转场/动画/滤镜（转场 450+、
  滤镜 1000+、特效 1000+、入出场动画各百余种），生成更专业的剪映草稿
  - 新增 `tools/jianying_assets.py`：从已装 pyJianYingDraft **实时检索真实可用的素材枚举名**
    （按类别 + 情绪关键词，如 `filter --grep 电影,冷`），避免用到不存在的名字导致草稿报错——
    比静态素材清单更可靠、随库版本自动同步
  - `finalcut` agent 内置"剪映素材手册"：电影感精选默认（转场/滤镜/动画均为已验证枚举名）
    + 检索脚本用法 + 克制使用原则（转场种类 ≤2-3、全片统一一个滤镜）
  - 与既有 pyJianYingDraft 草稿生成同源，零外部依赖；建项/精剪时脚本自动复制进工作区

## [2.3.2] - 2026-07-13

### 修复
- **粗剪"剪坏"画质**：`tools/concat.py` 原来无条件二次编码 + 缩放补边（上采样模糊、插帧抖动、补黑边），
  损害本已统一的即梦素材。改为**非破坏性优先**——探测规格，片段一致时走**纯流拷贝（零重编码，无损，
  经 md5 逐字节验证）**，仅规格真不一致才转码并打印 ⚠ 提示

### 变更（剪辑工作流重定位）
- **`/finalcut` 精剪确立为成片主推路径**（非破坏性：直接引用原始 sh*.mp4 上 NLE 时间线，最终只渲染一次）；
  明确精剪绝不使用粗剪预览作素材，且无需先跑 `/edit`
- **`/edit` 粗剪降级为可选**：仅供快速看节奏；其核心产出改为**给人工精剪的完整交付包**——
  原始素材清单 + EDL 式剪辑顺序表 + 手工精剪步骤（剪映/达芬奇导入、BGM 对位、字幕、调色、导出）
- 原始 `sh*.mp4` 全程只读不改的保证写入剪辑师规则；`/review` 完成后引导语改为优先 `/finalcut`
- 流水线、命令表、交付边界（README 中英 + 工作区模板）同步重定位

## [2.3.1] - 2026-07-13

### 修复
- **成片"全是脸部特写"缺电影感**：修正导演/摄影/审片三个 agent 的镜头语言偏向
  - 导演：新增"景别配比原则"（特写 ≤10% 只留情绪峰值，默认全景/中景撑起电影画面感）；
    删除原短剧规则里"竖屏优先特写、人脸是主角"的过度偏向；分镜示例改为"全景落地→中景对峙→特写爆点"的层次样板，
    画面描述要求写出前景/背景/纵深/光线
  - 摄影指导：新增"电影构图要领"——景别关键词严格对齐分镜（不擅自拉近），非特写镜头补
    `cinematic composition / depth of field / foreground-background layers / rule of thirds` 等构图词
  - 审片人：检查清单新增"电影感"维度，整集特写占比过高（>30% 或连续怼脸）时提示景别单调并建议回炉

## [2.3.0] - 2026-07-13

### 新增
- **跨运行时兼容**：同一份插件可安装到多种 Agent
  - 11 个 SKILL.md 统一加入"运行时适配"块：不支持 subagent 的运行时自动降级为
    "读取插件内 agents/*.md 作为工作规范在当前上下文执行"；无 AskUserQuestion 时门禁降级为对话内确认，语义不变
  - **OpenClaw**：经其 Claude 插件 bundle 机制直接安装
    （`openclaw plugins install film-studio --marketplace <本仓库>`），skills 原生加载 + agents 降级执行
  - **Hermes Agent**（Claude Code / Agent SDK 内核）：与 Claude Code 同构，`claude plugin` 命令直接装
  - 仓库开发规则新增：新技能必须保留"运行时适配"块

## [2.2.0] - 2026-07-13

### 新增
- **可选剪辑增强**（project.json 新增 `editing` 块，**两项默认关闭**，建项时询问、中途可让制片人开关）：
  - `episode_overlap` 集间交叉衔接：每集开头重放上一集最后镜头的结尾几秒（默认 4s，`sh00-recap.mp4`
    命名自然排序置顶），方便观看衔接；第 1 集不适用
  - `intro_outro` 片头/片尾：每集首尾加全剧复用的片名卡/引导卡（`assets/intro.mp4`、`outro.mp4`，
    首次启用时按 style-bible 风格生成）
  - 粗剪（editor）与精剪工程（finalcut，剪映/Resolve 两路径）都读取此配置；开启片头时字幕时间轴自动偏移
  - `tools/concat.py` 的 `--files` 支持绝对路径与目录内文件名混用（片头/片尾卡直接进清单，无需改码）

## [2.1.0] - 2026-07-13

### 新增
- **DaVinci Resolve Studio 精剪路径（推荐）**：/finalcut 开工时检测 Resolve（脚本模块存在 + `scriptapp` 可连接，
  外部脚本控制仅 Studio 付费版支持）；可用时经用户确认走官方 Python API——建项目/时间线、镜头序列、
  BGM 音轨对位、SRT 字幕、调色建议，且**确认后可自动渲染成片到 05-final/**（剪映路径做不到的能力）
- **未安装 Resolve 的用户零影响**：静默走剪映路径（pyJianYingDraft），不做任何推销提示

## [2.0.0] - 2026-07-13

### 不兼容变更（更名）
- **插件更名**：short-drama-studio → **film-studio**（影视工作台）；GitHub 仓库更名为
  `Claude-Code-Film-Studio`（旧地址自动重定向）；marketplace.json 增加 `renames` 记录旧名映射。
  旧用户迁移：`claude plugin marketplace update short-drama-studio` 走 renames，或卸载重装

### 新增
- **多创作形态**：建项时选择 短剧（short-drama）/ 电影短片（short-film）/ 动漫番剧（anime），
  写入 `project.json.format.medium`
  - 编剧按形态切换创作法则：短剧（黄金3秒/反转密度）、电影短片（三幕/视听叙事/留白）、动漫（情绪峰值/内心独白/章节感）
  - 导演按形态调整镜头语言：竖屏近景 / 横屏丰富景别 / 漫画式夸张构图
  - 美术按形态定视觉基调：动漫形态在 style-bible 锁定二次元流派关键词并逐字复用，防画风漂移
  - 摄影提示词、运营平台策略（抖音/快手、B站/视频号、B站+切片）同步按形态适配
  - 老项目无 medium 字段时默认 short-drama，完全向下兼容

本工作台遵循[语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号**：不兼容的流程/目录结构变更（老项目需要迁移）
- **次版本号**：新增 agent、命令或能力（向下兼容）
- **修订号**：修复与文档完善

每次升级：更新 `VERSION` → 在此记录变更 → `git tag v<版本> && git push --tags`。

## [1.4.1] - 2026-07-13

### 变更
- **即梦模型默认走 VIP 通道**（防排队等待过久）：常规镜头 `seedance2.0fast_vip`，重点镜头 `seedance2.0_vip`；
  非 VIP 通道模型仅在用户明确要求省积分且不赶时间时使用。摄影指导默认值、README、工作区规范同步更新

## [1.4.0] - 2026-07-13

### 新增
- **macOS 支持**：工作台全流程可在 Mac 上运行
  - 工具脚本从 PowerShell 迁移为跨平台 Python（`tools/concat.py`、`tools/clean_refimg.py`，删除 .ps1），
    功能等价并实测（混合规格/无音轨补静音/水印两模式）
  - 精剪师：剪映草稿目录按系统定位（macOS `~/Movies/JianyingPro/...`）；自动导出标注仅 Windows 支持，macOS 手动导出
  - 运营：封面中文字体按系统选择（Windows 微软雅黑 / macOS 苹方）
  - 各 agent/skill 命令示例改为两平台通用写法；工作区规范补充双平台环境说明
- 仓库开发规则新增跨平台约束（工具只用 Python stdlib + ffmpeg）

## [1.3.2] - 2026-07-13

### 文档
- README 多语言：新增英文版 `README.en.md`，中英文版顶部互设切换链接

## [1.3.1] - 2026-07-13

### 修复
- **Gemini 设定图水印污染视频**：Gemini（Nano Banana）出图右下角带可见水印，作为 `multimodal2video`
  参考图时会被 Seedance 复刻进视频。新增 `tools/clean-refimg.ps1`（delogo 修复右下角 / crop 裁底条两种模式），
  美术指导入库前强制清理并肉眼复查；摄影指导禁止引用 `_raw/` 原始图；审片人检查清单新增"水印残留"维度
- PowerShell 脚本改为 UTF-8 BOM 编码（Windows PowerShell 5.1 对无 BOM 中文脚本按 ANSI 解析会报错，
  concat.ps1 同步修复）

## [1.3.0] - 2026-07-13

### 新增
- **插件化**：仓库改造为标准 Claude Code 插件 + 自托管 marketplace（`.claude-plugin/plugin.json` + `marketplace.json`），
  支持命令行安装：`claude plugin marketplace add zq940222/Claude-Code-Short-Drama-Studios` →
  `claude plugin install short-drama-studio@short-drama-studio`
- `/new-drama` 新增工作区初始化：首次建项自动把创作规范（`templates/workspace-CLAUDE.md`）和
  `tools/concat.ps1` 复制进用户工作目录（插件的 CLAUDE.md 不会被自动加载，以此机制替代）

### 变更
- 目录结构：`.claude/agents/` → `agents/`，`.claude/skills/` → `skills/`（插件标准布局）
- 仓库根 CLAUDE.md 改为插件开发说明；工作台创作规范移至 `templates/workspace-CLAUDE.md`
- 发布流程：VERSION、plugin.json、marketplace.json 三处版本号保持一致

## [1.2.0] - 2026-07-13

### 新增
- **finalcut 精剪师 agent + `/finalcut` 命令**：pyJianYingDraft 自动生成剪映草稿（镜头序列+转场、BGM 对位、台词字幕轨 SRT、全局滤镜），剪映中微调导出
- **operator 运营 agent + `/publish` 命令**：发布文案（候选标题/话题标签/发布时段）、封面图（抽帧+大字标题）、半自动发布抖音创作者中心
- 门禁④：发布前用户确认（发布不可撤回）
- 目录规范新增 `06-publish/ep{NN}/`；`requirements.txt`

### 说明
- 剪映版本约束：5.9 草稿兼容最完整，≤6.8 支持自动导出，新版草稿加密支持有限

## [1.1.0] - 2026-07-13

### 修正
- **保留即梦原声**：Seedance 生成的视频自带声音（台词/音效），`tools/concat.ps1` 重写为保留音轨并统一 AAC 48kHz，无音轨片段自动补静音（原版本 `-an` 会丢音轨）
- 交付边界修正：`/edit` 定位为粗剪预览 + 精剪交付包

### 新增
- **composer 配乐师 agent + `/music` 命令**：Suno 网页端生成 BGM + 对位说明，可与生成/审片并行

## [1.0.0] - 2026-07-10

### 新增
- 初始搭建：8 个影视专业 agent（制片人/编剧/导演/美术指导/摄影指导/视频生成师/剪辑师/审片人）
- 8 个阶段命令：/new-drama /script /storyboard /design /shoot /review /edit /studio-status
- 三道门禁（剧本定稿/设定图定稿/积分报价）与防烧钱机制
- 引擎分工：设定图走 Gemini 网页端，视频走即梦 Seedance 2.0，拼接走 ffmpeg
- 项目目录规范与 `tools/concat.ps1`
