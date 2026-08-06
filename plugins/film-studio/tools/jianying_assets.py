#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""jianying_assets.py — 剪映素材枚举/检索工具（供 finalcut 精剪师查真实可用素材名）

pyJianYingDraft 内置海量素材（转场 450+、滤镜 1000+、特效 1000+、入出场动画各百余种）。
本脚本直接从已装库读取**当前版本真实可用**的素材枚举名，避免用到不存在的名字导致草稿报错。
精剪师写草稿前，按需检索对应类别 + 情绪关键词，从结果里挑，再写进 pyJianYingDraft 代码。

用法：
  python tools/jianying_assets.py transition --grep 闪黑      # 搜转场里含"闪黑"的
  python tools/jianying_assets.py filter --grep 冷,暗,电影     # 逗号=任一关键词
  python tools/jianying_assets.py intro                       # 列全部入场动画名
  python tools/jianying_assets.py list                        # 列出所有可查类别
"""
import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 类别 → pyJianYingDraft 枚举类名
CATS = {
    "transition": "TransitionType",          # 转场（片段之间）
    "intro": "IntroType",                     # 片段入场动画
    "outro": "OutroType",                     # 片段出场动画
    "group-anim": "GroupAnimationType",       # 组合动画
    "filter": "FilterType",                   # 滤镜/调色
    "effect": "VideoSceneEffectType",         # 画面特效（场景）
    "char-effect": "VideoCharacterEffectType",# 人物特效
    "text-intro": "TextIntro",                # 字幕入场
    "text-outro": "TextOutro",                # 字幕出场
    "text-loop": "TextLoopAnim",              # 字幕循环动画
    "mask": "MaskType",                       # 蒙版
    "audio-effect": "AudioSceneEffectType",   # 音频场景音效
    "tone": "ToneEffectType",                 # 音色
}

def main():
    ap = argparse.ArgumentParser(description="检索剪映（pyJianYingDraft）真实可用素材名")
    ap.add_argument("category", help="素材类别；用 list 查看全部类别")
    ap.add_argument("--grep", default=None, help="关键词过滤，逗号分隔=任一命中")
    a = ap.parse_args()

    if a.category == "list":
        print("可查类别：")
        for k, v in CATS.items():
            print(f"  {k:14s} → {v}")
        return

    if a.category not in CATS:
        sys.exit(f"未知类别 '{a.category}'；用 `python tools/jianying_assets.py list` 查看可用类别")

    try:
        import pyJianYingDraft as d
    except ImportError:
        sys.exit("未安装 pyJianYingDraft；先 `python -m pip install pyJianYingDraft`")

    enum = getattr(d, CATS[a.category], None)
    if enum is None:
        sys.exit(f"当前 pyJianYingDraft 版本无 {CATS[a.category]}（库升级后枚举可能改名）")

    names = [m.name for m in enum]
    if a.grep:
        kws = [k.strip() for k in a.grep.split(",") if k.strip()]
        names = [n for n in names if any(k in n for k in kws)]

    print(f"# {a.category}（{CATS[a.category]}）匹配 {len(names)} 项"
          + (f"，关键词: {a.grep}" if a.grep else "，全部") + "：")
    for n in names:
        print(n)

if __name__ == "__main__":
    main()
