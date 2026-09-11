# -*- coding: utf-8 -*-
"""测试参数「源码直改」编辑器
============================
本项目里「会随测试对象变化」的变量（打印机编号、登录手机号、耗材尺寸 …）
**就写在用例文件顶部**，本模块负责把界面上填的新值**直接改写回源码那几行**。

    testcases/test_release.py::

        # ----------------统一管理变量----------------
        device_number1 = "T0013B2507037084"  # 第一台打印机编号（官方耗材）
        device_number2 = "T0024B2024071849"  # 第二台打印机编号(自定义耗材)
        ...

设计要点（都是为了让「改源码」这件事不至于失控）：

1. **用 AST 定位，不用正则**：只认模块级的 ``名字 = 字面量`` 赋值，函数体内的
   同名局部变量、注释掉的行都不会被误伤。
2. **只改那一行**：其余字节原样保留；行尾注释原样带走，整块的注释对齐列
   会按新值长度重算（值长度不变时输出与原文件逐字节一致）。
3. **写完先自检**：新内容先过一遍 ``ast.parse``，语法不合法直接放弃，绝不落盘。
4. **原子替换 + 留备份**：先写同目录临时文件再 ``os.replace``；改写前把原文件
   备份到 ``logs/param_backups/``，改坏了可以 ``python param_editor.py restore``。
5. **按文件隔离**：两个用例文件面向的测试对象本就不同（T0013… 官方耗材 /
   T0109… 商超耗材），耗材尺寸也不一样。哪个文件填的值只写进哪个文件。

命令行（可选，界面不是唯一入口）：

    python param_editor.py show                    # 列出各文件当前值与所在行号
    python param_editor.py set diy_width=40 --file test_release.py
    python param_editor.py restore --file test_release.py   # 回滚到最近一次备份
"""

import argparse
import ast
import datetime
import io
import os
import shutil
import sys
import tokenize

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TESTCASE_DIR = os.path.join(PROJECT_ROOT, "testcases")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "logs", "param_backups")

# --------------------------------------------------------------------------
# 字段定义：顺序 + 中文标签，界面与命令行都按这个顺序展示
# 新增参数时只在这里加一行，其余逻辑自动适配
# --------------------------------------------------------------------------
FIELDS = (
    ("device_number1", "第一台打印机编号（官方耗材）"),
    ("device_number2", "第二台打印机编号（自定义耗材）"),
    ("device_number3", "第三台打印机编号（商超耗材）"),
    ("telephone_number", "登录手机号"),
    ("diy_width", "自定义耗材宽度"),
    ("diy_height", "自定义耗材高度"),
    ("diy_gap", "自定义耗材间隙"),
)
FIELD_LABELS = dict(FIELDS)
FIELD_ORDER = [k for k, _ in FIELDS]

# 初始值 = 各用例文件改造前的原始硬编码值，「恢复默认值」用它们
SEED = {
    "test_release.py": {
        "device_number1": "T0013B2507037084",
        "device_number2": "T0024B2024071849",
        "telephone_number": "17777786604",
        "diy_width": "50",
        "diy_height": "30",
        "diy_gap": "3",
    },
    "test_release_home.py": {
        "device_number1": "T0109A2024041502",
        "device_number2": "T0171A2504150001",
        "device_number3": "T0109A2024041502",
        "telephone_number": "17777786604",
        "diy_width": "30",
        "diy_height": "20",
        "diy_gap": "8",
    },
}


# --------------------------------------------------------------------------
# 基础读写
# --------------------------------------------------------------------------
def file_path(fname):
    """用例文件名 -> 绝对路径（也接受已经是路径的入参）。"""
    s = str(fname)
    if os.path.isabs(s) or os.sep in s or "/" in s:
        return s
    return os.path.join(TESTCASE_DIR, s)


