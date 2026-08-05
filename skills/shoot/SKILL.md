---
name: shoot
description: 视频生成阶段。摄影指导产出 shotlist.json 提示词清单，报积分预估给用户确认（门禁③）后，视频生成师批量提交即梦生成任务并下载。用户说"开拍"、"生成视频"、"/shoot"时使用。
---

# /shoot 视频生成（含门禁③——唯一消耗大量积分的环节）

## 运行时适配（跨 Agent 兼容）

- **支持 subagent 的运行时**（Claude Code / Hermes Agent 等）：按下文"调度 xxx agent"正常派发子代理执行
- **不支持 subagent 的运行时**（OpenClaw 等，以插件 bundle 方式安装）：正文提到"调度 X agent"时，
  改为读取插件根 `agents/<X>.md`（本技能目录上两级），以其为工作规范在当前上下文直接执行，效果等同
- **用户确认处**：有 AskUserQuestion 工具就用；没有则直接在对话中提问并等待用户回复，门禁语义不变


## 前置检查

- status.design 必须是 approved；否则先走 /design
- 回炉场景（review 后重拍）：shotlist.json 已存在且有 status=pending 的镜头，跳过第 1 步；若这些 pending 镜头有未备齐的 `keyframes_needed` 先走第 1.5 步，否则直接从第 2 步开始
- **白模（可选）**：分镜里有 `【白模】` 标注但 `status.previz` 仍是 pending 时，提醒用户"这些镜头的运镜可先走
  `/previz` 用白模锁死（本地渲染、不耗积分），再来生成命中率更高"——用户可选择先做白模或直接生成，不阻塞

## 流程

1. **提示词**：调度 **cinematographer** agent 产出 `04-footage/ep{NN}/shotlist.json`
   （逐镜头：模式、提示词、引用图、**时长**、模型、**分辨率**；导演标为长镜的行用时间码译成 8-15s 多节拍，一行一片、别译窄成 4s 碎片）
   - 三种即梦模式认名：全能参考=`multimodal2video`、智能多帧=`multiframe2video`、首尾帧=`frames2video`
   - **认领白模**：Glob `03-previz/ep{NN}/*-blockout.mp4`，有白模的镜头一律走 `multimodal2video`，
     白模进 `videos`、标 `blockout` 字段，提示词按"白模三句式"（复刻句/分工句/**禁灰面句**）写——
     漏禁灰面句会把 3D 灰模质感复刻进成片，属必回炉（见 cinematographer 白模专章）
1.5. **关键帧 prep（仅当 shotlist 有 `keyframes_needed` 时）**：`frames2video`/`multiframe2video` 需要镜头专属关键帧。
   若某镜 `keyframes_needed` 非空，先调度 **art-director** agent 用 Gemini 出图（**Gemini 免费、不耗即梦积分**、走水印清理），
   产物落 `03-design/keyframes/`，比例须与本集 ratio 一致；出齐并肉眼复查后再进报价。
   - **积分红线**：Gemini 出关键帧不耗积分，可在门禁③前做；**但若 Gemini 不可用降级到 `dreamina text2image`（耗即梦积分），
     不得静默扣分**——把关键帧出图的预估积分一并计入门禁③报价，随视频生成一起让用户确认
   - （标了 `first_from_prev` 的衔接首帧不在此步——它由视频生成师在生成时用 ffmpeg 从上一镜抽尾帧，无需出图、免费）
2. **报价（门禁③）**：调度 **producer** agent：
   - `dreamina user_credit` 查当前余额
   - 汇总待生成任务：N 个镜头、**总时长与时长分布**（提醒：时长越长越贵，长镜集中在情绪/定场镜合理，若全片过长要和用户确认）、各模式/模型/**分辨率**分布
   - **含白模/视频参考的镜头数单列一行**：白模渲制本身不耗即梦积分，但视频参考位按即梦规则可能加价；
     历史没记过这类单价就照实说"该项单价未知，建议先拿 1 个白模镜校准"，别混进普通镜头一起估
   - 报积分预估：project.json 的 credits.notes 里有历史单价就据此估算；没有则如实说"单价未知"，
     建议先只生成 1 个镜头校准单价
   - 用 AskUserQuestion 问用户：**全部生成 / 先生成 1 镜校准 / 调整方案（换更省的模型、缩短长镜、减镜头）/ 取消**
3. **执行**：用户确认后，调度 **video-generator** agent（明确告知"门禁③已确认，授权生成镜头范围：…"）：
   批量提交 → 轮询 → 下载 → **可用性质检（ffprobe：完整性/时长/画幅/音轨；音轨按 mode 判定——静音模式 multiframe2video 不要求音轨、缺音轨不重生成）** → 通过才收货为
   `04-footage/ep{NN}/sh{NN}.mp4`、置 status=success → 实时更新 shotlist.json（不可用按传输/内容分类重试）
4. **收尾**：汇报成功/失败清单和实际积分消耗（写入 project.json credits）；
   status.footage → done（有 failed 镜头则保持 in_progress 并列出）
5. 提示下一步：`/review` 质检

## 硬性规则

- 门禁③未确认，任何人不得提交生成任务
- "先生成 1 镜校准"路径：完成后用实际消耗重新报价剩余镜头，再次确认后继续
