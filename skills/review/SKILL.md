---
name: review
description: 审片阶段。调度审片人 agent 对生成的镜头抽帧质检（画面瑕疵/角色一致性/分镜匹配/连贯性），产出审片报告和回炉清单。用户说"审片"、"质检"、"/review"时使用。
---

# /review 审片质检

## 前置检查

- shotlist.json 存在且至少有 status=success 的镜头；否则先走 /shoot

## 流程

1. 调度 **reviewer** agent：逐镜头抽帧审查，产出 `04-footage/ep{NN}/review-report.md`
2. 向用户呈现审片结论：通过 X 镜 / 建议回炉 Y 镜（附问题描述和抽帧截图路径，可 Read 展示关键帧）
3. 用 AskUserQuestion 问用户如何处理回炉清单：
   - **回炉重拍** → 确认哪些镜头，reviewer 把它们在 shotlist.json 中置回 pending 并更新提示词建议，
     然后走 `/shoot`（回炉同样过门禁③报价）
   - **瑕疵可接受，直接剪辑** → 提示下一步 `/edit`
4. 全部通过或用户放行后，告知可以进入 `/edit`

## 注意

- 回炉是正常工作流，AI 生成一次全过的概率不高；但回炉烧积分，决定权永远在用户
