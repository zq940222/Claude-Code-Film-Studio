#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""blender_blockout.py — 白模（3D blockout）预演构建与渲染脚本（跨平台：Windows / macOS）

读 `blockout.json` 规格 → 在 Blender 里搭白模（地面/墙体/道具方块 + 人物代理 + 相机运动）
→ Workbench 引擎渲白模帧序列 → ffmpeg 封装成与本集画幅一致的 mp4，
供摄影指导在即梦 `multimodal2video` 里当 `@video` 参考用（锁运镜、锁空间关系、锁走位）。

**白模只是"运镜与空间的骨架"，不承载画面风格**——风格仍由 STYLE LOCK + 设定图承载。
所以这里刻意只渲纯白灰面（无材质、无贴图、无色彩），把"看起来像什么"完全留给即梦。

用法（渲染；需本机已装 Blender 3.6+，Blender 自带 Python，无需额外装包）：
  blender -b --factory-startup -P tools/blender_blockout.py -- \
      --spec "projects/剧名/03-previz/ep01/blockout.json" --out-root "projects/剧名"
  # 只渲某几镜（改了规格重渲，别整集重来）：  --only sh03,sh07
  # 规格自检（纯 Python，不需要 Blender、不出图，建项/改规格后先跑这个）：
  python tools/blender_blockout.py --spec "projects/剧名/03-previz/ep01/blockout.json" --validate

blockout.json 规格见 previz-artist agent 规范；坐标系为 Blender 右手系（Z 向上，单位米）。
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import bpy  # 只有在 Blender 里跑才有；--validate 模式不需要
except ImportError:
    bpy = None

for _s in (sys.stdout, sys.stderr):  # Windows 控制台默认 GBK，统一 UTF-8（错误信息也要不乱码）
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

# 画幅 → 渲染分辨率（短边 720，与即梦 720p 输出对齐；比例必须与本集 ratio 严格一致）
RES = {"9:16": (720, 1280), "16:9": (1280, 720), "1:1": (720, 720),
       "3:4": (720, 960), "4:3": (960, 720), "21:9": (1680, 720)}


# ---------------------------------------------------------------- 规格校验

def validate(spec, only=None):
    """校验 blockout.json，返回 (待渲镜头列表, 警告列表)；致命错误直接 sys.exit。"""
    errs, warns = [], []
    ratio = spec.get("ratio")
    if ratio not in RES:
        errs.append(f"ratio 非法或缺失: {ratio!r}（可选 {'/'.join(RES)}）")
    fps = spec.get("fps", 24)
    if not isinstance(fps, int) or not 12 <= fps <= 60:
        errs.append(f"fps 非法: {fps!r}（建议 24）")

    shots, seen = [], set()
    for i, sh in enumerate(spec.get("shots") or []):
        sid = sh.get("id") or f"#{i}"
        if sid in seen:
            errs.append(f"{sid}: 镜号重复")
        seen.add(sid)
        if only and sid not in only:
            continue
        dur = sh.get("duration")
        if not isinstance(dur, (int, float)) or not 1 <= dur <= 15:
            errs.append(f"{sid}: duration 非法 {dur!r}（即梦单镜 4-15s，白模须与该镜时长一致）")
            dur = 0
        if not sh.get("out"):
            errs.append(f"{sid}: 缺 out（白模视频输出路径）")
        keys = (sh.get("camera") or {}).get("keys") or []
        if len(keys) < 2:
            errs.append(f"{sid}: camera.keys 至少 2 个（固定机位也要首尾两个同位置关键帧）")
        for k in keys:
            if not isinstance(k.get("t"), (int, float)):
                errs.append(f"{sid}: camera 关键帧缺 t")
            elif dur and not 0 <= k["t"] <= dur:
                errs.append(f"{sid}: camera 关键帧 t={k['t']} 越出 0-{dur}s")
            for f in ("pos", "look_at"):
                v = k.get(f)
                if not (isinstance(v, (list, tuple)) and len(v) == 3):
                    errs.append(f"{sid}: camera 关键帧 {f} 必须是三元数组 [x,y,z]")
        if keys and dur:
            ts = [k.get("t") for k in keys if isinstance(k.get("t"), (int, float))]
            if ts and sorted(ts) != ts:
                errs.append(f"{sid}: camera.keys 必须按 t 升序")
            if ts and abs(max(ts) - dur) > 0.05:
                warns.append(f"{sid}: 末个关键帧 t={max(ts)} ≠ duration {dur}s，"
                             f"末段运镜会停住（如确为静止收尾可忽略）")
        for a in sh.get("actors") or []:
            h = a.get("height", 1.7)
            if not 0.5 <= h <= 2.5:
                warns.append(f"{sid}: 人物代理 {a.get('name')} 身高 {h}m 不像人（景别会算错）")
        shots.append(sh)

    if only:
        missing = only - seen
        if missing:
            errs.append(f"--only 指定的镜号不在规格里: {','.join(sorted(missing))}")
    if not shots:
        errs.append("没有待渲镜头")
    if errs:
        sys.exit("规格校验失败：\n  - " + "\n  - ".join(errs))
    return shots, warns


