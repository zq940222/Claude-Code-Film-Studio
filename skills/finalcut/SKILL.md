---
name: finalcut
description: 精剪阶段。调度精剪师 agent 自动组装精剪工程——检测到 DaVinci Resolve Studio（推荐）走官方 API 建时间线并可自动渲染；否则默认生成剪映草稿（pyJianYingDraft）。镜头+转场、BGM 对位、台词字幕、滤镜一次组装。用户说"精剪"、"剪映剪辑"、"达芬奇剪辑"、"加字幕"、"/finalcut"时使用。
---

# /finalcut 精剪

## 前置检查

- 本集全部镜头 status=success（粗剪 /edit 做过更好，但非必需——精剪直接用原始镜头）
- BGM 未生成时提示先跑 `/music`（也可选择无 BGM 继续，字幕和转场照做）

## 流程

1. 调度 **finalcut** agent，它会自动选择工具：
   - **检测到 DaVinci Resolve Studio 可连接** → 告知用户"推荐用 Resolve（可自动渲染导出成片）"，
     确认后用官方 Python API 建工程：时间线（镜头序列）、BGM 音轨对位、字幕（SRT）、调色建议；
     用户检查时间线后可授权自动渲染到 `05-final/`
   - **未检测到** → 静默走剪映路径（不推销 Resolve）：pyJianYingDraft 生成剪映草稿
     （视频轨+场间转场、BGM 轨压低音量、字幕轨、全局滤镜），用户在剪映中微调导出
   - 按 project.json 的 `editing` 块处理增强选项（默认全关跳过）：集间交叉衔接、片头/片尾卡，字幕时间轴相应偏移
2. 向用户报告工程名称/位置和三个常见微调点：转场、字幕断句、BGM 音量
3. 用户确认导出成片后，更新 project.json：status.final → done
4. 提示下一步：`/publish` 发布到平台

## 注意

- 剪映版本约束：草稿生成对 5.9 支持最完整；自动导出仅 Windows + ≤6.8；新版剪映草稿加密，失败时退回 /edit 粗剪 + 手动精剪
- Resolve 外部脚本控制需要 Studio 付费版；免费版/未运行时一律走剪映
- 素材用绝对路径写入工程，提醒用户别移动项目目录，否则工程里素材丢失
