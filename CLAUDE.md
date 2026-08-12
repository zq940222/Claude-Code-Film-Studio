# film-studio 插件源码仓库

本仓库是插件 **film-studio（影视工作台，原 short-drama-studio）** 的源码，同时是它的自托管 marketplace。
自 v3.0.0 起插件本体下沉到 `plugins/film-studio/`，仓库根同时提供两份 marketplace 清单：
Claude Code 读 `.claude-plugin/marketplace.json`，Codex CLI 读 `.agents/plugins/marketplace.json`（见 `docs/adr/0004`）。

在这里工作 = 开发插件本身；实际创作（短剧/电影短片/动漫番剧/创意段子）应在独立工作目录进行（安装插件后 `/new-drama` 建项，工作区规范由 `templates/workspace-CLAUDE.md` 复制生成）。

## 仓库结构

```
.claude-plugin/marketplace.json         # Claude Code marketplace（source 指向 ./plugins/film-studio；renames 保留旧名映射）
.agents/plugins/marketplace.json        # Codex marketplace（同一插件，source 必须写成对象形式）
plugins/film-studio/                    # 插件本体（bundle 边界，仓库层文件不进插件）
  .claude-plugin/plugin.json            # 唯一一份插件 manifest（Codex 也复用它；版本号必须随发布更新）
  agents/                               # 12 个专业 agent（插件标准路径）
  skills/                               # 12 个阶段命令 + 4 份规范技能（seedance-prompt/edit-rhythm/sound-design/subtitle-craft）
  schemas/                              # project.json 与 shotlist.json 的结构定义（建项时复制为工作区 tools/schemas/）
  tools/                                # concat.py + clean_refimg.py + jianying_assets.py + blender_blockout.py + validate_project.py 跨平台脚本（/new-drama 建项时复制进工作区）
  templates/workspace-CLAUDE.md         # 工作区规范模板（/new-drama 建项时复制为工作区 CLAUDE.md）
scripts/ci_check.py                     # 仓库结构自检（CI 用，仓库层，不进插件 bundle）
.github/workflows/ci.yml                # CI：结构自检 + schema 自检 + claude plugin validate
requirements.txt                        # Python 依赖（pyJianYingDraft）——仓库层，插件用户看不到，安装说明须留在 README 与精剪技能里
docs/adr/                               # 架构决策记录
docs/superpowers/specs/                 # 设计文档（含修订记录）
```

## 修改插件的规则

1. **工作台创作规范只改 `plugins/film-studio/templates/workspace-CLAUDE.md`**（仓库根的本 CLAUDE.md 不会被插件用户加载，只服务于仓库开发）
2. skills 引用插件内文件时用相对于技能目录的路径（如 `../../tools/concat.py`，上两级恒等于插件根，与插件放在哪层无关）；agents 不知道插件根位置，凡是 agent 要用的文件必须在建项时复制进工作区
   - **新增 `tools/` 脚本或 `schemas/` 文件时，必须同步挂进 `skills/new-drama/SKILL.md` 第 0 步的复制清单**——
     漏挂不会报错，只会让功能在工作区里静默失效。`scripts/ci_check.py` 守着这条
3. **跨平台约束**：工具脚本只用 Python（stdlib）+ ffmpeg，禁止 PowerShell/bash 专属脚本；agent/skill 里的命令示例须两平台通用（正斜杠路径），平台差异处显式写明 Windows/macOS 两种写法
   - 唯一例外是 `tools/blender_blockout.py` 用 `bpy`（**Blender 自带的 Python 模块，不需 pip 装包**，仍是零第三方依赖）；
     它必须保留不依赖 Blender 的 `--validate` 纯校验路径，且 Blender 作为**可选依赖**——任何 Blender 缺失场景都要能优雅跳过（见 `docs/adr/0003`）
4. **创作形态**：`project.json.format.medium`（short-drama/short-film/anime/sketch）驱动编剧/导演/美术/摄影/运营的法则切换；新增形态相关能力时四种形态都要覆盖。商单机制（sponsor brief）与形态解耦（见 `docs/adr/0002`），改商单相关能力时对所有形态生效
5. **跨运行时兼容**：每个 SKILL.md 必须保留"运行时适配"块（subagent 降级为读 agents/*.md、AskUserQuestion 降级为对话询问）；新增技能时照抄该块——Codex CLI 只加载 `skills/`、**不把 `agents/*.md` 当子代理**，这个块是它可用性的必要条件（同样服务 OpenClaw 等 bundle 安装的运行时）
   - 双 marketplace 必须同步：新增/改名插件条目时两份清单一起改；Codex 侧 `source` 只接受对象形式，且**插件必须在子目录**（`"./"` 自托管会被拒），所以插件不能搬回仓库根
   - 每个 SKILL.md 还必须有**交付自检块**（可机械判定的通过判据）；`scripts/ci_check.py` 守着这两块
6. **数据结构的单一真源是 `plugins/film-studio/schemas/`**：改 `project.json` / `shotlist.json` 的结构时，
   先改 schema，再同步 producer.md / cinematographer.md 里的示例与说明。校验器
   （`tools/validate_project.py`）只实现 JSON Schema 的一个受支持子集，写 schema 只能用
   `SUPPORTED_KEYWORDS` 里的关键字——`--schema-lint` 会在 CI 里拦住用了不支持关键字的 schema
   （那会让校验静默失效）。新增跨文件语义检查时，一并在 `--self-test` 里加断言
7. **每次发布**：更新 `VERSION` + `plugins/film-studio/.claude-plugin/plugin.json` 的 version + `.claude-plugin/marketplace.json` 的 `metadata.version`（三处一致）→ 记 `CHANGELOG.md` → 四条校验通过（见规则 9）→ 提交 → `git tag v<版本>` → 推送（含 tags）
8. 语义化版本：主=不兼容的流程/目录结构/命名变更；次=新增 agent/命令/能力；修订=修复与文档
9. 本地验证（CI 跑的是同样四条，提交前本地先过）：
   ```bash
   python3 scripts/ci_check.py
   python3 plugins/film-studio/tools/validate_project.py --schema-lint
   python3 plugins/film-studio/tools/validate_project.py --self-test
   ```
   加上 `claude plugin validate .` + `claude plugin validate plugins/film-studio --strict`；
   本地试装 Claude Code：`claude plugin marketplace add <本仓库路径>` 后 `claude plugin install film-studio@film-studio`；
   本地试装 Codex（建议 `CODEX_HOME=<临时目录>` 隔离，别污染真实配置）：`codex plugin marketplace add <本仓库路径>` 后 `codex plugin add film-studio@film-studio`，
   用 `codex debug prompt-input` 确认 16 个技能以 `film-studio:<name>` 出现

## Agent skills

### Issue tracker

Issue 跟踪在本仓库的 GitHub Issues（通过 `gh` CLI 读写）。See `docs/agents/issue-tracker.md`.

### Triage labels

使用五个默认 triage 标签：needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix。See `docs/agents/triage-labels.md`.

### Domain docs

单上下文布局：根目录 `CONTEXT.md` + `docs/adr/`。See `docs/agents/domain.md`.
