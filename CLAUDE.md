# film-studio 插件源码仓库

本仓库是 Claude Code 插件 **film-studio（影视工作台，原 short-drama-studio）** 的源码，同时是它的自托管 marketplace（`.claude-plugin/marketplace.json` 中 `source: "./"`，含 `renames` 记录旧名迁移）。

在这里工作 = 开发插件本身；实际创作（短剧/电影短片/动漫番剧）应在独立工作目录进行（安装插件后 `/new-drama` 建项，工作区规范由 `templates/workspace-CLAUDE.md` 复制生成）。

## 仓库结构

```
.claude-plugin/plugin.json      # 插件 manifest（版本号必须随发布更新）
.claude-plugin/marketplace.json # 自托管 marketplace（版本号与 plugin.json 保持一致；renames 保留旧名映射）
agents/                         # 11 个专业 agent（插件标准路径）
skills/                         # 11 个阶段命令（插件标准路径）
tools/                          # concat.py + clean_refimg.py 跨平台脚本（/new-drama 建项时复制进工作区）
templates/workspace-CLAUDE.md   # 工作区规范模板（/new-drama 建项时复制为工作区 CLAUDE.md）
requirements.txt                # Python 依赖（pyJianYingDraft）
docs/superpowers/specs/         # 设计文档（含修订记录）
```

## 修改插件的规则

1. **工作台创作规范只改 `templates/workspace-CLAUDE.md`**（插件根的本 CLAUDE.md 不会被插件用户加载，只服务于仓库开发）
2. skills 引用插件内文件时用相对于技能目录的路径（如 `../../tools/concat.py`）；agents 不知道插件根位置，凡是 agent 要用的文件必须在建项时复制进工作区
3. **跨平台约束**：工具脚本只用 Python（stdlib）+ ffmpeg，禁止 PowerShell/bash 专属脚本；agent/skill 里的命令示例须两平台通用（正斜杠路径），平台差异处显式写明 Windows/macOS 两种写法
4. **创作形态**：`project.json.format.medium`（short-drama/short-film/anime）驱动编剧/导演/美术/摄影/运营的法则切换；新增形态相关能力时三种形态都要覆盖
5. **跨运行时兼容**：每个 SKILL.md 必须保留"运行时适配"块（subagent 降级为读 agents/*.md、AskUserQuestion 降级为对话询问）；新增技能时照抄该块——这保证插件 bundle 能装进 OpenClaw 等非 Claude Code 运行时
6. **每次发布**：更新 `VERSION` + `.claude-plugin/plugin.json` 和 `marketplace.json` 的 version（三处一致）→ 记 `CHANGELOG.md` → `claude plugin validate .` 通过 → 提交 → `git tag v<版本>` → 推送（含 tags）
7. 语义化版本：主=不兼容的流程/目录结构/命名变更；次=新增 agent/命令/能力；修订=修复与文档
8. 本地验证：`claude plugin validate .`；本地试装：`claude plugin marketplace add <本仓库路径>` 后 `claude plugin install film-studio@film-studio`
