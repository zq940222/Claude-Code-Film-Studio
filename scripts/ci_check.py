#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""film-studio 仓库结构自检（CI 用，零第三方依赖）

守住 CLAUDE.md 里那些靠人记的约定：三处版本号一致、每个技能都有运行时适配块与交付自检、
每个 agent 的 frontmatter 完整、两份 marketplace 清单同步，以及最容易出事的一条——
**新增了 tools/ 脚本却忘了挂进 `/new-drama` 的复制清单**（挂漏了 agent 就够不到该文件，
功能会静默失效）。

    python scripts/ci_check.py

退出码：0 = 全过；1 = 有检查未通过。
"""

import json
import os
import py_compile
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "film-studio")

failures = []
passes = []


def ok(message):
    passes.append(message)


def fail(message):
    failures.append(message)


def read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def frontmatter(text, where):
    """极简 YAML frontmatter 解析：只取顶格的 key: value，够本仓库用。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail("%s：缺少 YAML frontmatter（首行必须是 ---）" % where)
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if line[:1] not in (" ", "\t", "#", "") and ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    fail("%s：frontmatter 没有闭合的 ---" % where)
    return None


# --------------------------------------------------------------------------

def check_version_sync():
    """CLAUDE.md 规则 7：VERSION / plugin.json / marketplace.json 三处版本一致。"""
    version = read(os.path.join(ROOT, "VERSION")).strip()
    plugin_version = load_json(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"))["version"]
    market = load_json(os.path.join(ROOT, ".claude-plugin", "marketplace.json"))
    market_version = market.get("metadata", {}).get("version")

    found = {"VERSION": version,
             "plugin.json": plugin_version,
             "marketplace.json": market_version}
    if len(set(found.values())) != 1:
        fail("三处版本号不一致：%s" % ", ".join("%s=%s" % kv for kv in found.items()))
    else:
        ok("三处版本号一致（%s）" % version)


def check_all_json_parses():
    bad = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for name in files:
            if not name.endswith(".json"):
                continue
            path = os.path.join(base, name)
            try:
                load_json(path)
            except ValueError as exc:
                bad.append("%s（%s）" % (os.path.relpath(path, ROOT), exc))
    if bad:
        fail("JSON 解析失败：%s" % "；".join(bad))
    else:
        ok("所有 JSON 文件可解析")


def check_skills():
    """每个 SKILL.md：frontmatter 完整、name 与目录名一致、有运行时适配块、有交付自检。"""
    skills_dir = os.path.join(PLUGIN, "skills")
    names = sorted(os.listdir(skills_dir))
    problems = 0
    for name in names:
        path = os.path.join(skills_dir, name, "SKILL.md")
        where = "skills/%s/SKILL.md" % name
        if not os.path.isfile(path):
            fail("%s：目录下没有 SKILL.md" % where)
            problems += 1
            continue
        text = read(path)
        fields = frontmatter(text, where)
        if fields is None:
            problems += 1
            continue
        if fields.get("name") != name:
            fail("%s：frontmatter 的 name=%r 与目录名 %r 不一致" % (where, fields.get("name"), name))
            problems += 1
        if not fields.get("description"):
            fail("%s：frontmatter 缺 description（技能靠它被触发）" % where)
            problems += 1
        # CLAUDE.md 规则 5：跨运行时兼容的必要条件
        if "运行时适配" not in text:
            fail("%s：缺「运行时适配」块——Codex/OpenClaw 等不支持 subagent 的运行时会不可用" % where)
            problems += 1
        if "交付自检" not in text and "交付前自查" not in text:
            fail("%s：缺交付自检块（每个技能都要有可判定的通过判据）" % where)
            problems += 1
    if not problems:
        ok("%d 个技能的 frontmatter、运行时适配块、交付自检齐备" % len(names))


def check_agents():
    agents_dir = os.path.join(PLUGIN, "agents")
    names = sorted(n for n in os.listdir(agents_dir) if n.endswith(".md"))
    problems = 0
    for name in names:
        stem = name[:-3]
        where = "agents/%s" % name
        fields = frontmatter(read(os.path.join(agents_dir, name)), where)
        if fields is None:
            problems += 1
            continue
        if fields.get("name") != stem:
            fail("%s：frontmatter 的 name=%r 与文件名 %r 不一致" % (where, fields.get("name"), stem))
            problems += 1
        for key in ("description", "tools"):
            if not fields.get(key):
                fail("%s：frontmatter 缺 %s" % (where, key))
                problems += 1
    if not problems:
        ok("%d 个 agent 的 frontmatter 完整" % len(names))


def check_new_drama_copy_list():
    """CLAUDE.md 规则 2：agent 够不到插件根，凡是 agent 要用的文件必须在建项时复制进工作区。

    新增 tools/ 脚本却忘了挂进复制清单，是这条规则最容易踩的坑——功能会静默失效，
    因为脚本在插件里好好的，只是工作区里没有。
    """
    text = read(os.path.join(PLUGIN, "skills", "new-drama", "SKILL.md"))
    tools = sorted(n for n in os.listdir(os.path.join(PLUGIN, "tools")) if n.endswith(".py"))
    missing = [n for n in tools if n not in text]
    if missing:
        fail("这些 tools/ 脚本没出现在 /new-drama 的复制清单里，工作区拿不到：%s" % "、".join(missing))
    elif "schemas" not in text:
        fail("/new-drama 的复制清单没提 schemas/，validate_project.py 在工作区会找不到 schema")
    else:
        ok("%d 个 tools/ 脚本 + schemas/ 都挂进了 /new-drama 复制清单" % len(tools))


TOOL_REFERENCE = re.compile(r"tools/([a-z_]+\.py)")
SELF_HEAL_WORDS = ("复制", "补一份", "补齐")


def check_tool_self_heal():
    """技能里用到某个 tools/ 脚本，就必须同时给出「工作区缺了从插件根补一份」的自愈指引。

    只靠 `/new-drama` 复制是不够的：老工作区是在该脚本存在之前建的，跑到用它的那一步
    会直接失败。仓库里 design/edit/finalcut/previz 都已是这个写法，这里把它变成强制。
    """
    skills_dir = os.path.join(PLUGIN, "skills")
    problems = []
    for name in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path) or name == "new-drama":
            continue  # new-drama 本身就是那份复制清单
        text = read(path)
        for tool in sorted(set(TOOL_REFERENCE.findall(text))):
            # 用邻近窗口而不是整行匹配：说明文字常因排版折行，工具名和"复制"未必同行
            healed = False
            for match in re.finditer(re.escape(tool), text):
                window = text[max(0, match.start() - 150):match.end() + 150]
                if any(word in window for word in SELF_HEAL_WORDS):
                    healed = True
                    break
            if not healed:
                problems.append("skills/%s/SKILL.md 用了 tools/%s 却没有「缺了从插件根补一份」的指引"
                                % (name, tool))
    if problems:
        fail("工具自愈指引缺失（老工作区跑到这一步会失败）：\n         "
             + "\n         ".join(problems))
    else:
        ok("引用了 tools/ 脚本的技能都带了自愈指引")


