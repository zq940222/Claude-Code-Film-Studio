---
name: music
description: 配乐阶段。调度配乐师 agent 用 Suno 网页端生成背景音乐，产出 BGM 文件和对位说明，供剪映/PR 精剪使用。用户说"配乐"、"背景音乐"、"BGM"、"/music"时使用。
---

# /music 背景音乐

## 运行时适配（跨 Agent 兼容）

- **支持 subagent 的运行时**（Claude Code / Hermes Agent 等）：按下文"调度 xxx agent"正常派发子代理执行
- **不支持 subagent 的运行时**（Codex CLI / OpenClaw 等，以插件 bundle 方式安装）：正文提到"调度 X agent"时，
  改为读取插件根 `agents/<X>.md`（本技能目录上两级），以其为工作规范在当前上下文直接执行，效果等同
- **用户确认处**：有 AskUserQuestion 工具就用；没有则直接在对话中提问并等待用户回复，门禁语义不变


## 前置检查

- status.script 为 approved（配乐方案基于剧本情绪曲线）；分镜已完成更佳（可精确到镜头区间对位）

## 流程

1. 调度 **composer** agent：
   - 先出配乐方案（几段 BGM、曲风、情绪、对应剧情区间），呈现给用户确认
   - 确认后走 Suno 网页端生成，下载到 `04-footage/ep{NN}/bgm/`
   - 写 `bgm-notes.md` 对位说明（每段音乐的入点镜头、情绪、循环建议）
2. 向用户汇报：生成了几段、各自路径、Suno 额度情况
3. 提醒：BGM 不进 ffmpeg 粗剪，是给剪映/PR 精剪的独立素材

## 注意

- Suno 不可用（未登录/额度尽）时停下报告，不用其他引擎替代
- 本阶段与 /shoot、/review 无依赖关系，可并行进行

## 交付自检（本阶段通过的判据）

- [ ] BGM 文件落在 `04-footage/ep{NN}/bgm/`，每个文件存在且非空
- [ ] `bgm-notes.md` 每段都标了**起止时间码 + 对应剧情段落 + 循环建议**，精剪师能直接对位
- [ ] 按 `sound-design` 技能的"交付自检"过了一遍（三层轨没越界、ducking 写明、静音镜有补音方案）
- [ ] BGM **没有**混进 `/edit` 粗剪（粗剪只保留即梦原声）
- [ ] 走了降级（用户自备 BGM / 无 BGM 交付）时已明确告知用户，`bgm-notes.md` 里写清了精剪该怎么处理
