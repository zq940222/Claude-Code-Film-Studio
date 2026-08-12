#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""film-studio 项目档案校验器（跨平台，零第三方依赖）

校验 project.json / shotlist.json 的结构与跨文件语义，把工作区 CLAUDE.md 里
那些"硬性安全规则"从散文约定变成可机械判定的检查——尤其是烧积分前的三类事故：
画幅不一致、引用了带水印的 _raw 图、没过门禁就开拍。

用法
----
    python validate_project.py                      # 校验工作区下所有 projects/*
    python validate_project.py projects/龙王归来     # 只校验一个项目
    python validate_project.py --self-test          # 内置样例自检（CI 用，不需要工作区）
    python validate_project.py --schema-lint        # 校验 schema 本身只用了受支持的关键字（CI 用）
    python validate_project.py --quiet              # 只输出 ERROR，不输出 WARN

退出码：0 = 通过（可含 WARN）；1 = 有 ERROR；2 = 用法或环境错误。

schema 的查找顺序（兼容"插件内"与"复制进工作区"两种摆放）：
    <脚本目录>/schemas/          ← 工作区布局（tools/validate_project.py + tools/schemas/）
    <脚本目录>/../schemas/       ← 插件布局（tools/validate_project.py + schemas/）

关于 JSON Schema 的支持范围
--------------------------
本校验器只实现下方 SUPPORTED_KEYWORDS 里的关键字，不引 jsonschema 库（插件工具
按仓库规则 3 必须零第三方依赖）。写 schema 时只能用这些关键字——`--schema-lint`
会在 CI 里守住这条，防止写了不支持的关键字而校验静默失效。

一处刻意的偏离：`additionalProperties: false` 的违例按 **WARN** 报告而非 ERROR。
这样既能抓出 `submitid` 这类会让任务丢失的拼写错误，又不会因为将来新增字段就
把既有项目判成非法。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SUPPORTED_KEYWORDS = {
    # 注解（不参与校验）
    "$schema", "$id", "title", "description",
    # 引用
    "$defs", "$ref",
    # 通用
    "type", "enum", "const",
    # 字符串
    "minLength", "maxLength", "pattern",
    # 数值
    "minimum", "maximum",
    # 数组
    "minItems", "maxItems", "items",
    # 对象
    "required", "properties", "patternProperties", "additionalProperties",
    # 组合
    "allOf", "if", "then", "else",
}

ERROR = "ERROR"
WARN = "WARN"


class _Delete(object):
    """自检里表示"把这个字段删掉"的哨兵。"""


_DELETE = _Delete()

STAGE_DONE = ("approved", "done")
STAGE_ACTIVE = ("in_progress", "approved", "done")


class Issue(object):
    def __init__(self, level, where, path, message):
        self.level = level
        self.where = where          # 文件（相对工作区）
        self.path = path            # JSON 路径，如 format.medium
        self.message = message

    def __str__(self):
        loc = self.path or "(根)"
        return "[%s] %s :: %s — %s" % (self.level, self.where, loc, self.message)


# --------------------------------------------------------------------------
# JSON Schema 子集校验
# --------------------------------------------------------------------------

def _type_ok(value, t):
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "null":
        return value is None
    return False


def _resolve_ref(root, ref):
    if not ref.startswith("#/"):
        raise ValueError("只支持文档内 $ref（形如 #/$defs/name），收到：%s" % ref)
    node = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise ValueError("$ref 指向不存在的位置：%s" % ref)
        node = node[part]
    return node


def _join(path, key):
    return "%s.%s" % (path, key) if path else str(key)


def _describe(value):
    if isinstance(value, str):
        return '"%s"' % (value if len(value) <= 40 else value[:37] + "...")
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "数组(%d 项)" % len(value)
    if isinstance(value, dict):
        return "对象"
    return str(value)


