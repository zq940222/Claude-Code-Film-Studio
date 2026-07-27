# 可观测性 UI 走独立 TS 应用，不内置于插件

用户需要比 `/studio-status` 对话表格更强的项目可观测性（图形化仪表盘：进度/镜头/产物/积分）。我们决定将其做成独立仓库 [film-studio-dashboard](https://github.com/zq940222)（Vite + React + Express，全 TypeScript 本地 web 应用），启动后选择工作目录即可只读观测其中项目，而不是内置进本插件——因为插件的跨平台约束（CLAUDE.md 规则 3：工具脚本只用 Python stdlib + ffmpeg、零安装依赖）撑不起一个现代 web UI，而放宽该规则会把 Node 工具链强加给所有纯创作用户。

## Considered Options

- **插件内置（Python stdlib http.server + 无构建静态页）**：合规但 UI 能力天花板低，且给插件引入常驻服务的维护面 — 拒绝
- **前端构建产物（dist）入插件仓**：源码/产物双轨、规则 3 需加例外注记 — 拒绝
- **独立 TS 应用（选定）**：技术栈自由、随自身节奏演进；代价是发布/版本与插件双轨

## Consequences

- 仪表盘对工作区**严格只读 + 轻操作**（复制建议命令、`dreamina user_credit` 只读查积分）；绝不调 `query_result`、绝不回写工作区文件——四道门禁的对话确认语义不受影响（术语边界见 [CONTEXT.md](../../CONTEXT.md) 的「仪表盘」「轻操作」条目）
- 插件对仪表盘零依赖、零感知：工作区文件格式（project.json / shotlist.json / 目录规范）是两者之间唯一的隐式契约，插件侧变更这些格式时属破坏性变更，需知会仪表盘适配
