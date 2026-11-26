# -*- coding: utf-8 -*-
"""
从 ui_dump 的控件树生成定位字典
================================
读取 logs/ui_dump/*.xml（tools/ui_tree_dump.py 的产物），把每个可定位节点
（app 包内的 resource-id 节点 + 有唯一文案的文本节点）转成 locators.py 风格的
(AppiumBy, selector) 条目，并按页面分组输出。

用法：
    python tools/gen_locators.py            # 生成 logs/ui_dump/generated_locators.py
    python tools/gen_locators.py --report    # 只打印统计

去重规则：
  - 同一个 selector 只保留一条，记录它出现过的所有页面
  - 已经在 locators.py 里存在的 selector 默认跳过（--include-existing 可保留）
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP_DIR = os.path.join(ROOT, "logs", "ui_dump")
OUT_PY = os.path.join(DUMP_DIR, "generated_locators.py")

APP_PACKAGE = "com.fhit.app_iprinter"
PREFIX = f"{APP_PACKAGE}:id/"

# 系统/框架级容器，做定位没有意义
SKIP_IDS = {
    "content", "action_bar_root", "statusBarBackground", "navigationBarBackground",
    "decor_content_parent", "action_bar", "action_bar_container", "action_bar_title",
    "action_bar_subtitle", "up", "home", "screen_simple", "screen", "fragment_container",
}

GROUPS = [
    # (分组名, 关键字匹配——命中文件名即归入该组)
    ("首页", ("首页",)),
    ("我的", ("我的",)),
    ("新建标签/耗材选择", ("新建标签",)),
    ("编辑页与功能栏", ("编辑页", "功能栏", "功能_")),
    ("查找设备", ("查找设备",)),
    ("其他页面", ()),
]


# --------------------------------------------------------------------------
def camel_to_snake(name: str) -> str:
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name)
    s = re.sub(r"(?<=[A-Z])([A-Z][a-z])", r"_\1", s)
    s = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fa5]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_").lower()


def load_existing_selectors():
    """把 locators.py 里已有的 selector 读出来（只做文本比对，不 import，避免依赖）。"""
    path = os.path.join(ROOT, "locators.py")
    if not os.path.exists(path):
        return set(), set()
    src = open(path, encoding="utf-8").read()
    selectors = set()
    keys = set()
    for m in re.finditer(r'"([^"]+)"\s*:\s*\(\s*(AppiumBy\.\w+|"[^"]+")\s*,\s*(.+?)\)\s*,?\s*(?:#.*)?$',
                         src, re.M):
        keys.add(m.group(1))
        raw = m.group(3).strip()
        # 取第一种写法里的字符串字面量
        lit = re.match(r"""^[fFrRbB]?['"](.+)['"]$""", raw)
        if lit:
            selectors.add(lit.group(1))
        else:
            selectors.add(raw)
    return keys, selectors


def page_tag(filename):
    return re.sub(r"^\d+_", "", os.path.splitext(os.path.basename(filename))[0])


def group_of(tag):
    for name, kws in GROUPS:
        if any(k in tag for k in kws):
            return name
    return "其他页面"


def is_noise_text(text: str) -> bool:
    """过滤画布内容/数据类文案，它们不是可复用的控件文案。"""
    if not text:
        return True
    if len(text) > 16:
        return True
    if text.endswith(":") or text.endswith("："):
        return True
    if re.fullmatch(r"[\d\s.,:\-/元%]+", text):
        return True
    return False