def validate(value, schema, root, where, path=""):
    """按 schema 校验 value，返回 Issue 列表。"""
    issues = []

    if "$ref" in schema:
        return validate(value, _resolve_ref(root, schema["$ref"]), root, where, path)

    if "type" in schema:
        types = schema["type"]
        if isinstance(types, str):
            types = [types]
        if not any(_type_ok(value, t) for t in types):
            issues.append(Issue(ERROR, where, path,
                                "类型应为 %s，实际是 %s" % ("/".join(types), _describe(value))))
            return issues  # 类型都不对，后面的检查没有意义

    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(_describe(v) for v in schema["enum"])
        issues.append(Issue(ERROR, where, path,
                            "取值 %s 不在允许范围内（%s）" % (_describe(value), allowed)))

    if "const" in schema and value != schema["const"]:
        issues.append(Issue(ERROR, where, path,
                            "必须是 %s，实际是 %s" % (_describe(schema["const"]), _describe(value))))

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            issues.append(Issue(ERROR, where, path, "不能为空 / 长度至少 %d" % schema["minLength"]))
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            issues.append(Issue(ERROR, where, path, "长度不得超过 %d" % schema["maxLength"]))
        if "pattern" in schema and not re.search(schema["pattern"], value):
            issues.append(Issue(ERROR, where, path,
                                "格式不符（应匹配 %s），实际是 %s" % (schema["pattern"], _describe(value))))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(Issue(ERROR, where, path, "不得小于 %s，实际是 %s" % (schema["minimum"], value)))
        if "maximum" in schema and value > schema["maximum"]:
            issues.append(Issue(ERROR, where, path, "不得大于 %s，实际是 %s" % (schema["maximum"], value)))

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            issues.append(Issue(ERROR, where, path, "至少需要 %d 项，实际 %d 项" % (schema["minItems"], len(value))))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            issues.append(Issue(ERROR, where, path, "最多 %d 项，实际 %d 项" % (schema["maxItems"], len(value))))
        if "items" in schema:
            for i, item in enumerate(value):
                issues.extend(validate(item, schema["items"], root, where, "%s[%d]" % (path, i)))

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                issues.append(Issue(ERROR, where, path, "缺少必填字段 %s" % key))

        props = schema.get("properties", {})
        pattern_props = schema.get("patternProperties", {})
        for key, sub in props.items():
            if key in value:
                issues.extend(validate(value[key], sub, root, where, _join(path, key)))

        for pattern, sub in pattern_props.items():
            for key in value:
                if re.search(pattern, key):
                    issues.extend(validate(value[key], sub, root, where, _join(path, key)))

        if schema.get("additionalProperties") is False:
            for key in value:
                if key in props:
                    continue
                if any(re.search(p, key) for p in pattern_props):
                    continue
                issues.append(Issue(WARN, where, _join(path, key),
                                    "未知字段（拼错了？已知字段：%s）"
                                    % ", ".join(sorted(props) or ["无"])))

    for sub in schema.get("allOf", []):
        issues.extend(validate(value, sub, root, where, path))

    if "if" in schema:
        matched = not validate(value, schema["if"], root, where, path)
        branch = "then" if matched else "else"
        if branch in schema:
            conditional = validate(value, schema[branch], root, where, path)
            # 条件分支的报错脱离上下文就看不懂（"mode 不在允许范围内" 到底为什么？），
            # 把该分支的 description 作为原因附在后面。
            reason = schema[branch].get("description")
            if reason:
                for issue in conditional:
                    issue.message = "%s —— %s" % (issue.message, reason)
            issues.extend(conditional)

    return issues


# --------------------------------------------------------------------------
# schema 加载与自检
# --------------------------------------------------------------------------

def schema_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in (os.path.join(here, "schemas"), os.path.join(here, os.pardir, "schemas")):
        if os.path.isdir(candidate):
            return os.path.normpath(candidate)
    return None