# ---------------------------------------------------------------- 建场景

def frame_of(t, dur, frames):
    """秒 → 帧号：t=0 落第 1 帧、t=duration 落最后一帧。

    这样运镜正好在渲染区间内走完（若按 1+t*fps 算，t=duration 会落到 frame_end+1，末段动作渲不出来）。
    """
    return 1 + round(float(t) / dur * (frames - 1)) if dur else 1


def clear_scene():
    """清空对象与动作数据（同一次 Blender 进程里连渲多镜，防止上一镜残留）。"""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for act in list(bpy.data.actions):
        bpy.data.actions.remove(act)


def add_box(name, pos, size):
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(pos))
    obj = bpy.context.active_object
    obj.name, obj.scale = name, tuple(size)  # size=1 的立方体，scale 即实际尺寸（米）
    return obj


def build_set(sh):
    """地面 + 墙体 + 道具方块：只求空间关系与遮挡关系对，不求好看。"""
    st = sh.get("set") or {}
    fx, fy = (st.get("floor") or {}).get("size", [12, 12])
    add_box("Floor", (0, 0, -0.05), (fx, fy, 0.1))
    for i, w in enumerate(st.get("walls") or [], 1):
        add_box(f"Wall{i}", w["pos"], w["size"])
    for i, p in enumerate(st.get("props") or [], 1):
        add_box(p.get("name") or f"Prop{i}", p["pos"], p["size"])


def build_actor(a, dur, frames):
    """人物代理：圆柱身 + 球头 + 朝向小块（朝向块让轴线/视线方向在白模里看得出来）。

    身高按真实米数搭——景别（全景/中景/近景）在白模里能不能对，全靠人物比例真实。
    """
    name = a.get("name") or "Actor"
    h = float(a.get("height", 1.7))
    root = bpy.data.objects.new(f"A_{name}", None)  # 空物体当骨架根，动画挂在它身上
    bpy.context.scene.collection.objects.link(root)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.80 * h, location=(0, 0, 0.40 * h),
                                        vertices=16)
    body = bpy.context.active_object
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.105, location=(0, 0, 0.88 * h),
                                         segments=16, ring_count=8)
    head = bpy.context.active_object
    nose = add_box(f"{name}_face", (0, 0.14, 0.88 * h), (0.06, 0.12, 0.06))
    for part in (body, head, nose):
        part.parent = root  # 直接挂父级（parent_inverse 保持单位矩阵，子物体坐标即局部偏移）

    keys = a.get("keys") or [{"t": 0, "pos": a.get("pos", [0, 0, 0]),
                              "facing": a.get("facing", 0)}]
    for k in keys:
        f = frame_of(k["t"], dur, frames)
        root.location = tuple(k.get("pos", a.get("pos", [0, 0, 0])))
        root.rotation_euler = (0, 0, math.radians(float(k.get("facing", a.get("facing", 0)))))
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
    if len(keys) == 1:  # 静止人物也补个尾帧，避免只有单关键帧
        root.keyframe_insert("location", frame=frames)
    return root


