# -*- coding: utf-8 -*-
"""元素定位库（locators.py）的解析与体检
==========================================
`locators.py` 是项目里唯一的定位来源，250 条条目全靠人肉维护。本模块把它
**读成结构化数据**并做一组体检，供 run_gui.py 的「元素定位」窗口使用。

只读模块：不改 locators.py，也不 import 它（用 AST 解析，避免任何副作用）。
"""

import ast
import collections
import io
import os
import re
import subprocess
import sys
import tokenize

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCATORS_PATH = os.path.join(PROJECT_ROOT, "locators.py")

# 扫描「谁在用」时要跳过的目录
_SKIP_DIRS = {
    ".venv", "__pycache__", ".workbuddy", ".git", "logs", "reports", "node_modules",
}

# 超长 selector 阈值（超过就列出来，便于拆分或改用 id）
LONG_SELECTOR = 150
# 体检明细最多展示的条数（避免界面里堆上千行）
MAX_ISSUES_PER_KIND = 200

_SECTION_RE = re.compile(r"^#\s*=+\s*(.+?)\s*=+\s*$")
_REF_RE = re.compile(r'LOCATORS\[\s*["\']([^"\']+)["\']\s*\]')


# --------------------------------------------------------------------------
# 解析
# --------------------------------------------------------------------------
def _read(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def _by_name(node):
    """取出 By 的名字：AppiumBy.ID -> 'ID'；字符串常量 'class name' 原样返回。"""
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Constant):
        return str(node.value)
    return None


