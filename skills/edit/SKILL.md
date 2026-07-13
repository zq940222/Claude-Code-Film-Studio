---
name: edit
description: 粗剪交付阶段。调度剪辑师 agent 用 ffmpeg 统一转码、按分镜顺序拼接粗剪预览（保留即梦原声），整理精剪交付包（原始镜头+BGM+台词本）供剪映/PR 使用。用户说"剪辑"、"合成"、"出片"、"/edit"时使用。
---

# /edit 粗剪与交付

## 前置检查

- shotlist.json 中本集全部镜头 status=success（或用户在 /review 明确放行）；有缺口先报告

## 流程

0. 工作区缺 `tools/concat.py` 时，先从插件根（本技能目录上两级）的 `tools/concat.py` 复制过来
1. 调度 **editor** agent：
   - 按 shotlist 顺序统一转码 + 拼接（用工作区 `tools/concat.py`，跨平台，**保留即梦原声音轨**）
   - 按 project.json 的 `editing` 块处理增强选项（默认全关跳过）：集间交叉衔接（上集结尾几秒置顶）、片头/片尾卡
   - 输出粗剪 `05-final/<剧名>-ep{NN}-粗剪.mp4`
   - ffprobe 校验时长/规格/含音频流，抽首中尾 3 帧确认画面
   - 整理精剪交付包清单 `05-final/delivery-ep{NN}.md`（粗剪 + 原始镜头 + BGM + 台词本）
2. 向用户报告粗剪路径、时长、分辨率，展示抽帧；BGM 尚未生成的提醒可运行 `/music`
3. 更新 project.json：status.final → done
4. 收尾提示：拿交付包进剪映/PR 精剪——配乐混音（BGM 对位见 bgm-notes.md）、字幕（台词本）、
   转场调色；若是多集项目，提示继续下一集