def load_schema(name):
    directory = schema_dir()
    if directory is None:
        raise IOError("找不到 schemas/ 目录（在 %s 及其上一级都没有）"
                      % os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(directory, name)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def lint_schema(schema, where, path=""):
    """确认 schema 只用了本校验器支持的关键字。"""
    issues = []
    if isinstance(schema, dict):
        for key, sub in schema.items():
            child = _join(path, key)
            if key not in SUPPORTED_KEYWORDS:
                issues.append(Issue(ERROR, where, child,
                                    "校验器不支持的 schema 关键字 %s（支持的见 SUPPORTED_KEYWORDS）" % key))
            if key in ("properties", "patternProperties", "$defs"):
                if isinstance(sub, dict):
                    for name, value in sub.items():
                        issues.extend(lint_schema(value, where, _join(child, name)))
            elif key in ("items", "if", "then", "else", "$ref"):
                issues.extend(lint_schema(sub, where, child))
            elif key == "allOf":
                if isinstance(sub, list):
                    for i, value in enumerate(sub):
                        issues.extend(lint_schema(value, where, "%s[%d]" % (child, i)))
            elif key == "additionalProperties":
                if not isinstance(sub, bool):
                    issues.append(Issue(ERROR, where, child, "只支持布尔形式的 additionalProperties"))
    return issues


# --------------------------------------------------------------------------
# 跨文件语义检查
# --------------------------------------------------------------------------

def _rel(root, path):
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path


def _ffprobe(path):
    """返回 (duration_sec, width, height)；ffprobe 不可用或读不出时返回 None。"""
    if not shutil.which("ffprobe"):
        return None
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height", "-show_entries", "format=duration",
           "-of", "json", path]
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             timeout=30, check=False).stdout
        data = json.loads(out.decode("utf-8", "replace"))
        stream = (data.get("streams") or [{}])[0]
        duration = float(data.get("format", {}).get("duration", 0) or 0)
        return duration, int(stream.get("width", 0)), int(stream.get("height", 0))
    except Exception:
        return None


def _ratio_of(width, height):
    if not width or not height:
        return None
    value = float(width) / float(height)
    if abs(value - 9.0 / 16.0) < 0.02:
        return "9:16"
    if abs(value - 16.0 / 9.0) < 0.02:
        return "16:9"
    return "%dx%d" % (width, height)


def check_gates(project, where):
    """门禁顺序：把「未过门禁不得进入下一阶段」变成可机械判定的检查。"""
    issues = []
    status = project.get("status") or {}

    def active(stage):
        return status.get(stage) in STAGE_ACTIVE

    def passed(stage):
        return status.get(stage) in STAGE_DONE

    if active("design") and not passed("script"):
        issues.append(Issue(ERROR, where, "status.design",
                            "门禁① 未过：剧本还不是 approved/done 就进了设定图阶段"))
    if active("footage") and not passed("script"):
        issues.append(Issue(ERROR, where, "status.footage",
                            "门禁① 未过：剧本还不是 approved/done 就进了生成阶段"))
    if active("footage") and not passed("design"):
        issues.append(Issue(ERROR, where, "status.footage",
                            "门禁② 未过：设定图还不是 approved/done 就进了生成阶段"
                            "（角色一致性无锚点，生成即烧积分）"))
    if active("final") and not active("footage"):
        issues.append(Issue(WARN, where, "status.final",
                            "还没有任何镜头生成就进了成片阶段"))
    if active("publish") and not passed("final"):
        issues.append(Issue(WARN, where, "status.publish",
                            "成片还不是 approved/done 就进了发布阶段"))
    return issues


def check_ledger(project, where):
    """积分账本对账：预估 → 预留 → 核销。"""
    issues = []
    ledger = project.get("ledger")
    if not isinstance(ledger, dict):
        return issues

    entries = ledger.get("entries") or []
    actual = sum(e.get("credits", 0) for e in entries if e.get("kind") == "actual")
    released = sum(e.get("credits", 0) for e in entries if e.get("kind") == "release")
    reserved = sum(e.get("credits", 0) for e in entries if e.get("kind") == "reserve")

    spent = (project.get("credits") or {}).get("spent")
    if spent is not None and abs(float(spent) - actual) > 0.5:
        issues.append(Issue(WARN, where, "credits.spent",
                            "与账本对不上：credits.spent=%s，账本 actual 合计=%s（少记了一笔核销？）"
                            % (spent, actual)))

    outstanding = reserved - actual - released
    if outstanding < -0.5:
        issues.append(Issue(WARN, where, "ledger.entries",
                            "实际消耗（%s）超过已预留（%s）：有生成任务没走门禁③ 预留就提交了"
                            % (actual, reserved)))

    unit = ledger.get("unit_price") or {}
    if unit.get("confidence") == "calibrated" and not unit.get("samples"):
        issues.append(Issue(WARN, where, "ledger.unit_price",
                            "标了 calibrated 却没有样本数，单价不可信——报价时应按 unknown 处理"))
    if unit.get("confidence") == "calibrated" and unit.get("per_shot") in (None, 0):
        issues.append(Issue(WARN, where, "ledger.unit_price.per_shot",
                            "标了 calibrated 却没有实测单价"))
    return issues


