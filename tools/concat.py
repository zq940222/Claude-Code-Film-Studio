#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""concat.py — 短剧工作台镜头粗剪拼接脚本（跨平台：Windows / macOS）

先把所有片段统一转码为相同规格（H.264/yuv420p/30fps/统一分辨率 + AAC 48kHz 立体声），再无损 concat。
即梦生成的视频自带声音（台词/音效），音轨全程保留；无音轨的片段自动补静音，保证 concat 不错位。

用法：
  python tools/concat.py --input-dir "projects/剧名/04-footage/ep01" \
      --output "projects/剧名/05-final/剧名-ep01-粗剪.mp4" --ratio 9:16
  python tools/concat.py --input-dir ... --output ... --files sh02.mp4 sh01.mp4   # 自定义顺序
  # --files 也接受绝对路径（如片头/片尾卡），与目录内文件名可混用
"""
import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows 管道默认 GBK，统一 UTF-8

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"命令失败: {' '.join(map(str, cmd))}\n{r.stderr.strip()}")
    return r.stdout.strip()

def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip()
    return bool(out)

def main():
    ap = argparse.ArgumentParser(description="统一转码 + 拼接镜头片段（保留音轨）")
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--ratio", choices=["9:16", "16:9"], default="9:16")
    ap.add_argument("--files", nargs="*", default=None, help="自定义顺序；省略则按 sh*.mp4 文件名排序")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()

    W, H = (1080, 1920) if a.ratio == "9:16" else (1920, 1080)
    indir = Path(a.input_dir)

    clips = ([indir / f for f in a.files] if a.files
             else sorted(indir.glob("sh*.mp4")))
    if not clips:
        sys.exit("InputDir 下没有找到镜头片段（sh*.mp4）")
    for c in clips:
        if not c.exists():
            sys.exit(f"片段不存在: {c}")
    print(f"待拼接 {len(clips)} 个片段（{W}x{H} @ {a.fps}fps，保留音轨）")

    work = indir / "_work"
    work.mkdir(exist_ok=True)
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={a.fps}")
    acodec = ["-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k"]
    vcodec = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(a.crf), "-preset", "medium"]

    normalized = []
    for i, clip in enumerate(clips, 1):
        out = work / f"{i:03d}_{clip.name}"
        silent = not has_audio(clip)
        print(f"[{i}/{len(clips)}] 转码 {clip.name}{'（无音轨，补静音）' if silent else ''} ...")
        if silent:
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(clip),
                   "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                   "-map", "0:v", "-map", "1:a", "-shortest", "-vf", vf] + vcodec + acodec + [str(out)]
        else:
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(clip),
                   "-vf", vf] + vcodec + acodec + [str(out)]
        run(cmd)
        normalized.append(out)

    list_file = work / "concat_list.txt"
    list_file.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in normalized), encoding="utf-8")

    outp = Path(a.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(outp)])

    dur = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", str(outp)])
    print(f"完成: {outp}（时长 {dur}s，含音轨）")

if __name__ == "__main__":
    main()