def _comments(src):
    """行号 -> 行尾注释原文（含 #）。用 tokenize 取，字符串里的 # 不会误判。"""
    out = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                out.setdefault(tok.start[0], tok.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return out


def _sections(src):
    """分段标记：`# ============ 通用 ============` -> [(行号, 标题), ...]。"""
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        m = _SECTION_RE.match(line.strip())
        if m:
            out.append((i, m.group(1)))
    return out


def _section_of(sections, lineno):
    cur = "未分段"
    for ln, title in sections:
        if ln < lineno:
            cur = title
        else:
            break
    return cur


def parse(path=LOCATORS_PATH):
    """解析 locators.py。

    返回 (entries, duplicate_keys)：
      entries        —— 按源码顺序，每项 {key, by, selector, comment, lineno, section}
      duplicate_keys —— 同一个 key 被定义多次的名字（后者会静默覆盖前者）
    """
    src = _read(path)
    tree = ast.parse(src)
    comments = _comments(src)
    sections = _sections(src)

    node = None
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and getattr(stmt.targets[0], "id", "") == "LOCATORS":
            node = stmt.value
            break
    if node is None:
        return [], []

    entries, seen, duplicated = [], set(), []
    for k_node, v_node in zip(node.keys, node.values):
        try:
            key = ast.literal_eval(k_node)
        except (ValueError, SyntaxError):
            continue
        if not isinstance(key, str):
            continue
        lineno = k_node.lineno
        by, selector = None, None
        if isinstance(v_node, (ast.Tuple, ast.List)) and len(v_node.elts) == 2:
            by = _by_name(v_node.elts[0])
            try:
                selector = ast.literal_eval(v_node.elts[1])
            except (ValueError, SyntaxError):
                selector = None
        selector = selector if isinstance(selector, str) else ""

        if key in seen and key not in duplicated:
            duplicated.append(key)
        seen.add(key)

        comment = comments.get(lineno, "")
        entries.append({
            "key": key,
            "by": by or "?",
            "selector": selector,
            "comment": comment.lstrip("#").strip(),
            "lineno": lineno,
            "section": _section_of(sections, lineno),
        })
    return entries, duplicated


# --------------------------------------------------------------------------
# 引用索引：谁在用这些 key
# --------------------------------------------------------------------------
def _iter_py_files():
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                if os.path.abspath(path) != os.path.abspath(LOCATORS_PATH):
                    yield path


def _refs_in_source(src):
    """统计一段源码里引用到的 key。

    优先用 AST：只认真正的 ``LOCATORS["key"]`` 下标访问（含 ``find(driver, "key")``），
    这样文档字符串 / 注释里写的示例不会被误算成真实引用 —— 正则做不到这一点
    （本模块自己的 docstring 就踩过这个坑，凭空多报一条「引用缺失」）。
    源码语法有误时退回正则。
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return collections.Counter(_REF_RE.findall(src))

    counter = collections.Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            base = node.value
            name = base.id if isinstance(base, ast.Name) else None
            if name != "LOCATORS":
                continue
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                counter[sl.value] += 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("find", "click_key") and len(node.args) >= 2:
                arg = node.args[1]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    counter[arg.value] += 1
    return counter


def usage_index():
    """{key: [(相对文件名, 出现次数), ...]}。

    只认 ``LOCATORS["key"]`` 这一种写法（项目里 651 处引用全是它）。
    """
    index = {}
    for path in _iter_py_files():
        try:
            text = _read(path)
        except (OSError, UnicodeDecodeError):
            continue
        rel = os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")
        for key, n in _refs_in_source(text).items():
            index.setdefault(key, {})
            index[key][rel] = index[key].get(rel, 0) + n
    return {k: sorted(v.items(), key=lambda x: -x[1]) for k, v in index.items()}


# --------------------------------------------------------------------------
# 体检
# --------------------------------------------------------------------------
def check(entries=None, duplicated=None, usage=None):
    """返回体检问题列表。每项 {level, kind, key, lineno, detail}。

    level: error（会直接报错）/ warn（会失效或易错）/ info（可读性、维护性）
    """
    if entries is None or duplicated is None:
        entries, duplicated = parse()
    if usage is None:
        usage = usage_index()

    defined = {e["key"] for e in entries}
    issues = []

    def add(level, kind, key, lineno, detail):
        issues.append({
            "level": level, "kind": kind, "key": key,
            "lineno": lineno, "detail": detail,
        })

    for key in duplicated:
        lns = [e["lineno"] for e in entries if e["key"] == key]
        add("error", "重复定义", key, lns[0] if lns else 0,
            "定义为 %d 次（行 %s），后面的会静默覆盖前面的"
            % (len(lns), "、".join(map(str, lns))))

    for key in sorted(set(usage) - defined):
        files = "、".join(f for f, _ in usage[key])
        add("error", "引用缺失", key, 0,
            "用例引用了它，但 locators.py 里没有定义 —— 运行到会 KeyError（%s）" % files)

    by_sel = {}
    for e in entries:
        by_sel.setdefault((e["by"], e["selector"]), []).append(e)
    for (by, sel), group in by_sel.items():
        if len(group) > 1:
            add("warn", "定位重复", group[0]["key"], group[0]["lineno"],
                "%s 个 key 指向同一个 %s 定位：%s"
                % (len(group), by, "、".join(g["key"] for g in group)))

    for e in entries:
        if e["key"] not in usage:
            add("info", "未被使用", e["key"], e["lineno"],
                "没有任何用例引用它（改动/删除前先确认不是给将来留的）")
        if "@text=" in e["selector"]:
            add("warn", "@text 硬编码", e["key"], e["lineno"],
                "XPATH 里写死了界面文案，开发改字或多语言就会失效")
        if len(e["selector"]) > LONG_SELECTOR:
            add("info", "selector 过长", e["key"], e["lineno"],
                "%d 字符，建议改用 resource-id 或抽成更短的定位" % len(e["selector"]))
        if any("\u4e00" <= c <= "\u9fff" for c in e["key"]):
            add("info", "key 含中文", e["key"], e["lineno"],
                "与英文命名混用，不好记也不好在代码里搜")
        if not e["comment"]:
            add("info", "缺少注释", e["key"], e["lineno"],
                "行尾没有中文注释，看不出这元素是干什么的")

    order = {"error": 0, "warn": 1, "info": 2}
    issues.sort(key=lambda i: (order.get(i["level"], 9), i["kind"], i["lineno"]))
    return issues


def stats(entries=None, usage=None, issues=None):
    """汇总统计，供界面顶部展示。"""
    if entries is None:
        entries, _dup = parse()
    if usage is None:
        usage = usage_index()
    if issues is None:
        issues = check(entries, None, usage)

    by_count = {}
    for e in entries:
        by_count[e["by"]] = by_count.get(e["by"], 0) + 1

    return {
        "total": len(entries),
        "by": by_count,
        "sections": len({e["section"] for e in entries}),
        "refs": sum(sum(c for _, c in v) for v in usage.values()),
        "used": len({e["key"] for e in entries} & set(usage)),
        "error": sum(1 for i in issues if i["level"] == "error"),
        "warn": sum(1 for i in issues if i["level"] == "warn"),
        "info": sum(1 for i in issues if i["level"] == "info"),
    }


def report():
    """一次性返回界面需要的全部数据。"""
    entries, duplicated = parse()
    usage = usage_index()
    issues = check(entries, duplicated, usage)
    return {
        "entries": entries,
        "duplicated": duplicated,
        "usage": usage,
        "issues": issues,
        "stats": stats(entries, usage, issues),
        "path": LOCATORS_PATH,
    }


def issues_of_key(issues, key):
    return [i for i in issues if i["key"] == key]


# --------------------------------------------------------------------------
# 打开源码对应行
# --------------------------------------------------------------------------
def _editor_cmd():
    """找可用的编辑器命令行（带 -g 跳行号）。找不到就返回 None。"""
    for exe in ("code", "code-insiders", "subl", "notepad++"):
        try:
            subprocess.run([exe, "--version"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=5)
            return exe
        except (OSError, subprocess.SubprocessError):
            continue
    return None


def open_source(lineno=None):
    """在编辑器里打开 locators.py（尽量跳到指定行）。返回说明文字。"""
    exe = _editor_cmd()
    if exe:
        args = [exe, "-g", "%s:%d" % (LOCATORS_PATH, lineno or 1)] \
            if exe != "notepad++" else [exe, "-n%d" % (lineno or 1), LOCATORS_PATH]
        try:
            subprocess.Popen(args)
            return "已用 %s 打开 locators.py 第 %s 行" % (exe, lineno or 1)
        except OSError:
            pass
    try:
        os.startfile(LOCATORS_PATH)          # Windows：交给默认程序
        return "已用系统默认程序打开 locators.py（未能定位到第 %s 行）" % (lineno or 1)
    except OSError as e:
        return "打开失败：%s" % e


# --------------------------------------------------------------------------
# 命令行
# --------------------------------------------------------------------------
_LEVEL_TAG = {"error": "[错误]", "warn": "[警告]", "info": "[提示]"}


def _cli_show():
    entries, _ = parse()
    print("locators.py 共 %d 条定位：" % len(entries))
    for e in entries:
        print("  %4d 行  %-28s %-12s %s   # %s"
              % (e["lineno"], e["key"], e["by"], e["selector"][:60], e["comment"]))
    return 0


def _cli_check(only_errors=False):
    data = report()
    st = data["stats"]
    print("locators.py：%d 条定位，被引用 %d 次（覆盖 %d 条键）"
          % (st["total"], st["refs"], st["used"]))
    print("体检：错误 %d / 警告 %d / 提示 %d\n"
          % (st["error"], st["warn"], st["info"]))

    counts = {}
    for it in data["issues"]:
        counts[it["kind"]] = counts.get(it["kind"], 0) + 1
    for kind, n in sorted(counts.items(), key=lambda x: -x[1]):
        print("  %-14s %d 项" % (kind, n))

    print()
    shown = 0
    for it in data["issues"]:
        if only_errors and it["level"] != "error":
            continue
        if shown >= MAX_ISSUES_PER_KIND * 3:
            print("  ...（略）")
            break
        print("  %s %-12s %-24s 第 %4d 行  %s"
              % (_LEVEL_TAG.get(it["level"], "?"), it["kind"], it["key"],
                 it["lineno"], it["detail"]))
        shown += 1
    return 1 if st["error"] else 0


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="locators.py 解析与体检")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("show", help="列出全部定位")
    p_check = sub.add_parser("check", help="体检报告")
    p_check.add_argument("--errors", action="store_true", help="只列错误级问题")
    args = p.parse_args(argv)

    if args.cmd == "show":
        return _cli_show()
    return _cli_check(getattr(args, "errors", False))


if __name__ == "__main__":
    sys.exit(main())