def check_history(project_dir, project, workspace):
    """门禁留痕（history/gates.jsonl）：只在文件存在时检查，老项目没有该文件不算问题。"""
    issues = []
    path = os.path.join(project_dir, "history", "gates.jsonl")
    if not os.path.isfile(path):
        return issues

    where = _rel(workspace, path)
    approved = set()
    with open(path, "r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                issues.append(Issue(ERROR, where, "第 %d 行" % number,
                                    "不是合法 JSON——留痕损坏会让中断后无法判断门禁状态"))
                continue
            if not isinstance(record, dict) or "ts" not in record:
                issues.append(Issue(WARN, where, "第 %d 行" % number, "缺少 ts 时间戳"))
                continue
            if record.get("action") == "approved" and record.get("gate") is not None:
                approved.add(str(record["gate"]))

    status = project.get("status") or {}
    expected = [("1", "script", "剧本定稿"), ("2", "design", "设定图定稿"),
                ("3", "footage", "积分报价"), ("4", "publish", "发布")]
    for gate, stage, name in expected:
        if status.get(stage) in STAGE_ACTIVE and gate not in approved:
            issues.append(Issue(WARN, where, "gate %s" % gate,
                                "%s 阶段已推进，但留痕里没有门禁%s（%s）的确认记录" % (stage, gate, name)))
    return issues


