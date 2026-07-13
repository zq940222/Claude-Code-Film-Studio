---
name: shoot
description: 视频生成阶段。摄影指导产出 shotlist.json 提示词清单，报积分预估给用户确认（门禁③）后，视频生成师批量提交即梦生成任务并下载。用户说"开拍"、"生成视频"、"/shoot"时使用。
---

# /shoot 视频生成（含门禁③——唯一消耗大量积分的环节）

## 前置检查

- status.design 必须是 approved；否则先走 /design
- 回炉场景（review 后重拍）：shotlist.json 已存在且有 status=pending 的镜头，跳过第 1 步直接从第 2 步开始

## 流程

1. **提示词**：调度 **cinematographer** agent 产出 `04-footage/ep{NN}/shotlist.json`
   （逐镜头：模式、提示词、引用图、时长、模型）
2. **报价（门禁③）**：调度 **producer** agent：
   - `dreamina user_credit` 查当前余额
   - 汇总待生成任务：N 个镜头、总时长、各模式/模型分布
   - 报积分预估：project.json 的 credits.notes 里有历史单价就据此估算；没有则如实说"单价未知"，
     建议先只生成 1 个镜头校准单价
   - 用 AskUserQuestion 问用户：**全部生成 / 先生成 1 镜校准 / 调整方案（换 fast 模型、减镜头）/ 取消**
3. **执行**：用户确认后，调度 **video-generator** agent（明确告知"门禁③已确认，授权生成镜头范围：…"）：
   批量提交 → 轮询 → 下载到 `04-footage/ep{NN}/sh{NN}.mp4` → 实时更新 shotlist.json
4. **收尾**：汇报成功/失败清单和实际积分消耗（写入 project.json credits）；
   status.footage → done（有 failed 镜头则保持 in_progress 并列出）
5. 提示下一步：`/review` 质检

## 硬性规则

- 门禁③未确认，任何人不得提交生成任务
- "先生成 1 镜校准"路径：完成后用实际消耗重新报价剩余镜头，再次确认后继续
