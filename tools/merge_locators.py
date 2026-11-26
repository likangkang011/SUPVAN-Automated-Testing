# -*- coding: utf-8 -*-
"""
把生成的定位条目合并进 locators.py
==================================
读 logs/ui_dump/generated_locators.json，把 selector 尚未存在于 locators.py 的条目
追加到 LOCATORS 末尾的「自动抓取」段，按页面分组，写完自动校验：

  1. locators.py 可正常 import
  2. 新增 key 与原有 key 无重名
  3. 新增 selector 与原有 selector 无重复

用法：
    python tools/merge_locators.py            # 执行合并
    python tools/merge_locators.py --dry-run  # 只看会加多少条
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCATORS_PY = os.path.join(ROOT, "locators.py")
GEN_JSON = os.path.join(ROOT, "logs", "ui_dump", "generated_locators.json")

MARKER = "# ============ 自动抓取（真实控件树 dump，可整段删除） ============"

# 即使用不到文案/点击，也值得保留的控件类型
KEEP_CLASSES = {
    "android.widget.EditText", "android.widget.ImageView", "android.widget.Button",
    "android.widget.Switch", "android.widget.CheckBox", "android.widget.RadioButton",
    "android.widget.SeekBar", "android.widget.TextView", "android.widget.RadioGroup",
}


def load_existing():
    src = open(LOCATORS_PY, encoding="utf-8").read()
    keys = set(re.findall(r'^\s{4}"([^"]+)"\s*:\s*\(', src, re.M))
    sels = set()
    for m in re.finditer(r'^\s{4}"[^"]+"\s*:\s*\(\s*[^,]+,\s*(.+?)\)\s*,?\s*(?:#.*)?$', src, re.M):
        raw = m.group(1).strip()
        lit = re.match(r"""^[fFrRbB]?['"](.+)['"]$""", raw)
        sels.add(lit.group(1) if lit else raw)
    return src, keys, sels


def render(records):
    order = ["首页", "我的", "查找设备", "新建标签/耗材选择",
             "编辑页与功能栏", "其他页面"]
    records = sorted(records, key=lambda r: (order.index(r["group"])
                                             if r["group"] in order else len(order),
                                             r["key"]))
    lines = ["", f"    {MARKER}"]
    lines.append("    # 由 tools/gen_locators.py 从 logs/ui_dump/*.xml 生成；")
    lines.append("    # 条目名按「控件 id 转下划线」命名，页面归属见行尾注释。")
    group = None
    for r in records:
        if r["group"] != group:
            group = r["group"]
            lines.append("")
            lines.append(f"    # ---------- {group} ----------")
        by = "AppiumBy.ID" if r["by"] == "ID" else "AppiumBy.XPATH"
        sel = r["selector"].replace('"', '\\"')
        note = "/".join(r["pages"][:2])
        if r["text"]:
            note += f" | {r['text']}"
        lines.append(f'    "{r["key"]}": ({by}, "{sel}"),  # {note}')
    return "\n".join(lines) + "\n"


def main():
    dry = "--dry-run" in sys.argv
    src, keys, sels = load_existing()
    records = json.load(open(GEN_JSON, encoding="utf-8"))

    if MARKER in src:
        print("[abort] locators.py 里已经有自动抓取段，请先手动删除再合并，避免重复追加")
        return 1

    new, skipped = [], 0
    dropped = 0
    for r in records:
        if r["selector"] in sels or r["key"] in keys:
            skipped += 1
            continue
        # 纯布局容器（无文案、不可点击、非输入/图片类）不并进主表：
        # 它们的位置关系随时会变，留着只会干扰；完整清单仍在 generated_locators.py
        if (not r.get("clickable") and not r["text"]
                and r["class"] not in KEEP_CLASSES):
            dropped += 1
            continue
        new.append(r)

    print(f"[plan] 生成 {len(records)} 条，已存在/重名跳过 {skipped} 条，"
          f"过滤布局容器 {dropped} 条，将追加 {len(new)} 条")
    if dry or not new:
        return 0

    # 插到 LOCATORS 的收尾大括号之前
    idx = src.rstrip().rfind("}")
    merged = src[:idx] + render(new).lstrip("\n") + src[idx:]
    if not merged.endswith("\n"):
        merged += "\n"
    open(LOCATORS_PY, "w", encoding="utf-8").write(merged)

    # 校验
    import importlib
    sys.path.insert(0, ROOT)
    import locators
    importlib.reload(locators)
    total = len(locators.LOCATORS)
    print(f"[ok] locators.py 现有 {total} 条定位（原 {total - len(new)} + 新增 {len(new)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
