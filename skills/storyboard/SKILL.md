---
name: storyboard
description: 分镜阶段。调度导演 agent 把定稿剧本拆解成分镜表（镜号/景别/运镜/时长/画面/台词/情绪）。用户说"做分镜"、"/storyboard"时使用。
---

# /storyboard 分镜

## 前置检查

- project.json 的 status.script 必须是 approved；否则告知用户先走 /script 定稿

## 流程

1. 调度 **director** agent：读定稿剧本，产出 `02-storyboard/ep{NN}-storyboard.md`
2. 检查导演的时长核算：各镜头时长之和 vs 每集目标时长，偏差 >15% 让导演调整
3. 把分镜表和风险镜头提示呈现给用户；分镜不设硬门禁，用户无异议即自动推进
4. 更新 project.json：status.storyboard → done
5. 提取分镜表中的"出场角色"和"场景"去重清单，作为 /design 阶段的工作清单写在分镜文件末尾；提示下一步 `/design`