def check_shotlist(shotlist, where, project, project_dir, workspace):
    """shotlist 的跨字段与跨文件检查（schema 表达不了的部分）。"""
    issues = []
    shots = shotlist.get("shots") or []

    project_ratio = ((project.get("format") or {}).get("ratio"))
    if project_ratio and shotlist.get("ratio") and shotlist["ratio"] != project_ratio:
        issues.append(Issue(ERROR, where, "ratio",
                            "画幅与 project.json 不一致（shotlist=%s，project=%s）——照错画幅生成必错"
                            % (shotlist["ratio"], project_ratio)))

    seen = set()
    ids = set(s.get("id") for s in shots if isinstance(s, dict))
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            continue
        base = "shots[%d]" % index
        shot_id = shot.get("id")
        label = "%s(%s)" % (base, shot_id) if shot_id else base
        if shot_id:
            if shot_id in seen:
                issues.append(Issue(ERROR, where, label, "镜号重复"))
            seen.add(shot_id)

        mode = shot.get("mode")
        status = shot.get("status")
        committed = status in ("submitted", "success")

        # --- 引用文件 ---
        refs = []
        for key in ("images", "videos", "audios"):
            for i, value in enumerate(shot.get(key) or []):
                refs.append(("%s.%s[%d]" % (label, key, i), value))
        for key in ("first", "last", "blockout"):
            if shot.get(key):
                refs.append(("%s.%s" % (label, key), shot[key]))

        for ref_path, ref in refs:
            if "/03-design/_raw/" in ref.replace(os.sep, "/"):
                issues.append(Issue(ERROR, where, ref_path,
                                    "引用了 _raw/ 里未清水印的原始图——水印会被复刻进视频且无法补救"))
            absolute = os.path.join(workspace, ref)
            if not os.path.exists(absolute):
                level = ERROR if committed else WARN
                hint = "该镜已提交/已完成，引用文件却不存在" if committed else "引用的文件还不存在（可能尚未出图）"
                issues.append(Issue(level, where, ref_path, "%s：%s" % (hint, ref)))

        # --- 白模归属与一致性 ---
        blockout = shot.get("blockout")
        if blockout:
            if blockout not in (shot.get("videos") or []):
                issues.append(Issue(ERROR, where, "%s.blockout" % label,
                                    "白模视频没有出现在 videos 里，即梦收不到这一路参考"))
            if mode != "multimodal2video":
                issues.append(Issue(ERROR, where, "%s.blockout" % label,
                                    "只有 multimodal2video 有视频参考位，当前 mode=%s" % mode))
            probe = _ffprobe(os.path.join(workspace, blockout))
            if probe:
                duration, width, height = probe
                want = shot.get("duration")
                if want and abs(duration - float(want)) > 0.3:
                    issues.append(Issue(ERROR, where, "%s.blockout" % label,
                                        "白模时长 %.1fs 与该镜 %.1fs 不一致——重渲白模免费，照错白模生成烧积分"
                                        % (duration, float(want))))
                got_ratio = _ratio_of(width, height)
                if got_ratio and project_ratio and got_ratio != project_ratio:
                    issues.append(Issue(ERROR, where, "%s.blockout" % label,
                                        "白模画幅 %s 与项目 %s 不一致" % (got_ratio, project_ratio)))

        # --- 模式专属的跨字段规则 ---
        if mode == "frames2video":
            if not shot.get("first") and not shot.get("first_from_prev"):
                issues.append(Issue(ERROR, where, label,
                                    "frames2video 必须有首帧：给 first 关键帧，或用 first_from_prev 从上一镜抽尾帧"))
            if not shot.get("last"):
                issues.append(Issue(ERROR, where, label, "frames2video 缺少尾帧 last"))
        if shot.get("first_from_prev") and shot["first_from_prev"] not in ids:
            issues.append(Issue(ERROR, where, "%s.first_from_prev" % label,
                                "指向不存在的镜号 %s" % shot["first_from_prev"]))
        if mode == "multiframe2video":
            images = shot.get("images") or []
            transitions = shot.get("transitions")
            if len(images) > 2:
                if not transitions:
                    issues.append(Issue(ERROR, where, label,
                                        "3 张以上关键帧必须给 transitions 数组（长度 = 图数-1 = %d）"
                                        % (len(images) - 1)))
                elif len(transitions) != len(images) - 1:
                    issues.append(Issue(ERROR, where, "%s.transitions" % label,
                                        "段数 %d 与关键帧数不匹配（应为 图数-1 = %d）"
                                        % (len(transitions), len(images) - 1)))
            if transitions:
                total = sum(t.get("duration", 0) for t in transitions if isinstance(t, dict))
                if shot.get("duration") and abs(total - float(shot["duration"])) > 0.3:
                    issues.append(Issue(WARN, where, "%s.duration" % label,
                                        "应为各段之和 %.1fs，实际写了 %.1fs" % (total, float(shot["duration"]))))

        # --- 生成状态自洽 ---
        if status == "submitted" and not shot.get("submit_id"):
            issues.append(Issue(ERROR, where, label,
                                "状态是 submitted 却没有 submit_id——任务会丢失，无法用 /studio-status 收割"))
        if status == "success":
            if not shot.get("file"):
                issues.append(Issue(ERROR, where, label, "状态是 success 却没有产物路径 file"))
            elif not os.path.exists(os.path.join(workspace, shot["file"])):
                issues.append(Issue(ERROR, where, "%s.file" % label,
                                    "产物文件不存在：%s" % shot["file"]))
            if not shot.get("submit_id"):
                issues.append(Issue(WARN, where, label, "状态是 success 却没有 submit_id，无法追溯"))

        for i, reason in enumerate(shot.get("rework_reasons") or []):
            if not (reason.startswith("[AI]") or reason.startswith("[人工]")):
                issues.append(Issue(WARN, where, "%s.rework_reasons[%d]" % (label, i),
                                    "缺少来源标记（应以 [AI] 或 [人工] 开头）：%s" % reason))

    return issues


def check_project(project_dir, workspace):
    """校验一个项目目录，返回 Issue 列表。"""
    issues = []
    where = _rel(workspace, os.path.join(project_dir, "project.json"))
    project_path = os.path.join(project_dir, "project.json")

    if not os.path.isfile(project_path):
        return [Issue(ERROR, _rel(workspace, project_dir), "", "缺少 project.json，不是有效的项目目录")]

    try:
        with open(project_path, "r", encoding="utf-8") as handle:
            project = json.load(handle)
    except ValueError as exc:
        return [Issue(ERROR, where, "", "JSON 解析失败：%s" % exc)]

    project_schema = load_schema("project.schema.json")
    issues.extend(validate(project, project_schema, project_schema, where))
    issues.extend(check_gates(project, where))
    issues.extend(check_ledger(project, where))
    issues.extend(check_history(project_dir, project, workspace))

    for name in ("01-script", "02-storyboard", "03-design", "04-footage", "05-final"):
        if not os.path.isdir(os.path.join(project_dir, name)):
            issues.append(Issue(WARN, _rel(workspace, project_dir), "", "缺少标准目录 %s/" % name))

    shotlist_schema = load_schema("shotlist.schema.json")
    footage = os.path.join(project_dir, "04-footage")
    if os.path.isdir(footage):
        for episode in sorted(os.listdir(footage)):
            path = os.path.join(footage, episode, "shotlist.json")
            if not os.path.isfile(path):
                continue
            sl_where = _rel(workspace, path)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    shotlist = json.load(handle)
            except ValueError as exc:
                issues.append(Issue(ERROR, sl_where, "", "JSON 解析失败：%s" % exc))
                continue
            issues.extend(validate(shotlist, shotlist_schema, shotlist_schema, sl_where))
            match = re.match(r"^ep(\d+)$", episode)
            if match and shotlist.get("episode") != int(match.group(1)):
                issues.append(Issue(ERROR, sl_where, "episode",
                                    "集号 %s 与目录名 %s 不一致" % (shotlist.get("episode"), episode)))
            issues.extend(check_shotlist(shotlist, sl_where, project, project_dir, workspace))

    return issues


