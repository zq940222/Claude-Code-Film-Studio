---
name: new-drama
description: 新建影视项目（短剧/电影短片/动漫番剧）。收集片名、创作形态、题材、画幅（9:16/16:9）、每集时长、集数，创建标准项目目录和 project.json。用户说"新建短剧"、"新建项目"、"做部动漫"、"拍个短片"、"/new-drama"时使用。
---

# /new-drama 建项

## 运行时适配（跨 Agent 兼容）

- **支持 subagent 的运行时**（Claude Code / Hermes Agent 等）：按下文"调度 xxx agent"正常派发子代理执行
- **不支持 subagent 的运行时**（OpenClaw 等，以插件 bundle 方式安装）：正文提到"调度 X agent"时，
  改为读取插件根 `agents/<X>.md`（本技能目录上两级），以其为工作规范在当前上下文直接执行，效果等同
- **用户确认处**：有 AskUserQuestion 工具就用；没有则直接在对话中提问并等待用户回复，门禁语义不变


## 第 0 步：工作区初始化（只做一次）

本技能目录的上两级是插件根目录（含 `templates/` 和 `tools/`）。检查当前工作目录：

- 无 `CLAUDE.md` → 把插件根的 `templates/workspace-CLAUDE.md` 复制为工作区 `./CLAUDE.md`（工作台创作规范，之后会话自动加载）；已有 CLAUDE.md 则展示规范要点提示用户手动合并，**不要覆盖**
- 工作区 `tools/` 缺 `concat.py`、`clean_refimg.py` 或 `jianying_assets.py` → 从插件根的 `tools/` 复制过来（分别用于粗剪拼接、清水印、精剪查剪映素材；跨平台 Python 脚本）
- 检查 `python -c "import pyJianYingDraft"`（macOS 用 `python3`），失败则提示 `python -m pip install pyJianYingDraft`（/finalcut 精剪要用，可先跳过不阻塞建项）

## 流程

1. 用 AskUserQuestion 收集（用户在参数里已给的不重复问）：
   - **片名**（可暂定）
   - **创作形态**：短剧（竖屏快节奏，抖音/快手）/ 电影短片（横屏电影感叙事）/ 动漫番剧（二次元画风，B站/抖音）
   - **题材**：都市逆袭 / 甜宠 / 悬疑 / 玄幻 / 科幻 / 热血 / 其他
   - **画幅**：9:16 竖屏 或 16:9 横屏（短剧默认竖屏，电影短片默认横屏，动漫两者皆可）
   - **每集时长**：短剧 60-120 秒；电影短片 180-600 秒；动漫番剧 120-300 秒
   - **集数**：建议先做 1 集试水验证流程，再批量
   - **剪辑增强**（多选，**默认都不选**）：① 集间交叉衔接——每集开头重放上一集结尾几秒，方便观看衔接；
     ② 片头/片尾——每集加片名卡和引导卡。写入 project.json 的 `editing` 块，之后随时可让制片人改
2. **选整体视频风格（像小云雀那样一次定风格、全剧锁定）**：读插件根的 `templates/style-presets.md`（本技能目录上两级；库按 真人/2D/3D 三类组织，共十余个预设）。
   确定 medium 后，用一次 AskUserQuestion 按形态给 3-4 个最合适的预设 + "更多/自定义"（选"更多"就在对话里按类别列全库让用户挑）：
   - 短剧 → `cn-urban-realist 国产都市写实` / `korean-soft 韩剧都市柔光` / `hollywood-retro 美式复古好莱坞` / 更多(港风/武侠江湖写实/古装华丽/霓虹赛博/3D卡通/自定义…)
   - 电影短片 → `cinematic-film 电影质感` / `film-90s-realist 90年代写实电影` / `jp-slice-of-life 日式生活自然` / 更多(复古叙事/90年代农村/国风水墨/厚涂油画…)
   - 动漫 → `anime-2d 日系动漫2D手绘` / `cartoon-3d 3D卡通` / `donghua-guofeng 国漫国风` / 更多(90年代复古动漫/厚涂插画/3D写实CG…)
   - `custom 自定义`：让用户描述想要的风格（或参考影片），记下，稍后由美术指导拟 STYLE LOCK
3. 调度 **producer** agent 建项：创建 `projects/<片名>/` 全套目录（01-script、02-storyboard、
   03-design/characters、03-design/scenes、04-footage、05-final）和 project.json（**含 `format.medium` 创作形态与 `format.style` 选定风格**）
4. **写风格锁桩到 style-bible.md（单一真源）**：在 `03-design/style-bible.md` 顶部写入**固定结构**的风格锁区（标题逐字照抄下方，各 agent 靠这行标题定位）：
   ```
   ## 风格锁 STYLE LOCK（逐字复用，勿改）
   <把选定预设的 STYLE LOCK 英文关键词块原样贴在此；custom 则写占位：TODO 待 /design 由美术指导按用户描述拟定>
   ```
   此后美术出图、摄影写视频提示词、精剪调色都以此区块为准——**agent 只读工作区的 style-bible.md，不读插件的预设库**
5. 顺带查一次 `dreamina user_credit` 报告余额
6. 告知用户下一步：运行 `/script` 开始剧本创作；如果用户已带来了故事想法，直接问是否现在进入剧本阶段。
   （风格在 /design 出图前仍可改；一旦出了设定图/视频再改风格＝那些图和视频作废需重做，同画幅约束）

## 创作形态的影响（写进 project.json 后各 agent 自动适配）

| 形态 | medium 值 | 编剧法则 | 视觉基调 |
|---|---|---|---|
| 短剧 | `short-drama` | 黄金3秒、高反转密度、卡点钩子 | 写实、竖屏近景为主 |
| 电影短片 | `short-film` | 三幕结构、视听叙事、留白 | 电影感、横屏、景别丰富 |
| 动漫番剧 | `anime` | 热血/情绪张力、内心独白、章节感 | 二次元画风（style-bible 锁定具体流派） |

`format.style` 是在 medium 的默认基调之上进一步选定的**具体画风预设**（写实都市/电影质感/2D手绘/3D卡通…），
选定后写进 style-bible.md 的风格锁，全剧逐字复用保持一致。动漫的"锁定二次元流派"就是本机制的一个预设（`anime-2d`）。

## 注意

- 片名会成为目录名：过滤 Windows 非法字符（`\ / : * ? " < > |`）
- 若同名项目已存在，停下询问是续作、覆盖还是换名