def collect(include_existing=False):
    """收集定位点。

    分两步：
      1. 先按节点抓「id -> 出现过的文案集合」和「无 id 的文案」；
      2. 再决定定位写法：同一个 id 只有一种文案时用纯 id（更稳），
         出现多种文案（宫格/列表）时才用 id+text 精确区分。
    """
    files = sorted(f for f in os.listdir(DUMP_DIR) if f.endswith(".xml"))
    existing_keys, existing_selectors = load_existing_selectors()

    by_id = {}       # short_id -> {texts:set, class, pages:set, clickable, desc}
    by_text = {}     # (class,text) -> {pages:set, clickable}

    for fn in files:
        path = os.path.join(DUMP_DIR, fn)
        tag = page_tag(fn)
        if tag.startswith("_"):
            continue
        try:
            tree = ET.parse(path)
        except Exception as e:
            print(f"[skip] {fn} 解析失败：{e}")
            continue
        for node in tree.iter():
            rid = node.get("resource-id") or ""
            text = (node.get("text") or "").strip()
            desc = (node.get("content-desc") or "").strip()
            cls = node.get("class") or ""
            clickable = node.get("clickable") == "true"

            if rid.startswith(PREFIX):
                short = rid[len(PREFIX):]
                if short in SKIP_IDS:
                    continue
                rec = by_id.setdefault(short, {
                    "id": short, "class": cls, "texts": set(), "pages": set(),
                    "clickable": False, "desc": desc,
                })
                if text and not is_noise_text(text):
                    rec["texts"].add(text)
                rec["pages"].add(tag)
                rec["clickable"] = rec["clickable"] or clickable
            elif text and not rid and cls.startswith("android.widget.") and not is_noise_text(text):
                rec = by_text.setdefault((cls, text), {"pages": set(), "clickable": clickable})
                rec["pages"].add(tag)

    items = {}       # selector -> record
    for short, rec in by_id.items():
        rid = PREFIX + short
        texts = sorted(rec["texts"])
        if len(texts) > 1:
            for t in texts:
                selector = f'//{rec["class"]}[@resource-id="{rid}" and @text="{t}"]'
                items[selector] = {
                    "selector": selector, "by": "XPATH", "id": short, "text": t,
                    "class": rec["class"], "pages": sorted(rec["pages"]),
                    "desc": rec["desc"], "clickable": rec["clickable"],
                }
        else:
            items[rid] = {
                "selector": rid, "by": "ID", "id": short,
                "text": texts[0] if texts else "",
                "class": rec["class"], "pages": sorted(rec["pages"]),
                "desc": rec["desc"], "clickable": rec["clickable"],
            }

    for (cls, text), rec in by_text.items():
        selector = f'//{cls}[@text="{text}"]'
        items.setdefault(selector, {
            "selector": selector, "by": "XPATH", "id": "", "text": text,
            "class": cls, "pages": sorted(rec["pages"]), "desc": "",
            "clickable": rec["clickable"],
        })

    # 生成 key
    used = set(existing_keys)
    out = []
    for rec in items.values():
        if not include_existing and rec["selector"] in existing_selectors:
            rec["existing"] = True
        base = camel_to_snake(rec["id"]) if rec["id"] else f"text_{camel_to_snake(rec['text'])}"
        # 只有「同一 id 多文案」的条目才需要拼文案后缀区分
        if rec["id"] and rec["by"] == "XPATH" and rec["text"]:
            base = f"{base}_{camel_to_snake(rec['text'])}"
        if not base:
            base = "node"
        key = base
        n = 2
        while key in used:
            key = f"{base}_{n}"
            n += 1
        used.add(key)
        rec["key"] = key
        rec["group"] = group_of(rec["pages"][0]) if rec["pages"] else "其他页面"
        out.append(rec)
    return out, existing_selectors


def write_py(records, include_existing=False):
    new = [r for r in records if not r.get("existing")]
    groups = {}
    for r in new:
        groups.setdefault(r["group"], []).append(r)

    lines = [
        "# -*- coding: utf-8 -*-",
        '"""',
        "自动生成的定位候选（来源：logs/ui_dump/*.xml 真实控件树）",
        "合并方式：把需要的条目拷进 locators.py 的 LOCATORS 即可。",
        f"共 {len(new)} 条，页面组：{'、'.join(f'{k}({len(v)})' for k, v in groups.items())}",
        '"""',
        "from appium.webdriver.common.appiumby import AppiumBy",
        "",
        "GENERATED_LOCATORS = {",
    ]
    for group, recs in groups.items():
        lines.append(f"    # ================= {group} =================")
        for r in recs:
            by = "AppiumBy.ID" if r["by"] == "ID" else "AppiumBy.XPATH"
            sel = r["selector"].replace('"', '\\"')
            note = f"# {'/'.join(r['pages'][:2])}"
            if r["text"]:
                note += f" | {r['text']}"
            lines.append(f'    "{r["key"]}": ({by}, "{sel}"),  {note}')
        lines.append("")
    lines.append("}")
    open(OUT_PY, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(new, open(os.path.join(DUMP_DIR, "generated_locators.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[ok] 写出 {OUT_PY}（{len(new)} 条新增候选）")


def main():
    include_existing = "--include-existing" in sys.argv
    records, existing = collect(include_existing)
    new = [r for r in records if not r.get("existing")]
    print(f"[统计] 控件树去重后 {len(records)} 个定位点，其中已在 locators.py 里 {len(records)-len(new)} 个，新增候选 {len(new)} 个")
    by_group = {}
    for r in new:
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
    for g, c in by_group.items():
        print(f"  - {g}: {c}")
    if "--report" not in sys.argv:
        write_py(records, include_existing)


if __name__ == "__main__":
    main()