# --------------------------------------------------------------------------
# 自检（CI 用，不依赖工作区）
# --------------------------------------------------------------------------

_GOOD_PROJECT = {
    "title": "龙王归来",
    "genre": "都市逆袭",
    "format": {"medium": "short-drama", "ratio": "9:16", "episode_duration_sec": 90,
               "episodes": 1, "style": {"preset": "cn-urban-realist", "name": "国产都市写实"}},
    "editing": {"episode_overlap": {"enabled": False, "seconds": 4}, "intro_outro": {"enabled": False}},
    "status": {"script": "done", "storyboard": "done", "previz": "skipped",
               "design": "approved", "footage": "in_progress", "final": "pending"},
    "credits": {"spent": 320, "notes": "ep01 前 4 镜实测 320"},
    "ledger": {
        "unit_price": {"per_shot": 80, "per_video_ref_shot": None, "confidence": "calibrated", "samples": 4},
        "entries": [
            {"ts": "2026-08-12", "ep": "ep01", "kind": "estimate", "shots": 4, "credits": 400},
            {"ts": "2026-08-12", "ep": "ep01", "kind": "reserve", "shots": 4, "credits": 400},
            {"ts": "2026-08-12", "ep": "ep01", "kind": "actual", "shots": 4, "credits": 320,
             "balance_after": 13880},
            {"ts": "2026-08-12", "ep": "ep01", "kind": "release", "credits": 80},
        ],
    },
    "created": "2026-08-12",
}

_GOOD_SHOTLIST = {
    "episode": 1,
    "ratio": "9:16",
    "shots": [
        {"id": "sh01", "mode": "text2video", "prompt": "STYLE LOCK ... empty alley at dawn",
         "duration": 6, "model": "seedance2.0fast_vip", "resolution": "720p",
         "transition_in": "定场（第 1 场开场）", "status": "pending", "submit_id": None, "file": None},
        {"id": "sh02", "mode": "multiframe2video", "prompt": None,
         "images": ["a.png", "b.png", "c.png"],
         "transitions": [{"prompt": "kf1 到 kf2", "duration": 4},
                         {"prompt": "kf2 到 kf3", "duration": 3}],
         "duration": 7, "model": None, "resolution": None, "silent": True,
         "status": "pending", "submit_id": None, "file": None},
    ],
}


