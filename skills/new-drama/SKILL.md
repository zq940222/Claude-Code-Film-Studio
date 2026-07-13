---
name: new-drama
description: 新建短剧项目。收集剧名、题材、画幅（9:16/16:9）、每集时长、集数，创建标准项目目录和 project.json。用户说"新建短剧"、"开新项目"、"/new-drama"时使用。
---

# /new-drama 建项

## 第 0 步：工作区初始化（只做一次）

本技能目录的上两级是插件根目录（含 `templates/` 和 `tools/`）。检查当前工作目录：

- 无 `CLAUDE.md` → 把插件根的 `templates/workspace-CLAUDE.md` 复制为工作区 `./CLAUDE.md`（工作台创作规范，之后会话自动加载）；已有 CLAUDE.md 则展示规范要点提示用户手动合并，**不要覆盖**
- 无 `tools/concat.ps1` → 把插件根的 `tools/concat.ps1` 复制为工作区 `./tools/concat.ps1`（剪辑师拼接要用）
- 检查 `python -c "import pyJianYingDraft"`，失败则提示 `python -m pip install pyJianYingDraft`（/finalcut 精剪要用，可先跳过不阻塞建项）

## 流程

1. 用 AskUserQuestion 收集（用户在参数里已给的不重复问）：
   - **剧名**（可暂定）
   - **题材**：都市逆袭 / 甜宠 / 悬疑 / 玄幻 / 其他
   - **画幅**：9:16 竖屏（抖音/快手）或 16:9 横屏（B站/YouTube）
   - **每集时长**：竖屏推荐 60-120 秒，横屏推荐 180-300 秒
   - **集数**：建议先做 1 集试水验证流程，再批量
2. 调度 **producer** agent 建项：创建 `projects/<剧名>/` 全套目录（01-script、02-storyboard、
   03-design/characters、03-design/scenes、04-footage、05-final）和 project.json
3. 顺带查一次 `dreamina user_credit` 报告余额
4. 告知用户下一步：运行 `/script` 开始剧本创作；如果用户已带来了故事想法，直接问是否现在进入剧本阶段

## 注意

- 剧名会成为目录名：过滤 Windows 非法字符（`\ / : * ? " < > |`）
- 若同名项目已存在，停下询问是续作、覆盖还是换名
