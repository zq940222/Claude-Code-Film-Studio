#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""clean_refimg.py — 设定图水印清理脚本（跨平台：Windows / macOS）

Gemini（Nano Banana）生成的图片右下角带可见水印；设定图作为 multimodal2video 参考图时，
水印会被 Seedance 复刻进视频。设定图入库（03-design/）前必须先用本脚本清理。

两种模式：
  delogo（默认）：用 ffmpeg delogo 修复右下角水印区域，保留完整画面（角落是背景时效果最好）
  crop：直接裁掉底部条带（画面底部无关键内容时用，如场景图天空/地面留白多）

用法：
  python tools/clean_refimg.py --in raw.png --out "03-design/characters/林晚-front.png"
  python tools/clean_refimg.py --in raw.png --out clean.png --mode crop
  python tools/clean_refimg.py --in raw.png --out clean.png --width-pct 0.30 --height-pct 0.12  # 水印偏大时扩大区域
"""
import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows 管道默认 GBK，统一 UTF-8

def main():
    ap = argparse.ArgumentParser(description="清理设定图右下角水印")
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--mode", choices=["delogo", "crop"], default="delogo")
    ap.add_argument("--width-pct", type=float, default=0.20, help="水印区域宽度占比（右下角）")
    ap.add_argument("--height-pct", type=float, default=0.08, help="水印区域/裁剪条带高度占比")
    a = ap.parse_args()

    src, dst = Path(a.src), Path(a.dst)
    if not src.exists():
        sys.exit(f"输入文件不存在: {src}")

    dim = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(src)],
        capture_output=True, text=True).stdout.strip()
    img_w, img_h = (int(x) for x in dim.split(","))

    if a.mode == "delogo":
        # delogo 区域必须完整落在画面内部（不能贴边），四周留 2px
        reg_w = min(int(img_w * a.width_pct), img_w - 4)
        reg_h = min(int(img_h * a.height_pct), img_h - 4)
        x, y = img_w - reg_w - 2, img_h - reg_h - 2
        vf = f"delogo=x={x}:y={y}:w={reg_w}:h={reg_h}"
    else:
        strip = int(img_h * a.height_pct)
        vf = f"crop={img_w}:{img_h - strip}:0:0"

    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(src), "-vf", vf, "-frames:v", "1", "-update", "1", str(dst)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"水印清理失败: {src}\n{r.stderr.strip()}")
    print(f"完成({a.mode}): {dst}（{img_w}x{img_h}，处理区域 {vf}）")
    print("提醒：清理后务必肉眼检查右下角，水印残留时扩大 --width-pct/--height-pct 重跑")

if __name__ == "__main__":
    main()