def check_marketplaces():
    """两份 marketplace 清单必须同步指向同一个插件目录。"""
    claude = load_json(os.path.join(ROOT, ".claude-plugin", "marketplace.json"))
    codex = load_json(os.path.join(ROOT, ".agents", "plugins", "marketplace.json"))

    claude_entries = {p["name"]: p.get("source") for p in claude.get("plugins", [])}
    codex_entries = {}
    for plugin in codex.get("plugins", []):
        source = plugin.get("source")
        if not isinstance(source, dict):
            fail("Codex marketplace 的 source 必须是对象形式，%r 不是" % plugin.get("name"))
            continue
        codex_entries[plugin["name"]] = source.get("path")

    if set(claude_entries) != set(codex_entries):
        fail("两份 marketplace 的插件条目不一致：Claude=%s，Codex=%s"
             % (sorted(claude_entries), sorted(codex_entries)))
        return

    for name, source in claude_entries.items():
        codex_path = codex_entries[name]
        if source != codex_path:
            fail("插件 %s 在两份 marketplace 里的 source 不一致（%s vs %s）"
                 % (name, source, codex_path))
            continue
        target = os.path.join(ROOT, source)
        if not os.path.isdir(target):
            fail("插件 %s 的 source 指向不存在的目录：%s" % (name, source))
            continue
        # Codex 要求插件位于 marketplace 根的子目录，"./" 自托管会被拒
        if os.path.normpath(target) == os.path.normpath(ROOT):
            fail("插件 %s 的 source 指向仓库根，Codex 会拒绝安装（必须在子目录）" % name)
            continue
        if not os.path.isfile(os.path.join(target, ".claude-plugin", "plugin.json")):
            fail("插件 %s 的目录下没有 .claude-plugin/plugin.json" % name)
    ok("两份 marketplace 清单同步，插件位于子目录且 manifest 就位")


