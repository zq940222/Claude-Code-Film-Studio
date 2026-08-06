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
2. `dreamina user_credit` 查积分余额
3. 扫描各项目 shotlist.json 中 status=submitted 的镜头（提交了但没等到结果的），
   用 `dreamina query_result --submit_id=<id>` 补查一次，能收割的顺手下载并更新状态
4. 输出总览表：

```
| 项目 | 画幅 | 集数 | 剧本 | 分镜 | 白模 | 设定 | 生成 | 成片 | 下一步 |
|---|---|---|---|---|---|---|---|---|---|
| 龙王归来 | 9:16 | 1 | ✅ | ✅ | ⏭ 跳过 | ✅ | 8/12 | - | /shoot 补 4 镜 |
| 暗巷 | 16:9 | 1 | ✅ | ✅ | ✅ 3镜 | ✅ | - | - | /shoot |

积分余额：14200（历史单价：约 xx/5s 镜头，见各项目 credits.notes）
```

- 白模列读 `status.previz`：`✅ N镜`（done，N = `03-previz/ep*/`下的 `*-blockout.mp4` 数）／`⏭ 跳过`（skipped 或没装 Blender）／`-`（pending；分镜里有 `【白模】` 标注时提示"可走 /previz"）。**白模是可选阶段，`-` 或 `⏭` 都不算卡住**

5. 明确指出每个项目卡在哪个门禁/阶段、建议的下一条命令
