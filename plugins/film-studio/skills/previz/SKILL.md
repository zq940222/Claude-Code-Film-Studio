---
name: previz
description: 白模预演阶段（可选）。调度白模师 agent 用 Blender 给复杂镜头搭白模（blockout）、渲成运镜参考视频，供即梦全能参考 @video 复刻运镜与空间关系。用户说"做白模"、"预演"、"锁运镜"、"/previz"时使用。
---

# /previz 白模预演（可选阶段，不消耗即梦积分）

给**复杂运镜/精确空间/明确走位**的镜头搭 Blender 白模（灰白代理几何体 + 相机动画），
渲成白模参考视频，让即梦 `multimodal2video` 照着它复刻运镜——把"提示词描述运镜、AI 靠猜"
换成"给它看一遍怎么走"。**白模只锁运镜与空间，风格仍由 STYLE LOCK + 设定图承载。**

## 运行时适配（跨 Agent 兼容）

- **支持 subagent 的运行时**（Claude Code / Hermes Agent 等）：按下文"调度 xxx agent"正常派发子代理执行
- **不支持 subagent 的运行时**（Codex CLI / OpenClaw 等，以插件 bundle 方式安装）：正文提到"调度 X agent"时，
  改为读取插件根 `agents/<X>.md`（本技能目录上两级），以其为工作规范在当前上下文直接执行，效果等同
- **用户确认处**：有 AskUserQuestion 工具就用；没有则直接在对话中提问并等待用户回复，门禁语义不变

## 前置检查

- `project.json` 的 `status.storyboard` 必须是 `done`（白模按分镜的运镜/时长/走位搭，没分镜无从下手）
- **探测 Blender**（跨平台）：`blender --version`；不在 PATH 时试常见位置——
  Windows `C:/Program Files/Blender Foundation/Blender */blender.exe`、macOS `/Applications/Blender.app/Contents/MacOS/Blender`
  - **没装 Blender**：如实告知"白模需要 Blender 3.6+（免费，blender.org）"，用 AskUserQuestion 问用户
    **装了再来 / 跳过白模直接走 /design**；选跳过就把 `status.previz` 置 `skipped` 并明确说明
    "跳过白模不影响任何后续流程，复杂运镜改由提示词表达（AI 执行稳定性略低）"，然后提示 `/design`
- 工作区 `tools/blender_blockout.py` 必须存在（建项时由插件复制）；缺失则从插件根 `tools/` 补一份

## 流程

1. **选镜（先谈清单再动手）**：调度 **previz-artist** agent 读分镜表，按其选镜标准挑出值得做白模的镜头，
   逐镜给"为什么值得做"，用 AskUserQuestion 请用户确认清单（可增可减）
   - 典型比例一集 10%-30%（1-4 镜）：复杂运镜 / 三人以上纵深站位 / 明确走位 / 一镜到底长镜 /
     同场景多机位要空间对齐 / 之前回炉过"运镜没照做"的镜头
   - **本阶段零即梦积分消耗**，不属门禁③；但会改变这些镜头的生成参数（多一路 `@video` 参考），所以要用户点头
2. **写规格 + 校验**：previz-artist 产出 `03-previz/ep{NN}/blockout.json`，跑免费自检：
   ```bash
   python tools/blender_blockout.py --spec "projects/<剧名>/03-previz/ep01/blockout.json" --validate
   ```
3. **渲染白模**：
   ```bash
   blender -b --factory-startup -P tools/blender_blockout.py -- --spec "projects/<剧名>/03-previz/ep01/blockout.json" --out-root "projects/<剧名>"
   ```
   产物 `03-previz/ep{NN}/sh{NN}-blockout.mp4`（画幅=本集 ratio、时长=该镜 duration、无音轨、纯灰白）
4. **自检**：逐段 ffprobe 核对时长/画幅，并**抽帧用 Read 看图**确认主体在画幅内、景别与分镜一致（详见 previz-artist 规范）；
   不合格改规格用 `--only sh{NN}` 重渲（免费，别拖到生成时才发现）
5. **交接**：previz-artist 写 `03-previz/ep{NN}/previz-report.md`（逐镜"白模锁了什么"+ 给摄影指导的提示），
   更新 `project.json` 的 `status.previz` → `done`
6. 提示下一步：设定图未做 → `/design`；已做 → `/shoot`（摄影指导会把白模写进 shotlist 的 `blockout`/`videos` 字段）

## 回炉用法（审片说"运镜没照做"时最值钱）

`/review` 审出「运镜执行差」「切镜没执行」「空间关系错」这类回炉原因、且提示词已改过一轮仍不行时：
回本命令**只给那几镜补白模**（`--only`），然后走 `/shoot` 重生成——比继续改第三版提示词有效得多。

## 注意

- 白模是**可选阶段**：跳过不影响流水线，四道门禁不变（白模不新增门禁）
- 白模视频占用 `multimodal2video` 的视频参考位（`--video`，最多 3 个）；一镜通常只用 1 个白模
- **视频参考位按即梦规则可能加价**，报价时由制片人如实计入门禁③（见 /shoot）
- 老项目 `project.json` 没有 `status.previz` 字段属正常（视为未做），由 producer 补写
- Blender 只在本阶段用到；不装 Blender 的用户全流程其余部分不受任何影响

## 交付自检（本阶段通过的判据）

白模错了会连累它锁的那些镜头**全部白烧积分**，而重渲白模是免费的——所以这里宁可多查一遍：

- [ ] 每个 `sh{NN}-blockout.mp4` 与该镜**同画幅、同时长**（用 ffprobe **实测**，不是照 `blockout.json` 假设）
- [ ] 抽帧用 Read 看过：主体在画幅内、景别与分镜一致、运镜走向与分镜描述一致
- [ ] 白模是纯灰白无材质（带材质会诱导 Seedance 连质感一起复刻）
- [ ] `previz-report.md` 逐镜写了"这个白模锁了什么"，摄影指导据此写三句式
- [ ] `status.previz` 是 `done` 或 `skipped`，不留在 `pending`
- [ ] 本阶段**零即梦积分消耗**（有任何积分支出说明走错了路径）
