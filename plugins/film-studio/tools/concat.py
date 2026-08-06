#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""concat.py — 影视工作台镜头拼接脚本（跨平台：Windows / macOS）

**非破坏性优先**：默认先探测各片段规格——
  · 规格完全一致（同编码/分辨率/帧率/像素格式，且都含音轨）→ 纯流拷贝 concat，**零重编码，无损**
  · 规格不一致 → 仅此时才统一转码（补边/补静音）后再 concat
即梦同模型同画幅输出的片段规格天然一致，因此常规情况走无损路径，画质不受损。

注意：本脚本产出的是"粗剪预览"，用于快速看节奏；正式精剪请用 /finalcut 走剪映/达芬奇
时间线（非破坏性，最终只渲染一次）。原始 sh*.mp4 永远不被本脚本修改（只读）。

用法：
  python tools/concat.py --input-dir "projects/剧名/04-footage/ep01" \
      --output "projects/剧名/05-final/剧名-ep01-粗剪.mp4"
  python tools/concat.py --input-dir ... --output ... --files sh02.mp4 sh01.mp4   # 自定义顺序
  # --files 也接受绝对路径（如片头/片尾卡），与目录内文件名可混用
  # 规格不一致需转码时，用 --ratio 指定目标画幅（9:16 默认 / 16:9）
  # --force-normalize 强制统一转码（一般不需要）
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

def probe(path):
    """返回 (video_spec_tuple, audio_spec_str)。audio_spec 为空串表示无音轨。"""
    v = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name,width,height,pix_fmt,r_frame_rate",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip()
    a = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=codec_name,sample_rate,channels",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip()
    return v, a

def concat_copy(clips, outp):
    """纯流拷贝拼接（无损）。"""
    list_file = outp.parent / "_concat_list.txt"
    list_file.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in clips), encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(outp)])
    list_file.unlink(missing_ok=True)

def main():
    ap = argparse.ArgumentParser(description="非破坏性优先地拼接镜头片段（保留音轨）")
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--ratio", choices=["9:16", "16:9"], default="9:16",
                    help="仅在需要转码（规格不一致）时用作目标画幅")
    ap.add_argument("--files", nargs="*", default=None, help="自定义顺序；省略则按 sh*.mp4 文件名排序")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--force-normalize", action="store_true", help="强制统一转码，跳过无损快路径")
    a = ap.parse_args()

    indir = Path(a.input_dir)
    clips = ([indir / f if not Path(f).is_absolute() else Path(f) for f in a.files] if a.files
             else sorted(indir.glob("sh*.mp4")))
    if not clips:
        sys.exit("InputDir 下没有找到镜头片段（sh*.mp4）")
    for c in clips:
        if not c.exists():
            sys.exit(f"片段不存在: {c}")

    outp = Path(a.output)
    outp.parent.mkdir(parents=True, exist_ok=True)

    # 探测规格，判断能否走无损流拷贝
    specs = [probe(c) for c in clips]
    all_have_audio = all(a_spec for _, a_spec in specs)
    uniform = len({s for s in specs}) == 1  # 视频+音频规格完全一致
    if uniform and all_have_audio and not a.force_normalize:
        print(f"规格一致（{specs[0][0]}），走无损流拷贝拼接 {len(clips)} 个片段 ...")
        concat_copy(clips, outp)
        dur = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "csv=p=0", str(outp)])
        print(f"完成（无损）: {outp}（时长 {dur}s，含音轨，未重编码）")
        return

    # 规格不一致：仅此时统一转码
    reason = "含无音轨片段" if not all_have_audio else "片段规格不一致"
    W, H = (1080, 1920) if a.ratio == "9:16" else (1920, 1080)
    print(f"⚠ {reason}，需统一转码为 {W}x{H}@{a.fps}fps 后拼接（会重编码，画质略有损失）")
    work = indir / "_work"
    work.mkdir(exist_ok=True)
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={a.fps}")
    acodec = ["-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k"]
    vcodec = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(a.crf), "-preset", "medium"]

    normalized = []
    for i, (clip, (_, a_spec)) in enumerate(zip(clips, specs), 1):
        out = work / f"{i:03d}_{clip.name}"
        silent = not a_spec
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

    concat_copy(normalized, outp)
    dur = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", str(outp)])
    print(f"完成（已转码统一规格）: {outp}（时长 {dur}s，含音轨）")

if __name__ == "__main__":
    main()
