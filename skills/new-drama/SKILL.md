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
- 工作区 `tools/` 缺 `concat.py` 或 `clean_refimg.py` → 从插件根的 `tools/` 复制过来（剪辑师拼接、美术指导清水印要用；跨平台 Python 脚本）
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
2. 调度 **producer** agent 建项：创建 `projects/<片名>/` 全套目录（01-script、02-storyboard、
   03-design/characters、03-design/scenes、04-footage、05-final）和 project.json（**含 medium 字段记录创作形态**）
3. 顺带查一次 `dreamina user_credit` 报告余额
4. 告知用户下一步：运行 `/script` 开始剧本创作；如果用户已带来了故事想法，直接问是否现在进入剧本阶段

## 创作形态的影响（写进 project.json 后各 agent 自动适配）

| 形态 | medium 值 | 编剧法则 | 视觉基调 |
|---|---|---|---|
| 短剧 | `short-drama` | 黄金3秒、高反转密度、卡点钩子 | 写实、竖屏近景为主 |
| 电影短片 | `short-film` | 三幕结构、视听叙事、留白 | 电影感、横屏、景别丰富 |
| 动漫番剧 | `anime` | 热血/情绪张力、内心独白、章节感 | 二次元画风（style-bible 锁定具体流派） |

## 注意

- 片名会成为目录名：过滤 Windows 非法字符（`\ / : * ? " < > |`）
- 若同名项目已存在，停下询问是续作、覆盖还是换名
