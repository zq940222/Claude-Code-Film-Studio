---
name: music
description: 配乐阶段。调度配乐师 agent 用 Suno 网页端生成背景音乐，产出 BGM 文件和对位说明，供剪映/PR 精剪使用。用户说"配乐"、"背景音乐"、"BGM"、"/music"时使用。
---

# /music 背景音乐

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