def build_camera(cam_spec, dur, frames, interp):
    """相机走位：空物体 CamRig 带 TRACK_TO 盯 look_at 目标，相机作为子物体承担荷兰角。

    这样 pos/look_at 可以逐帧给，运镜（推拉摇移跟环绕升降）全靠关键帧插值出来，
    而不是靠文字描述——这正是白模比提示词强的地方。
    """
    scene = bpy.context.scene
    target = bpy.data.objects.new("CamTarget", None)
    rig = bpy.data.objects.new("CamRig", None)
    scene.collection.objects.link(target)
    scene.collection.objects.link(rig)

    cam_data = bpy.data.cameras.new("Camera")
    # sensor_fit=AUTO：36mm 传感器宽度贴合画幅长边，等价于"把相机转过来拍竖屏"，
    # 所以 lens_mm 就是 36mm 全画幅等效焦段，景别可按真实拍摄经验推算（换算见 previz-artist 规范）
    cam_data.sensor_fit = "AUTO"
    cam_data.lens = float(cam_spec.get("lens_mm", 35))
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.parent = rig
    scene.camera = cam

    con = rig.constraints.new(type="TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"

    for k in cam_spec["keys"]:
        f = frame_of(k["t"], dur, frames)
        rig.location = tuple(k["pos"])
        rig.keyframe_insert("location", frame=f)
        target.location = tuple(k["look_at"])
        target.keyframe_insert("location", frame=f)
        cam.rotation_euler = (0, 0, math.radians(float(k.get("roll", 0))))  # 荷兰角
        cam.keyframe_insert("rotation_euler", frame=f)
        if k.get("lens_mm"):  # 逐帧焦段 → 变焦 / 希区柯克变焦
            cam_data.lens = float(k["lens_mm"])
            cam_data.keyframe_insert("lens", frame=f)

    for obj in (rig, target, cam, cam_data):
        ad = getattr(obj, "animation_data", None)
        if ad and ad.action:
            for fc in ad.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = interp  # LINEAR=匀速运镜；BEZIER=带加减速（默认）


def setup_render(scene, ratio, fps, frames):
    """Workbench 纯白灰面渲染：无材质无贴图，只留形体、阴影与凹凸（cavity）帮读空间。"""
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "SINGLE"
    sh.single_color = (0.8, 0.8, 0.8)
    for attr, val in (("show_shadows", True), ("show_cavity", True),
                      ("cavity_type", "BOTH"), ("show_object_outline", True)):
        try:
            setattr(sh, attr, val)  # 各版本可用性略有差异，缺了不影响可用性
        except (AttributeError, TypeError):
            pass
    try:
        scene.display.render_aa = "8"
    except (AttributeError, TypeError):
        pass

    scene.render.resolution_x, scene.render.resolution_y = RES[ratio]
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start, scene.frame_end = 1, frames
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False


def encode(frames_dir, fps, out_path):
    """帧序列 → mp4：走 ffmpeg 而不是 Blender 内置封装，编码参数与工作台其余环节一致。"""
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg 不在 PATH 中（白模帧已渲出在 %s，装好 ffmpeg 后可手动封装）" % frames_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", str(fps), "-start_number", "1", "-i", str(frames_dir / "f%04d.png"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-movflags", "+faststart", str(out_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"ffmpeg 封装失败：\n{r.stderr.strip()}")


def render_shot(sh, ratio, fps, out_root, interp):
    sid = sh["id"]
    dur = float(sh["duration"])
    frames = max(2, round(dur * fps))
    out_path = Path(sh["out"])
    if not out_path.is_absolute():
        out_path = out_root / out_path

    clear_scene()
    build_set(sh)
    for a in sh.get("actors") or []:
        build_actor(a, dur, frames)
    build_camera(sh["camera"], dur, frames, interp)

    scene = bpy.context.scene
    setup_render(scene, ratio, fps, frames)
    frames_dir = out_path.parent / f"_frames_{sid}"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(frames_dir / "f")

    print(f"[{sid}] 渲染 {frames} 帧 @{fps}fps（{dur}s，{RES[ratio][0]}x{RES[ratio][1]}）...")
    bpy.ops.render.render(animation=True)
    encode(frames_dir, fps, out_path)
    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"[{sid}] 完成 → {out_path}")
    return out_path


# ---------------------------------------------------------------- 入口

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser(description="按 blockout.json 搭白模并渲成即梦可用的运镜参考视频")
    ap.add_argument("--spec", required=True, help="blockout.json 路径")
    ap.add_argument("--out-root", default=".", help="镜头 out 为相对路径时的根目录（一般填项目目录）")
    ap.add_argument("--only", default=None, help="只渲这些镜号，逗号分隔（如 sh03,sh07）")
    ap.add_argument("--interp", choices=["BEZIER", "LINEAR"], default="BEZIER",
                    help="运镜插值：BEZIER 带加减速（默认，像真实推拉）；LINEAR 匀速")
    ap.add_argument("--validate", action="store_true", help="只校验规格并打印计划，不渲染（无需 Blender）")
    ap.add_argument("--allow-existing", action="store_true",
                    help="允许在已打开的 .blend 文件上执行（默认拒绝，防误改工程）")
    a = ap.parse_args(argv)

    spec_path = Path(a.spec)
    if not spec_path.exists():
        sys.exit(f"规格文件不存在: {spec_path}")
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"blockout.json 不是合法 JSON: {e}")

    only = {s.strip() for s in a.only.split(",") if s.strip()} if a.only else None
    shots, warns = validate(spec, only)
    ratio, fps = spec["ratio"], spec.get("fps", 24)
    for w in warns:
        print(f"⚠ {w}")

    if a.validate or bpy is None:
        if bpy is None and not a.validate:
            print("⚠ 未检测到 bpy（不在 Blender 里运行），只做规格校验")
        for sh in shots:
            print(f"[{sh['id']}] {sh['duration']}s → {max(2, round(sh['duration'] * fps))} 帧"
                  f" @{RES[ratio][0]}x{RES[ratio][1]}，{len(sh['camera']['keys'])} 个相机关键帧，"
                  f"{len(sh.get('actors') or [])} 个人物代理 → {sh['out']}")
        print(f"规格校验通过：{len(shots)} 镜，画幅 {ratio}，{fps}fps"
              + ("（含上述警告）" if warns else ""))
        return

    if bpy.data.filepath and not a.allow_existing:
        sys.exit(f"当前 Blender 已打开工程 {bpy.data.filepath}，本脚本会清空场景对象。"
                 "请改用 `blender -b --factory-startup -P ...`，或显式加 --allow-existing")

    out_root = Path(a.out_root)
    done = [render_shot(sh, ratio, fps, out_root, a.interp) for sh in shots]
    print(f"\n白模渲染完成 {len(done)} 镜（画幅 {ratio}，{fps}fps）：")
    for p in done:
        print(f"  - {p}")
    print("下一步：把这些白模视频写进 shotlist 的 blockout/videos 字段（摄影指导），"
          "提示词里必须写复刻句 + 禁灰面句，见 seedance-prompt 技能白模专章")


if __name__ == "__main__":
    main()