def _read_text(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return f.read()


def _atomic_write(path, text):
    """先写临时文件再替换，避免写到一半被中断留下半个文件。"""
    tmp = path + ".tmp-paramedit"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


# --------------------------------------------------------------------------
# 解析：找出「参数块」里的那些赋值行
# --------------------------------------------------------------------------
def _literal(node):
    """取出赋值右侧的字面量；非字面量（表达式）返回 (None, False)。"""
    try:
        val = ast.literal_eval(node)
    except (ValueError, SyntaxError, TypeError):
        return None, False
    if isinstance(val, str):
        return val, True
    if isinstance(val, (int, float)):
        return str(val), False
    return None, False


def _comments(src):
    """行号 -> 该行的行尾注释原文（含 #）。用 tokenize 取，避免误伤字符串里的 #。"""
    out = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                out.setdefault(tok.start[0], tok.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return out


def parse_source(src):
    """从源码文本里提取参数槽。返回 {字段: slot}，按 FIELD_ORDER 排序。

    slot = {"value": 当前值(字符串) | None, "lineno": 行号, "raw": 该行原文}
    """
    tree = ast.parse(src)
    cmts = _comments(src)
    lines = src.splitlines()
    found = {}
    for node in tree.body:                      # 只看模块级，函数内的同名变量不管
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Name) or tgt.id not in FIELD_LABELS:
            continue
        if tgt.id in found:                     # 同名只认第一次出现的
            continue
        if node.end_lineno != node.lineno:      # 跨行赋值不动，避免改坏
            continue
        value, _is_str = _literal(node.value)
        found[tgt.id] = {
            "value": value,
            "lineno": node.lineno,
            "raw": lines[node.lineno - 1] if node.lineno <= len(lines) else "",
            "comment": cmts.get(node.lineno, ""),
        }
    return {k: found[k] for k in FIELD_ORDER if k in found}


def has_block(fname):
    """该文件是否存在可改写的参数块（GUI 用它判断是否需要强制弹窗）。"""
    path = file_path(fname)
    if not os.path.isfile(path):
        return False
    try:
        return bool(parse_source(_read_text(path)))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False


def case_files():
    """testcases/ 下所有含参数块的 test_*.py（按名称排序）。"""
    out = []
    try:
        names = sorted(os.listdir(TESTCASE_DIR))
    except OSError:
        return out
    for name in names:
        if name.startswith("test_") and name.endswith(".py") and name != "__init__.py":
            if has_block(name):
                out.append(name)
    return out


def scan(fnames=None):
    """{文件名: {字段: slot}}。fnames 为空时扫描全部用例文件。"""
    result = {}
    for fname in list(fnames) if fnames else case_files():
        path = file_path(fname)
        if not os.path.isfile(path):
            continue
        try:
            slots = parse_source(_read_text(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        if slots:
            result[os.path.basename(str(fname))] = slots
    return result


def read_params(fname):
    """返回该文件当前的 {字段: 值}（仅含该文件真正写着的字段）。"""
    return {k: s["value"] for k, s in (scan([fname]).get(os.path.basename(str(fname))) or {}).items()}


# --------------------------------------------------------------------------
# 改写
# --------------------------------------------------------------------------
def _render(src, slots, updates):
    """按 updates 重写参数块，返回新源码。

    整块重算注释对齐列 —— 值变长变短后注释仍然整齐；值不变时输出与原文一致。
    """
    lines = src.splitlines(keepends=True)
    values = {k: (updates[k] if k in updates else s["value"]) for k, s in slots.items()}
    prefixes = {k: '{} = "{}"'.format(k, v if v is not None else "") for k, v in values.items()}
    width = max(len(p) for p in prefixes.values()) + 2

    for key, slot in slots.items():
        ln = slot["lineno"]
        eol = "\r\n" if lines[ln - 1].endswith("\r\n") else "\n"
        text = prefixes[key].ljust(width)
        if slot["comment"]:
            text += slot["comment"]
        lines[ln - 1] = text.rstrip() + eol
    return "".join(lines)


def _backup(path, fname):
    """改写前留一份备份，出问题可 restore。返回备份路径或 None。"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(BACKUP_DIR, "{}.{}.bak".format(fname, stamp))
        shutil.copy2(path, dst)
        return dst
    except OSError:
        return None


def _clean_values(fname, values, slots):
    """过滤出可安全写入的值，返回 (updates, errors)。"""
    updates, errors = {}, []
    for key, val in values.items():
        if key not in FIELD_LABELS:
            errors.append("{}：未知字段 {}".format(fname, key))
            continue
        if key not in slots:
            continue                        # 该文件本来没这个参数，不硬塞
        sval = "" if val is None else str(val).strip()
        if any(c in sval for c in ('"', "\\", "\n", "\r")):
            errors.append("{}：{} 的值不能包含引号、反斜杠或换行".format(fname, FIELD_LABELS[key]))
            continue
        updates[key] = sval
    return updates, errors


def apply(mapping):
    """把 {文件名: {字段: 新值}} 直接写进各自用例源码。

    返回 (changed, errors)：changed 是被真正改动的文件名列表。
    一个文件出错不影响其它文件；没变化的文件不落盘、不备份。
    """
    changed, errors = [], []
    for fname, values in mapping.items():
        name = os.path.basename(str(fname))
        path = file_path(fname)
        if not os.path.isfile(path):
            errors.append("{}：找不到文件".format(name))
            continue
        try:
            src = _read_text(path)
            slots = parse_source(src)
        except SyntaxError as e:
            errors.append("{}：当前源码语法有误，未改动（{}）".format(name, e))
            continue
        except (OSError, UnicodeDecodeError) as e:
            errors.append("{}：读取失败（{}）".format(name, e))
            continue
        if not slots:
            errors.append("{}：没找到可改写的参数块，已跳过".format(name))
            continue

        updates, errs = _clean_values(name, values, slots)
        errors.extend(errs)
        if not updates:
            continue

        new_src = _render(src, slots, updates)
        if new_src == src:
            continue                        # 值没变，不动文件
        try:
            ast.parse(new_src)              # 落盘前的最后一道闸
        except SyntaxError as e:
            errors.append("{}：改写后语法不合法，已放弃（{}）".format(name, e))
            continue
        backup = _backup(path, name)        # 先留退路，再动原文件
        try:
            _atomic_write(path, new_src)
        except OSError as e:
            errors.append("{}：写入失败（{}）".format(name, e))
            continue
        changed.append(name if backup else "{}（备份失败）".format(name))
    # 备份失败不影响改写本身，但要让调用方看到，故拼进名字里一并返回
    return changed, errors


def reset(fnames=None):
    """把参数恢复成 SEED 里的初始值（只含该文件本来就有的字段）。"""
    mapping = {}
    for fname in list(fnames) if fnames else list(SEED):
        seed = SEED.get(os.path.basename(str(fname)))
        if seed:
            mapping[os.path.basename(str(fname))] = seed
    return apply(mapping)


def latest_backup(fname):
    name = os.path.basename(str(fname))
    try:
        cands = sorted(
            f for f in os.listdir(BACKUP_DIR)
            if f.startswith(name + ".") and f.endswith(".bak")
        )
    except OSError:
        return None
    return os.path.join(BACKUP_DIR, cands[-1]) if cands else None


def restore(fname):
    """回滚到最近一次备份。返回 (ok, 说明)。"""
    name = os.path.basename(str(fname))
    bak = latest_backup(name)
    if not bak:
        return False, "{}：没有找到备份".format(name)
    try:
        _atomic_write(file_path(name), _read_text(bak))
    except OSError as e:
        return False, "{}：回滚失败（{}）".format(name, e)
    return True, "{}：已回滚到 {}".format(name, os.path.basename(bak))


# --------------------------------------------------------------------------
# 命令行
# --------------------------------------------------------------------------
def _cli_show():
    data = scan()
    if not data:
        print("testcases/ 下没有找到含参数块的 test_*.py。")
        return 0
    for fname, slots in data.items():
        print("\n[{}]  {}".format(fname, file_path(fname)))
        for key, slot in slots.items():
            print(
                "    第 {:>3} 行  {:<18} = {:<22} # {}".format(
                    slot["lineno"], key, slot["value"], FIELD_LABELS[key]
                )
            )
    print()
    return 0


def _cli_set(pairs, fname):
    values = {}
    for item in pairs:
        if "=" not in item:
            print("参数格式应为 key=value，收到：{}".format(item))
            return 2
        key, val = item.split("=", 1)
        key = key.strip()
        if key not in FIELD_LABELS:
            print("未知字段：{}\n可选：{}".format(key, ", ".join(FIELD_ORDER)))
            return 2
        values[key] = val.strip()

    targets = [os.path.basename(fname)] if fname else case_files()
    changed, errors = apply({t: values for t in targets})
    for e in errors:
        print("[跳过] " + e)
    if changed:
        print("已改写源码：" + "，".join(changed))
    elif not errors:
        print("值没有变化，未改动任何文件。")
    return 1 if errors and not changed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="测试参数源码直改")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("show", help="列出各用例文件的参数值及所在行号")
    p_set = sub.add_parser("set", help="改写参数，如 set diy_width=40")
    p_set.add_argument("pairs", nargs="+", help="key=value，可写多个")
    p_set.add_argument("--file", default=None, help="只改该文件，默认改所有含该参数的文件")
    p_reset = sub.add_parser("reset", help="恢复为初始值")
    p_reset.add_argument("--file", default=None, help="只恢复该文件")
    p_restore = sub.add_parser("restore", help="回滚到最近一次备份")
    p_restore.add_argument("--file", required=True, help="要回滚的用例文件")

    args = parser.parse_args(argv)

    if args.cmd == "set":
        return _cli_set(args.pairs, args.file)
    if args.cmd == "reset":
        changed, errors = reset([args.file] if args.file else None)
        for e in errors:
            print("[跳过] " + e)
        print("已恢复初始值：" + ("，".join(changed) if changed else "无变化"))
        return 0
    if args.cmd == "restore":
        ok, msg = restore(args.file)
        print(msg)
        return 0 if ok else 1

    return _cli_show()


if __name__ == "__main__":
    sys.exit(main())