def _self_test():
    """内置样例自检：好的样例必须零 ERROR，坏的样例必须被抓到。"""
    project_schema = load_schema("project.schema.json")
    shotlist_schema = load_schema("shotlist.schema.json")
    failures = []
    checked = [0]
    nowhere = os.path.join(os.getcwd(), "__self_test_no_such_dir__")

    def errors_of(instance, schema):
        return [i for i in validate(instance, schema, schema, "self-test") if i.level == ERROR]

    def expect_clean(name, instance, schema):
        checked[0] += 1
        found = errors_of(instance, schema)
        if found:
            failures.append("%s 本应通过，却报了：%s" % (name, "；".join(i.message for i in found)))

    def expect_error(name, instance, schema, needle):
        checked[0] += 1
        found = errors_of(instance, schema)
        if not any(needle in i.message or needle in i.path for i in found):
            failures.append("%s 本应报出「%s」，实际报了：%s"
                            % (name, needle, "；".join(i.message for i in found) or "无"))

    def expect_semantic(name, issues, needle):
        checked[0] += 1
        if not any(needle in i.message for i in issues):
            failures.append("%s 没被抓到（实际报了：%s）"
                            % (name, "；".join(i.message for i in issues) or "无"))

    def mutate(base, path, value):
        clone = json.loads(json.dumps(base))
        node = clone
        for key in path[:-1]:
            node = node[key]
        if value is _DELETE:
            node.pop(path[-1], None)
        else:
            node[path[-1]] = value
        return clone

    expect_clean("合法 project.json", _GOOD_PROJECT, project_schema)
    expect_clean("合法 shotlist.json", _GOOD_SHOTLIST, shotlist_schema)

    expect_error("未知 medium", mutate(_GOOD_PROJECT, ["format", "medium"], "tiktok"),
                 project_schema, "不在允许范围")
    expect_error("缺 format.ratio", mutate(_GOOD_PROJECT, ["format", "ratio"], _DELETE),
                 project_schema, "缺少必填字段 ratio")
    expect_error("非法阶段状态", mutate(_GOOD_PROJECT, ["status", "script"], "finished"),
                 project_schema, "不在允许范围")
    expect_error("created 格式错", mutate(_GOOD_PROJECT, ["created"], "2026/08/12"),
                 project_schema, "格式不符")
    expect_error("账本 kind 拼错", mutate(_GOOD_PROJECT, ["ledger", "entries", 0, "kind"], "estimated"),
                 project_schema, "不在允许范围")

    expect_error("multiframe 带了 model",
                 mutate(_GOOD_SHOTLIST, ["shots", 1, "model"], "seedance2.0_vip"),
                 shotlist_schema, "必须是 null")
    expect_error("multiframe 标了非静音",
                 mutate(_GOOD_SHOTLIST, ["shots", 1, "silent"], False),
                 shotlist_schema, "必须是 true")
    expect_error("seedance 家族要 1080p",
                 mutate(_GOOD_SHOTLIST, ["shots", 0, "resolution"], "1080p"),
                 shotlist_schema, "不在允许范围")
    expect_error("镜号格式错", mutate(_GOOD_SHOTLIST, ["shots", 0, "id"], "shot1"),
                 shotlist_schema, "格式不符")
    expect_error("单镜时长超上限", mutate(_GOOD_SHOTLIST, ["shots", 0, "duration"], 30),
                 shotlist_schema, "不得大于 15")
    expect_error("multimodal 缺参考图",
                 mutate(mutate(_GOOD_SHOTLIST, ["shots", 0, "mode"], "multimodal2video"),
                        ["shots", 0, "resolution"], "720p"),
                 shotlist_schema, "缺少必填字段 images")

    # 跨字段与跨文件检查（schema 表达不了，走 check_* 系列）
    def shotlist_issues(mutations):
        bad = json.loads(json.dumps(_GOOD_SHOTLIST))
        mutations(bad)
        return check_shotlist(bad, "self-test", _GOOD_PROJECT, nowhere, nowhere)

    def project_issues(mutations, checker):
        bad = json.loads(json.dumps(_GOOD_PROJECT))
        mutations(bad)
        return checker(bad, "self-test")

    def set_transitions(sl):
        sl["shots"][1]["transitions"] = [{"prompt": "只给了一段", "duration": 7}]

    def set_raw_image(sl):
        sl["shots"][0]["mode"] = "multimodal2video"
        sl["shots"][0]["images"] = ["projects/x/03-design/_raw/林晚.png"]

    def set_orphan_blockout(sl):
        sl["shots"][0]["mode"] = "multimodal2video"
        sl["shots"][0]["images"] = ["projects/x/03-design/characters/林晚.png"]
        sl["shots"][0]["blockout"] = "projects/x/03-previz/ep01/sh01-blockout.mp4"
        sl["shots"][0]["videos"] = []

    expect_semantic("multiframe 段数不匹配", shotlist_issues(set_transitions), "段数")
    expect_semantic("画幅与 project.json 不一致",
                    shotlist_issues(lambda sl: sl.update({"ratio": "16:9"})),
                    "画幅与 project.json 不一致")
    expect_semantic("引用 _raw/ 带水印原始图", shotlist_issues(set_raw_image), "_raw/")
    expect_semantic("白模没进 videos", shotlist_issues(set_orphan_blockout), "没有出现在 videos")
    expect_semantic("submitted 缺 submit_id",
                    shotlist_issues(lambda sl: sl["shots"][0].update({"status": "submitted"})),
                    "submit_id")
    expect_semantic("frames2video 缺首尾帧",
                    shotlist_issues(lambda sl: sl["shots"][0].update({"mode": "frames2video"})),
                    "缺少尾帧")
    expect_semantic("未过门禁② 就开拍",
                    project_issues(lambda p: p["status"].update({"design": "in_progress"}), check_gates),
                    "门禁②")
    expect_semantic("未过门禁① 就出设定图",
                    project_issues(lambda p: p["status"].update({"script": "in_progress"}), check_gates),
                    "门禁①")
    expect_semantic("账本与 credits.spent 对不上",
                    project_issues(lambda p: p["credits"].update({"spent": 999}), check_ledger),
                    "对不上")
    expect_semantic("超预留消耗",
                    project_issues(lambda p: p["ledger"]["entries"].append(
                        {"ts": "2026-08-13", "kind": "actual", "credits": 500}), check_ledger),
                    "超过已预留")

    return failures, checked[0]


