# 插件下沉到 plugins/ 子目录 + 双 marketplace 清单（Codex 一键安装）

为了让同一份插件在 Claude Code 与 OpenAI Codex CLI 上都能一键安装，我们把插件本体从仓库根**下沉到
`plugins/film-studio/`**，仓库根只保留两份 marketplace 清单：`.claude-plugin/marketplace.json`（Claude Code）
与 `.agents/plugins/marketplace.json`（Codex）。插件 manifest 仍是**唯一一份** `plugins/film-studio/.claude-plugin/plugin.json`
——Codex 的清单发现顺序是 `.codex-plugin/` → `.claude-plugin/` → `.cursor-plugin/`，会直接复用它。

在 codex-cli 0.139.0 上用隔离 `CODEX_HOME` 实测得到的三条硬约束决定了这个形状：

1. Codex **不读** `.claude-plugin/marketplace.json`（换成 Codex schema 放在该路径也读不到），只读 `.agents/plugins/marketplace.json`，
   且 `plugins[].source` 必须是对象（`{"source":"local","path":"..."}`）而非字符串
2. Codex 要求插件位于 marketplace 根的**子目录**：`"path": "./"`、`"."`、`"../<自身>"` 全部被拒（`codex plugin list` 报 No marketplace plugins found），
   而原仓库正是 `source: "./"` 的自托管形态 —— 这是必须改结构的根因
3. `skills/*/SKILL.md` 无需任何声明即被 Codex 发现并以 `film-studio:<name>` 进入模型 prompt；
   但插件根 `agents/*.md` **不会**被加载为 Codex 子代理（`$CODEX_HOME/agents/` 同样不加载）

## Considered Options

- **保持 `source: "./"` 自托管，Codex 用户手工复制 `skills/`+`agents/` 到 `$CODEX_HOME/`**：零结构改动、实测可用（相对路径 `../../agents/<x>.md` 恰好成立），
  但没有版本管理与更新命令，也拿不到插件命名空间 — 拒绝（降级为 README 里的备选装法）
- **为 Codex 单独建一个 wrapper 仓库**：主仓库不动，但插件本体要么复制要么 submodule，双份漂移 — 拒绝
- **插件下沉到子目录 + 两份 marketplace 清单（选定）**：两个运行时都是官方安装命令；代价是主版本级的目录变更，
  且已装用户须重新 `marketplace add`
- **顺带补一份 `.codex-plugin/plugin.json` 承载 Codex 的 `interface` UI 元数据**：能让 Codex 插件卡片更好看，
  但 Codex 优先读 `.codex-plugin/`，等于把 manifest 变成两份、版本号多一个漂移点 — 拒绝
  （`interface` 塞进 `.claude-plugin/plugin.json` 会让 `claude plugin validate --strict` 报未知字段，也拒绝）

## Consequences

- **发布检查表从三处版本号变四处**：`VERSION`、`plugins/film-studio/.claude-plugin/plugin.json`、
  `.claude-plugin/marketplace.json` 的 `metadata.version`，外加两份 marketplace 的插件条目必须同步增删；
  校验也从一条变两条（`claude plugin validate .` 与 `claude plugin validate plugins/film-studio --strict`）
- **`renames` 只在 Claude 侧**：Codex 的 marketplace schema 没有 renames 语义，旧名 `short-drama-studio` 的迁移只对 Claude Code 用户成立
- **"插件根 = 本技能目录上两级"的约定不变**：`skills/<name>/SKILL.md` 上两级仍是插件根（含 `tools/`、`templates/`、`agents/`），
  所有技能与 agent 里的相对路径无需改写
- **Codex 上全流程跑在单上下文**：12 个 agent 只能走技能里既有的降级路径（读 `agents/<X>.md` 当工作规范就地执行），
  没有并行、上下文占用更大；因此每个 SKILL.md 的"运行时适配"块从可选文档升级为 **Codex 可用性的必要条件**，新增技能必须照抄
- **门禁在 Codex 上是对话式的**：无 AskUserQuestion 工具，四道门禁降级为对话提问 + 等待回复，语义不变但没有结构化选项 UI
- **仓库层文件（README/CHANGELOG/docs/requirements.txt）不进插件**：插件 bundle 体积更小，但 `requirements.txt` 对插件用户不可见，
  pyJianYingDraft 的安装说明必须留在 README 与精剪技能正文里
