---
name: design
description: 设定图阶段。调度美术指导 agent 生成角色三视图和场景概念图（优先 Gemini 网页端，降级即梦），用户确认定稿（门禁②）。用户说"画设定图"、"角色设计"、"/design"时使用。
---

# /design 视觉设定（含门禁②）

## 运行时适配（跨 Agent 兼容）

- **支持 subagent 的运行时**（Claude Code / Hermes Agent 等）：按下文"调度 xxx agent"正常派发子代理执行
- **不支持 subagent 的运行时**（OpenClaw 等，以插件 bundle 方式安装）：正文提到"调度 X agent"时，
  改为读取插件根 `agents/<X>.md`（本技能目录上两级），以其为工作规范在当前上下文直接执行，效果等同
- **用户确认处**：有 AskUserQuestion 工具就用；没有则直接在对话中提问并等待用户回复，门禁语义不变


## 前置检查

- status.storyboard 必须是 done（设定清单来自分镜表）；分镜没做完先走 /storyboard

## 流程

0. 工作区缺 `tools/clean_refimg.py` 时，先从插件根（本技能目录上两级）的 `tools/clean_refimg.py` 复制过来
1. 调度 **art-director** agent：
   - 先写/更新 `03-design/style-bible.md`（全剧视觉基调）
   - 按分镜表的角色/场景清单生成设定图：角色每人 front/side/face 三张，场景每处一张
   - 首选 Gemini 网页端（不耗积分），失败降级即梦 text2image
   - **每张图入库前用 `tools/clean_refimg.py` 清理右下角水印并复查**（Gemini 图有可见水印，会被 Seedance 复刻进视频）
2. 生成完毕后逐张用 Read 查看图片（重点看右下角无水印残留），向用户展示并汇报：哪些图走了哪个引擎、是否消耗积分
3. **门禁②**：用 AskUserQuestion 明确问"设定图是否定稿？"
   - 定稿 → status.design → approved，提示下一步 `/shoot`
   - 不满意 → 收集具体意见（哪个角色/场景、什么问题），让美术指导重生成对应图，回到第 2 步

## 注意

- 设定图直接决定成片角色一致性，是回报率最高的确认环节，鼓励用户认真看
- 重生成只重做被点名的图，通过的图不要动
