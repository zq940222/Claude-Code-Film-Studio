---
name: script
description: 剧本创作阶段。调度编剧 agent 产出大纲、人物小传、分集剧本，迭代修改直到用户确认定稿（门禁①）。用户说"写剧本"、"/script"、"改剧本"时使用。
---

# /script 剧本创作（含门禁①）

## 前置检查

- 确定目标项目（projects/ 下唯一项目则默认它；多个则问）；project.json 必须存在，否则先走 /new-drama

## 流程

1. 收集用户的故事想法（一句话创意即可；用户没想法时让编剧先提 3 个题材内的高概念供选）
2. 调度 **screenwriter** agent：先出 `outline.md` + `characters.md`，给用户过目大纲和人物后再写分集剧本 `ep{NN}.md`
3. 把剧本关键内容（卖点、分集钩子、各集概要）呈现给用户，进入修改迭代循环
4. **门禁①**：用 AskUserQuestion 明确问"剧本是否定稿？"
   - 定稿 → 更新 project.json：status.script → approved，提示下一步 `/storyboard`
   - 修改 → 收集意见回到第 2 步

## 注意

- 迭代中的每一稿都直接覆盖文件（git 留痕），不要产生 v1/v2 文件副本
- 人物小传中的外貌描述是后续设定图的源头，确认环节要提醒用户重点看外貌设定
