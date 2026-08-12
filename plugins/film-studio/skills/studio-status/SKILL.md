---
name: studio-status
description: 工作台总览。列出所有短剧项目的阶段进度、待办门禁、即梦积分余额和未完成的生成任务。用户说"项目进度"、"工作台状态"、"/studio-status"时使用。
---

# /studio-status 工作台总览

## 运行时适配（跨 Agent 兼容）

- **支持 subagent 的运行时**（Claude Code / Hermes Agent 等）：按下文"调度 xxx agent"正常派发子代理执行
- **不支持 subagent 的运行时**（Codex CLI / OpenClaw 等，以插件 bundle 方式安装）：正文提到"调度 X agent"时，
  改为读取插件根 `agents/<X>.md`（本技能目录上两级），以其为工作规范在当前上下文直接执行，效果等同
- **用户确认处**：有 AskUserQuestion 工具就用；没有则直接在对话中提问并等待用户回复，门禁语义不变


## 流程

1. Glob 扫描 `projects/*/project.json`，逐个读取
2. 跑一次档案校验，把结构性问题在这里就暴露出来（比等到 `/shoot` 白烧积分强）：
   - 工作区缺 `tools/validate_project.py` 或 `tools/schemas/` → 先从插件根（本技能目录上两级）的
     `tools/validate_project.py` 与 `schemas/` 复制过来（后者复制为工作区 `tools/schemas/`）；
     **v3.1.0 之前建的工作区都没有这两项**，补齐即可，不必重跑 `/new-drama`
   ```bash
   python tools/validate_project.py
   ```
   （Windows 用 `python`，macOS 用 `python3`。有 ERROR 就在总览下方单列一节列出，并说明该跑哪个命令去修）
3. `dreamina user_credit` 查积分余额
4. 扫描各项目 shotlist.json 中 status=submitted 的镜头（提交了但没等到结果的），
   用 `dreamina query_result --submit_id=<id>` 补查一次，能收割的顺手下载并更新状态
5. 读各项目 `history/gates.jsonl`（有就读）确认门禁进度，与 `status` 交叉核对
6. 输出总览表：

```
| 项目 | 画幅 | 集数 | 剧本 | 分镜 | 白模 | 设定 | 生成 | 成片 | 下一步 |
|---|---|---|---|---|---|---|---|---|---|
| 龙王归来 | 9:16 | 1 | ✅ | ✅ | ⏭ 跳过 | ✅ | 8/12 | - | /shoot 补 4 镜 |
| 暗巷 | 16:9 | 1 | ✅ | ✅ | ✅ 3镜 | ✅ | - | - | /shoot |

积分余额：14200
| 项目 | 已核销 | 预留未用 | 单价可信度 |
|---|---|---|---|
| 龙王归来 | 320 | 80 | 已校准（4 镜样本，约 80/镜） |
| 暗巷 | 0 | 0 | 未校准——首次报价须先拿 1 镜校准 |
```

- 白模列读 `status.previz`：`✅ N镜`（done，N = `03-previz/ep*/`下的 `*-blockout.mp4` 数）／`⏭ 跳过`（skipped 或没装 Blender）／`-`（pending；分镜里有 `【白模】` 标注时提示"可走 /previz"）。**白模是可选阶段，`-` 或 `⏭` 都不算卡住**
- 积分表读 `ledger`：已核销 = `entries` 里 `kind=actual` 合计；预留未用 = `reserve` 合计 − `actual` 合计 − `release` 合计；
  可信度读 `unit_price.confidence`，`unknown` 一律显示"未校准"并提醒首次报价要先校准。老项目没有 `ledger` 块时回落到 `credits.spent` 并注明"无账本明细"

7. 明确指出每个项目卡在哪个门禁/阶段、建议的下一条命令；
   **中断恢复**：若某项目有 `status=submitted` 的镜头或 `reserve` 大于 `actual`，说明上次是在生成中途断的——
   先收割（第 4 步）再据实补 `actual`/`release` 流水，然后才提示下一步，不要让用户重复付一次积分

## 交付自检（本阶段通过的判据）

- [ ] 跑过 `validate_project.py`；有 ERROR 的项目已单列一节，并写清该跑哪个命令去修
- [ ] 每个项目都明确指出了**卡在哪个门禁/阶段**和**下一条命令**，没有含糊的"进行中"
- [ ] 挂起的 `submitted` 镜头都尝试收割过（`dreamina query_result`），能下的已下并更新状态
- [ ] 积分表三列都填了；`confidence` 为 `unknown` 的项目明确标注"未校准，首次报价须先校准"
- [ ] 本命令**只读不写生成任务**：除了收割已提交任务与补记流水，没有触发任何新的耗积分动作