def check_python_compiles():
    bad = []
    with tempfile.TemporaryDirectory() as scratch:
        for directory in (os.path.join(PLUGIN, "tools"), os.path.join(ROOT, "scripts")):
            if not os.path.isdir(directory):
                continue
            for name in sorted(os.listdir(directory)):
                if not name.endswith(".py"):
                    continue
                path = os.path.join(directory, name)
                try:
                    py_compile.compile(path, cfile=os.path.join(scratch, name + "c"),
                                       doraise=True)
                except py_compile.PyCompileError as exc:
                    bad.append("%s（%s）" % (name, exc))
    if bad:
        fail("Python 语法错误：%s" % "；".join(bad))
    else:
        ok("所有 Python 脚本语法正确")


COUNT_CLAIMS = [
    (re.compile(r"(\d+)\s*个(?:影视)?专业\s*agent"), "agent"),
    (re.compile(r"(\d+)\s*个 agent"), "agent"),
    (re.compile(r"(\d+)\s*个技能"), "skill"),
    (re.compile(r"(\d+)\s+(?:specialist|professional)\s+agents"), "agent"),
    (re.compile(r"(\d+)\s+skills"), "skill"),
]

CLAIM_FILES = [
    "README.md",
    "README.en.md",
    "CLAUDE.md",
    os.path.join("plugins", "film-studio", "templates", "workspace-CLAUDE.md"),
]


def check_count_claims():
    """文档里写死的"N 个 agent / N 个技能"最容易随新增能力而过时，逐处比对实际数量。"""
    skills = len([n for n in os.listdir(os.path.join(PLUGIN, "skills"))
                  if os.path.isdir(os.path.join(PLUGIN, "skills", n))])
    agents = len([n for n in os.listdir(os.path.join(PLUGIN, "agents")) if n.endswith(".md")])
    actual = {"skill": skills, "agent": agents}

    stale = []
    for relative in CLAIM_FILES:
        path = os.path.join(ROOT, relative)
        if not os.path.isfile(path):
            continue
        text = read(path)
        for pattern, kind in COUNT_CLAIMS:
            for match in pattern.finditer(text):
                claimed = int(match.group(1))
                if claimed != actual[kind]:
                    line = text[:match.start()].count("\n") + 1
                    stale.append("%s:%d 写着「%s」，实际 %d 个"
                                 % (relative, line, match.group(0), actual[kind]))
    if stale:
        fail("文档里的数量声明过时：\n         " + "\n         ".join(stale))
    else:
        ok("文档的数量声明与实际一致（%d 技能 / %d agent）" % (skills, agents))


def main():
    for check in (check_version_sync, check_all_json_parses, check_skills, check_agents,
                  check_new_drama_copy_list, check_tool_self_heal, check_marketplaces,
                  check_python_compiles, check_count_claims):
        try:
            check()
        except Exception as exc:  # 检查本身炸了也算失败，别静默跳过
            fail("%s 执行失败：%s: %s" % (check.__name__, type(exc).__name__, exc))

    for message in passes:
        print("[OK]   %s" % message)
    for message in failures:
        print("[FAIL] %s" % message)

    print("\n%d 项通过，%d 项失败" % (len(passes), len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