# --------------------------------------------------------------------------
# 入口
# --------------------------------------------------------------------------

def _report(issues, quiet):
    errors = [i for i in issues if i.level == ERROR]
    warns = [i for i in issues if i.level == WARN]
    for issue in errors:
        print(issue)
    if not quiet:
        for issue in warns:
            print(issue)
    return errors, warns


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="校验 film-studio 的 project.json / shotlist.json")
    parser.add_argument("targets", nargs="*",
                        help="项目目录（默认扫描当前工作区的 projects/*）")
    parser.add_argument("--self-test", action="store_true", help="跑内置样例自检（CI 用）")
    parser.add_argument("--schema-lint", action="store_true", help="校验 schema 本身（CI 用）")
    parser.add_argument("--quiet", action="store_true", help="只输出 ERROR")
    args = parser.parse_args(argv)

    if schema_dir() is None:
        here = os.path.dirname(os.path.abspath(__file__))
        print("[ERROR] 找不到 schemas/ 目录（在 %s 及其上一级都没有）。" % here)
        print("        本脚本按「自己所在目录的 schemas/」查找 schema。")
        print("        工作区里请把插件根的 schemas/ 复制为 tools/schemas/：")
        print("          <插件根>/schemas/  →  <工作区>/tools/schemas/")
        print("        （v3.1.0 之前建的工作区没有这一项，补齐即可，不必重跑 /new-drama）")
        return 2

    if args.schema_lint:
        issues = []
        for name in ("project.schema.json", "shotlist.schema.json"):
            issues.extend(lint_schema(load_schema(name), name))
        errors, _ = _report(issues, args.quiet)
        if errors:
            print("\n[FAIL] schema 用了校验器不支持的关键字，校验会静默失效")
            return 1
        print("[OK] schema 只用了受支持的关键字")
        return 0

    if args.self_test:
        failures, checked = _self_test()
        for failure in failures:
            print("[FAIL] %s" % failure)
        if failures:
            print("\n[FAIL] %d/%d 项自检未通过" % (len(failures), checked))
            return 1
        print("[OK] 自检通过：%d 项断言全数命中（合法样例零 ERROR，各类违例均被抓出）" % checked)
        return 0

    workspace = os.getcwd()
    if args.targets:
        project_dirs = [os.path.abspath(t) for t in args.targets]
    else:
        root = os.path.join(workspace, "projects")
        if not os.path.isdir(root):
            print("[ERROR] 当前目录下没有 projects/ —— 请在工作区根目录运行，或直接指定项目目录")
            return 2
        project_dirs = [os.path.join(root, name) for name in sorted(os.listdir(root))
                        if os.path.isdir(os.path.join(root, name))]

    if not project_dirs:
        print("[OK] 没有找到任何项目")
        return 0

    all_issues = []
    for project_dir in project_dirs:
        all_issues.extend(check_project(project_dir, workspace))

    errors, warns = _report(all_issues, args.quiet)
    print("\n检查了 %d 个项目：%d 个 ERROR，%d 个 WARN"
          % (len(project_dirs), len(errors), len(warns)))
    if errors:
        print("[FAIL] 有 ERROR 必须先修——其中画幅不一致、引用 _raw 图、未过门禁属于会烧积分的事故")
        return 1
    print("[OK] 通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
