# 更新日志

本工作台遵循[语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号**：不兼容的流程/目录结构变更（老项目需要迁移）
- **次版本号**：新增 agent、命令或能力（向下兼容）
- **修订号**：修复与文档完善

每次升级：更新 `VERSION` → 在此记录变更 → `git tag v<版本> && git push --tags`。

## [1.3.0] - 2026-07-13

### 新增
- **插件化**：仓库改造为标准 Claude Code 插件 + 自托管 marketplace（`.claude-plugin/plugin.json` + `marketplace.json`），
  支持命令行安装：`claude plugin marketplace add zq940222/Claude-Code-Short-Drama-Studios` →
  `claude plugin install short-drama-studio@short-drama-studio`
- `/new-drama` 新增工作区初始化：首次建项自动把创作规范（`templates/workspace-CLAUDE.md`）和
  `tools/concat.ps1` 复制进用户工作目录（插件的 CLAUDE.md 不会被自动加载，以此机制替代）

### 变更
- 目录结构：`.claude/agents/` → `agents/`，`.claude/skills/` → `skills/`（插件标准布局）
- 仓库根 CLAUDE.md 改为插件开发说明；工作台创作规范移至 `templates/workspace-CLAUDE.md`
- 发布流程：VERSION、plugin.json、marketplace.json 三处版本号保持一致

## [1.2.0] - 2026-07-13

### 新增
- **finalcut 精剪师 agent + `/finalcut` 命令**：pyJianYingDraft 自动生成剪映草稿（镜头序列+转场、BGM 对位、台词字幕轨 SRT、全局滤镜），剪映中微调导出
- **operator 运营 agent + `/publish` 命令**：发布文案（候选标题/话题标签/发布时段）、封面图（抽帧+大字标题）、半自动发布抖音创作者中心
- 门禁④：发布前用户确认（发布不可撤回）
- 目录规范新增 `06-publish/ep{NN}/`；`requirements.txt`

### 说明
- 剪映版本约束：5.9 草稿兼容最完整，≤6.8 支持自动导出，新版草稿加密支持有限

## [1.1.0] - 2026-07-13

### 修正
- **保留即梦原声**：Seedance 生成的视频自带声音（台词/音效），`tools/concat.ps1` 重写为保留音轨并统一 AAC 48kHz，无音轨片段自动补静音（原版本 `-an` 会丢音轨）
- 交付边界修正：`/edit` 定位为粗剪预览 + 精剪交付包

### 新增
- **composer 配乐师 agent + `/music` 命令**：Suno 网页端生成 BGM + 对位说明，可与生成/审片并行

## [1.0.0] - 2026-07-10

### 新增
- 初始搭建：8 个影视专业 agent（制片人/编剧/导演/美术指导/摄影指导/视频生成师/剪辑师/审片人）
- 8 个阶段命令：/new-drama /script /storyboard /design /shoot /review /edit /studio-status
- 三道门禁（剧本定稿/设定图定稿/积分报价）与防烧钱机制
- 引擎分工：设定图走 Gemini 网页端，视频走即梦 Seedance 2.0，拼接走 ffmpeg
- 项目目录规范与 `tools/concat.ps1`
