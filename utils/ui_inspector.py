# -*- coding: utf-8 -*-
"""元素拾取核心逻辑（无 UI 依赖）
================================
把「当前手机屏幕」变成可查询的数据：控件树 + 截图，并支持按坐标反查控件、
生成多种定位候选、校验定位在当前屏是否唯一、产出可直接粘贴进 locators.py 的代码。

设计边界：
    - 只管「当前这一屏」。要跨页面找元素，用户自己滑手机再刷新，工具不猜导航路径。
    - 不写 locators.py，只生成文本；要不要落盘由人决定。
    - 定位唯一性只在**当前屏**校验 —— 这是能离线确定的最大范围。

UI 侧（run_gui.py 的拾取窗口）与命令行都调这里。
"""

import os
import re
import struct
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCATORS_PATH = os.path.join(PROJECT_ROOT, "locators.py")

APP_PACKAGE = os.getenv("APP_PACKAGE", "com.fhit.app_iprinter")
APP_ACTIVITY = os.getenv("APP_ACTIVITY", ".ui.home.activity.HomeActivity")
PREFIX = f"{APP_PACKAGE}:id/"

_BOUNDS_RE = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")
_EXIST_KEY_RE = re.compile(r'^\s*"([^"#]+?)"\s*:\s*\(', re.M)
# "key": (AppiumBy.ID, "com.xxx:id/yyy")  →  取出 key + by + selector
_ENTRY_RE = re.compile(
    r'"([^"\n]+)"\s*:\s*\(\s*(?:AppiumBy\.(\w+)|"([^"]*)")\s*,\s*"([^"\n]*)"\s*\)'
)


# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------
def png_size(data):
    """从 PNG 头部取尺寸，避免为了一张图引入 Pillow。"""
    if not data or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", data[16:24])
    return w, h


def xpath_literal(value):
    """把任意字符串安全地塞进 xpath 字面量。

    优先双引号：和 locators.py 里现有 XPath 的书写风格一致，读起来不别扭。
    """
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f'"{p}"' for p in parts) + ")"


def camel_to_snake(name):
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name)
    s = re.sub(r"(?<=[A-Z])([A-Z][a-z])", r"_\1", s)
    s = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fa5]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_").lower()


def load_existing_keys():
    """读 locators.py 里已占用的 key，用于新条目命名时避让。

    纯文本正则，不 import locators.py（避免副作用，也避免它语法坏掉时拖垮工具）。
    """
    try:
        src = open(LOCATORS_PATH, encoding="utf-8").read()
    except OSError:
        return set()
    return {m.strip() for m in _EXIST_KEY_RE.findall(src) if m.strip()}


def load_existing_entries():
    """selector → (key, by)，用来判断「这个元素我是不是已经收录过了」。

    同时按 selector 和「去掉包名的短 id」两个维度索引，方便拿 rid 直接比对。
    """
    try:
        src = open(LOCATORS_PATH, encoding="utf-8").read()
    except OSError:
        return {}
    out = {}
    for key, by_attr, by_str, selector in _ENTRY_RE.findall(src):
        by = by_attr or by_str
        out.setdefault(selector, (key, by))
        if ":" in selector and "/" in selector:
            out.setdefault(selector.rsplit("/", 1)[-1], (key, by))
    return out


# --------------------------------------------------------------------------
# 控件树
# --------------------------------------------------------------------------
class Node:
    """一个控件节点。bounds 为屏幕像素矩形 (x1, y1, x2, y2)。"""

    __slots__ = (
        "cls", "rid", "text", "desc", "bounds", "clickable", "enabled",
        "checked", "selected", "scrollable", "long_clickable", "password",
        "package", "index", "parent", "children", "depth",
    )

    def __init__(self):
        self.cls = ""
        self.rid = ""
        self.text = ""
        self.desc = ""
        self.bounds = (0, 0, 0, 0)
        self.clickable = False
        self.enabled = True
        self.checked = False
        self.selected = False
        self.scrollable = False
        self.long_clickable = False
        self.password = False
        self.package = ""
        self.index = 0
        self.parent = None
        self.children = []
        self.depth = 0

    # ------- 派生属性 -------
    @property
    def area(self):
        x1, y1, x2, y2 = self.bounds
        return max(0, x2 - x1) * max(0, y2 - y1)

    @property
    def wid(self):
        return self.bounds[2] - self.bounds[0]

    @property
    def hei(self):
        return self.bounds[3] - self.bounds[1]

    @property
    def short_id(self):
        """resource-id 去掉包名前缀，locators.py 里习惯写全名，这里给短名做 key。"""
        return self.rid[len(PREFIX):] if self.rid.startswith(PREFIX) else self.rid

    @property
    def short_cls(self):
        return self.cls.rsplit(".", 1)[-1] if self.cls else ""

    @property
    def label(self):
        """给列表显示用的一句话描述。"""
        bits = [self.short_cls or "?"]
        if self.short_id:
            bits.append(self.short_id)
        if self.text:
            bits.append(f"“{self.text}”")
        if self.desc and self.desc != self.text:
            bits.append(f"[{self.desc}]")
        return "  ".join(bits)

    @property
    def comment(self):
        """locators.py 行尾注释用的中文说明：优先文案，其次 desc，最后类名。"""
        t = self.text or self.desc
        if t:
            return t.replace("\n", " ")[:24]
        return self.short_cls

    def contains(self, x, y):
        x1, y1, x2, y2 = self.bounds
        return x1 <= x < x2 and y1 <= y < y2

    def ancestors(self):
        out, cur = [], self.parent
        while cur is not None:
            out.append(cur)
            cur = cur.parent
        return out

    def path(self):
        """从根到本节点的祖先链（含自身，根在前）。"""
        return list(reversed(self.ancestors())) + [self]

    def __repr__(self):
        return f"<Node {self.label} {self.bounds}>"


def _num(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _bool(v):
    return str(v).lower() == "true"


def parse(source):
    """把 page_source(XML) 解析成 Node 树。解析失败返回 None。"""
    if not source or not source.strip():
        return None
    try:
        root_el = ET.fromstring(source)
    except ET.ParseError:
        return None

    def build(el, parent, depth):
        n = Node()
        a = el.attrib
        n.cls = a.get("class", "")
        n.rid = a.get("resource-id", "") or ""
        n.text = (a.get("text", "") or "").strip()
        n.desc = (a.get("content-desc", "") or "").strip()
        m = _BOUNDS_RE.match(a.get("bounds", ""))
        n.bounds = tuple(int(g) for g in m.groups()) if m else (0, 0, 0, 0)
        n.clickable = _bool(a.get("clickable"))
        n.enabled = _bool(a.get("enabled", "true"))
        n.checked = _bool(a.get("checked"))
        n.selected = _bool(a.get("selected"))
        n.scrollable = _bool(a.get("scrollable"))
        n.long_clickable = _bool(a.get("long-clickable"))
        n.password = _bool(a.get("password"))
        n.package = a.get("package", "")
        n.index = _num(a.get("index"))
        n.parent = parent
        n.depth = depth
        for child in el:
            n.children.append(build(child, n, depth + 1))
        return n

    return build(root_el, None, 0)


def iter_nodes(node):
    """深度优先遍历（含自身）。"""
    stack = [node]
    while stack:
        cur = stack.pop()
        yield cur
        stack.extend(reversed(cur.children))


def node_at(root, x, y, prefer_clickable=True):
    """按屏幕坐标找控件：命中该点的节点里，取「最小」的那个。

    两道过滤：
      1. 丢掉 hierarchy 这种根壳子 —— 它是整棵树的外包装，不是界面元素。
      2. prefer_clickable 时只在可点击节点里挑：找定位多半是为了点它，
         给用户按钮容器比给里面 12px 的图标有用。
    最后再优先「有 id/文案/描述」的节点，避免点在空白处拿回一个全屏容器。
    """
    pool = [
        n for n in iter_nodes(root)
        if n.area > 0 and n.contains(x, y) and n.cls != "hierarchy"
    ]
    if prefer_clickable:
        clickable = [n for n in pool if n.clickable]
        if clickable:
            pool = clickable
    if not pool:
        return None
    semantic = [n for n in pool if n.rid or n.text or n.desc]
    if semantic:
        pool = semantic
    # 面积最小优先；同面积取层级更深（更具体）的
    pool.sort(key=lambda n: (n.area, -n.depth))
    return pool[0]


def nearest_clickable(node):
    """自身可点击就返回自身，否则往上找最近的可点击祖先。"""
    cur = node
    while cur is not None:
        if cur.clickable:
            return cur
        cur = cur.parent
    return None


def same_class_index(node):
    """同父级下、同 class 的第几个（1 起），用于 class + index 兜底定位。"""
    if node.parent is None:
        return 1
    n = 0
    for sib in node.parent.children:
        if sib.cls == node.cls:
            n += 1
        if sib is node:
            return n
    return n or 1


def count_matching(root, pred):
    return sum(1 for n in iter_nodes(root) if pred(n))


def absolute_xpath(node):
    """完整绝对路径：能精确定位，但页面结构一变就失效。"""
    parts = []
    for n in node.path():
        if not n.cls:
            continue                      # hierarchy 这类没 class 的根节点，跳过
        if not parts:
            parts.append(f"//{n.cls}")
        else:
            parts.append(f"{n.cls}[{same_class_index(n)}]")
    return "/".join(parts) if parts else "//*"


# --------------------------------------------------------------------------
# 定位候选
# --------------------------------------------------------------------------
class Candidate:
    """一条定位方案 + 它的唯一性结论 + 可直接粘贴的代码。"""

    __slots__ = ("kind", "by", "locator", "count", "note", "level", "key", "comment")

    def __init__(self, kind, by, locator, count, note, level="ok", key="", comment=""):
        self.kind = kind          # 人类可读的策略名
        self.by = by              # "ID" / "XPATH"
        self.locator = locator
        self.count = count        # 当前屏命中数量
        self.note = note          # 结论/建议
        self.level = level        # ok / warn / bad，供 UI 着色
        self.key = key            # 建议的 locators key
        self.comment = comment    # 行尾注释

    @property
    def by_expr(self):
        # 坐标/多候选是项目自定义的伪定位常量，不是 AppiumBy 的成员
        if self.by in ("COORDINATE", "MULTI"):
            return self.by
        return f"AppiumBy.{self.by}"

    @property
    def entry_code(self):
        """可直接粘贴进 LOCATORS 的条目（注释右对齐，和文件里现有风格一致）。"""
        key = self.key or "<起个名>"
        if self.by == "COORDINATE":
            head = f'    "{key}": (COORDINATE, {self.locator}),'
            return f"{head:<86} # {self.comment}" if self.comment else head
        head = f'    "{key}": ({self.by_expr}, {xpath_literal(self.locator)}),'
        return f"{head:<86} # {self.comment}" if self.comment else head

    def call_code(self):
        """在用例里怎么用（走项目自己的 locators.py 约定）。"""
        if self.by == "COORDINATE":
            return f'tap_ratio(driver, *LOCATORS["{self.key}"])'
        return f'wait_for_element(driver, *LOCATORS["{self.key}"]).click()'

    def __repr__(self):
        return f"<Candidate {self.kind} count={self.count}>"


def _unique_note(count):
    if count == 1:
        return "当前屏唯一", "ok"
    if count == 0:
        return "当前屏未命中（可能是隐藏节点）", "bad"
    return f"当前屏命中 {count} 个，需收窄条件", "warn"


def key_for_node(node, existing_keys=None, used=None):
    """给一个控件起 locators.py 条目名，避开已占用的 key。

    key 是「元素级」的，不是「策略级」的：同一元素的 id 写法、xpath 写法
    应该共用一个语义名字，否则粘进 locators.py 会出现三个别名指向同一个控件。
    """
    existing = set(existing_keys or ())
    taken = set(used or ())
    # 只取 id 最后一段：系统控件形如 com.android.systemui:id/row0，
    # 整串转下划线会变成一坨没法读的名字
    raw = node.rid.rsplit("/", 1)[-1] if node.rid else ""
    base = camel_to_snake(raw) if raw else ""
    if not base:
        base = camel_to_snake(node.comment) or "node"
    if not base[0].isalpha():
        base = "n_" + base
    if len(base) > 60:
        base = base[:60].rstrip("_")
    key, i = base, 2
    while key in existing or key in taken:
        key = f"{base}_{i}"
        i += 1
    return key


def build_candidates(root, node, existing_keys=None, window=None):
    """给一个节点生成按推荐度排序的定位候选列表。

    排序原则：resource-id 唯一 > id+文案 > 祖先 id + 文案/desc > 祖先 id + 类名
    > 纯文案 > class 序号 > 坐标。前者跨版本最稳，后者只是「好歹能点」的兜底。

    window=(w, h) 传了就额外给一条坐标比例兜底 —— 项目里 COORDINATE/tap_ratio
    就是为「实在没有可定位属性」准备的那一档。
    """
    existing = set(existing_keys or ())          # 仅用于签名兼容，key 不在这里生成
    out = []
    comment = node.comment
    is_input = "EditText" in node.cls or node.password

    def add(kind, by, locator, count, level_override=None, note_override=""):
        note, level = _unique_note(count)
        if level_override:
            level = level_override
        if note_override:
            note = note_override
        # key 先留空：由 UI 在用户选中时统一起一个（见 key_for_node）
        out.append(Candidate(kind, by, locator, count, note, level, "", comment))

    # 1) resource-id 本身
    if node.rid:
        pred = lambda n, r=node.rid: n.rid == r
        cnt = count_matching(root, pred)
        if cnt == 1:
            add("resource-id", "ID", node.rid, cnt)
        else:
            # 同 id 多实例（列表/宫格），有文案就拼文案收窄
            if node.text:
                xp = f'//{node.cls}[@resource-id={xpath_literal(node.rid)} and @text={xpath_literal(node.text)}]'
                c2 = count_matching(
                    root,
                    lambda n, r=node.rid, t=node.text: n.rid == r and n.text == t,
                )
                if c2 == 1:
                    add("resource-id + 文案", "XPATH", xp, c2,
                        note_override="同 id 有多个，用文案收窄后唯一")
                else:
                    add("resource-id + 文案", "XPATH", xp, c2)
            # 纯 id 仍然列出来，标明会命中多个
            add("resource-id（会命中多个）", "ID", node.rid, cnt)

    # 2) 祖先 id + 后代条件：结构里唯一、又不受绝对层级影响
    fallback_anc = None
    for anc in node.ancestors():
        if not anc.rid:
            continue
        if count_matching(root, lambda n, r=anc.rid: n.rid == r) != 1:
            continue
        if fallback_anc is None:
            fallback_anc = anc              # 记下最近的可用祖先，下面兜底用
        handled = False
        if node.text:
            inner = count_matching(anc, lambda n, t=node.text: n.text == t)
            if inner == 1:
                add(f"祖先 {anc.short_id} + 文案", "XPATH",
                    f'//*[@resource-id={xpath_literal(anc.rid)}]//{node.cls}'
                    f"[@text={xpath_literal(node.text)}]",
                    inner, level_override="ok",
                    note_override="祖先唯一的相对路径，抗层级变动")
                handled = True
        if not handled and node.desc and node.desc != node.text:
            inner = count_matching(anc, lambda n, d=node.desc: n.desc == d)
            if inner == 1:
                add(f"祖先 {anc.short_id} + content-desc", "XPATH",
                    f'//*[@resource-id={xpath_literal(anc.rid)}]//{node.cls}'
                    f"[@content-desc={xpath_literal(node.desc)}]",
                    inner, level_override="ok",
                    note_override="祖先唯一的相对路径，抗层级变动")
                handled = True
        if handled:
            break

    # 2b) 既没文案也没描述？用「唯一祖先 + 类名」，比绝对路径短且稳得多
    if not out and fallback_anc is not None and node.cls:
        inner = count_matching(fallback_anc, lambda n: n.cls == node.cls)
        xp = f'//*[@resource-id={xpath_literal(fallback_anc.rid)}]//{node.cls}'
        if inner == 1:
            add(f"祖先 {fallback_anc.short_id} + 类名", "XPATH", xp, inner,
                level_override="ok", note_override="祖先内该类名唯一，比绝对路径稳")
        elif inner <= 5:
            add(f"祖先 {fallback_anc.short_id} + 类名", "XPATH", xp, inner)

    # 3) 纯文案 / content-desc
    if node.text:
        for cls_part in (node.cls, "*"):
            xp = f'//{cls_part}[@text={xpath_literal(node.text)}]'
            if cls_part == node.cls:
                cnt = count_matching(root, lambda n, t=node.text: n.text == t and n.cls == node.cls)
            else:
                cnt = count_matching(root, lambda n, t=node.text: n.text == t)
            if cnt == 1:
                if is_input:
                    add("文本（输入框当前值）", "XPATH", xp, cnt,
                        level_override="bad",
                        note_override="这是输入框里已有的值，会随内容变，别用它定位")
                else:
                    add("文本", "XPATH", xp, cnt,
                        level_override="warn",
                        note_override="按文案定位，界面上这句话改了就失效")
                break
        else:
            add("文本（会命中多个）", "XPATH",
                f'//*[@text={xpath_literal(node.text)}]',
                count_matching(root, lambda n, t=node.text: n.text == t),
                level_override="warn", note_override="多个控件同文案，改动风险高")

    if node.desc and node.desc != node.text:
        cnt = count_matching(root, lambda n, d=node.desc: n.desc == d)
        add("content-desc", "XPATH",
            f'//*[@content-desc={xpath_literal(node.desc)}]', cnt)

    # 4) class 绝对路径：连祖先都不可靠时的最后手段
    if not out and node.cls:
        add("class 绝对路径（兜底）", "XPATH", absolute_xpath(node), 1,
            level_override="bad", note_override="依赖绝对层级，页面一改就失效")

    # 5) 坐标比例：项目里 COORDINATE + tap_ratio 就是为这种场景准备的。
    #    已经有可靠定位时不出现，免得列表里塞一堆用不上的兜底项。
    if window and window[0] and window[1] and not any(c.level == "ok" for c in out):
        b = node.bounds
        xr = ((b[0] + b[2]) / 2.0) / window[0]
        yr = ((b[1] + b[3]) / 2.0) / window[1]
        out.append(Candidate(
            "坐标比例（兜底）", "COORDINATE", f"({xr:.3f}, {yr:.3f})", 1,
            "只能盲点，布局一变就偏；配 tap_ratio 用", "bad", "", comment,
        ))

    return out


# --------------------------------------------------------------------------
# 设备侧
# --------------------------------------------------------------------------
class Snapshot:
    """某一时刻的手机屏幕快照：截图 + 控件树。"""

    __slots__ = ("png", "img_w", "img_h", "win_w", "win_h", "root", "source",
                 "activity", "taken_at", "is_app")

    def __init__(self, png, root, source, window, activity, taken_at):
        self.png = png
        self.root = root
        self.source = source
        size = png_size(png) or (window[0], window[1])
        self.img_w, self.img_h = size
        self.win_w, self.win_h = window
        self.activity = activity
        self.taken_at = taken_at
        # 控件树里有没有被测 App 的控件 —— 没有就是抓到了系统界面/启动画面
        self.is_app = PREFIX in (source or "")

    def to_screen(self, img_x, img_y):
        """截图坐标 → 屏幕坐标（截图可能被系统缩放过，不能假设 1:1）。"""
        sx = self.win_w / self.img_w if self.img_w else 1.0
        sy = self.win_h / self.img_h if self.img_h else 1.0
        return int(img_x * sx), int(img_y * sy)

    def hit(self, img_x, img_y, prefer_clickable=True):
        if self.root is None:
            return None
        x, y = self.to_screen(img_x, img_y)
        return node_at(self.root, x, y, prefer_clickable=prefer_clickable)


class Inspector:
    """一条常驻的 Appium session，反复刷新当前屏。

    拾取是个「看一眼 → 点一下 → 再滑一下 → 再看」的高频操作，
    每次重建 session 要几十秒，所以这里保持连接，由调用方负责 close()。
    """

    def __init__(self, udid=None, port=4723, host="127.0.0.1", log=print):
        self.udid = udid or os.getenv("ANDROID_UDID", "")
        self.url = os.getenv("APPIUM_SERVER_URL", f"http://{host}:{port}")
        self.log = log
        self.driver = None

    @property
    def connected(self):
        return self.driver is not None

    def connect(self):
        from appium import webdriver
        from appium.options.android import UiAutomator2Options

        opts = UiAutomator2Options()
        opts.platform_name = "Android"
        opts.device_name = self.udid or "Android"
        if self.udid:
            opts.udid = self.udid
        opts.app_package = APP_PACKAGE
        opts.app_activity = APP_ACTIVITY
        opts.auto_grant_permissions = True
        opts.no_reset = True                  # 保留登录态，别每次从隐私协议开始
        opts.new_command_timeout = 3600       # 人要慢慢点，别中途超时
        opts.skip_device_initialization = True
        opts.set_capability("uiautomator2ServerLaunchTimeout", 180000)
        opts.set_capability("uiautomator2ServerInstallTimeout", 120000)
        # 通知监听强依赖 UiAutomation，设备侧偶发未连接时直接拖垮建 session
        opts.set_capability("enableNotificationListener", False)
        opts.set_capability("disableWindowAnimation", True)

        self.log(f"正在连接设备 {self.udid or '(默认)'} …")
        self.driver = webdriver.Remote(self.url, options=opts)
        # noReset 下 Appium 不保证把 App 拉到前台
        try:
            self.driver.activate_app(APP_PACKAGE)
        except Exception:
            pass
        self.wait_ready()
        self.log("设备已连接")
        return self.driver

    def close(self):
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def activity(self):
        try:
            return self.driver.current_activity or ""
        except Exception:
            return ""

    def wait_ready(self, timeout=20.0):
        """等被测 App 真正画出界面再抓。

        activate_app 之后 App 还在冷启动，这时候抓会拿到黑屏 + 系统 loading 圈，
        控件树里全是 com.android.systemui 的东西 —— 对找定位毫无意义。
        """
        import time

        end = time.time() + timeout
        while time.time() < end:
            try:
                src = self.driver.page_source
            except Exception:
                time.sleep(0.5)
                continue
            if PREFIX in src and len(src) > 2000:
                return True
            time.sleep(0.5)
        self.log("页面似乎还没渲染完，先抓当前状态（可点刷新重试）")
        return False

    def capture(self):
        """抓一帧：先截图再取控件树（截图快，树慢，让树尽量贴近当前态）。"""
        import time

        if self.driver is None:
            raise RuntimeError("尚未连接设备")
        win = self.driver.get_window_size()
        window = (win.get("width", 0), win.get("height", 0))
        png = self.driver.get_screenshot_as_png()
        source = self.driver.page_source
        return Snapshot(png, parse(source), source, window, self.activity(), time.time())

    # ---------------- 设备操作（让用户在窗口里就能翻页） ----------------
    def swipe_up(self, ratio=0.72):
        """内容上翻（手指从下往上滑）。"""
        self._swipe(ratio, ratio - 0.42)

    def swipe_down(self, ratio=0.32):
        self._swipe(ratio, ratio + 0.42)

    def _swipe(self, y1_ratio, y2_ratio):
        if self.driver is None:
            return
        w = self.driver.get_window_size()["width"]
        h = self.driver.get_window_size()["height"]
        self.driver.swipe(w // 2, int(h * y1_ratio), w // 2, int(h * y2_ratio), 300)

    def press_back(self):
        if self.driver is not None:
            try:
                self.driver.back()
            except Exception:
                pass

    def activate(self):
        """把被测 App 拉回前台（按返回键退出去之后用它回来）。"""
        if self.driver is None:
            return
        try:
            self.driver.activate_app(APP_PACKAGE)
        except Exception:
            pass


# --------------------------------------------------------------------------
# 报错归因
# --------------------------------------------------------------------------
_ERROR_HINTS = (
    (
        ("uiautomation not connected", "uiautomation is not connected"),
        "手机侧的 UiAutomation 连接断了，Appium 建会话失败。\n\n"
        "按顺序试：\n"
        "1. 拔插一次数据线，重新点「连接设备」\n"
        "2. 还不行就重启手机再连（最有效，不会丢数据）\n\n"
        "这是 Appium 在部分机型上的老毛病，不是脚本问题。",
    ),
    (
        ("could not find a connected android device", "no devices/emulators found",
         "device offline", "device not found", "not found in adb"),
        "adb 没看到可用的手机。\n\n"
        "检查：数据线是否松动、手机上 USB 调试是否还开着、"
        "有没有弹出「允许 USB 调试」的授权框。",
    ),
    (
        ("unauthorized",),
        "手机还没授权这台电脑调试。\n\n"
        "拔插数据线后，在手机弹出的「允许 USB 调试吗」里点允许"
        "（勾上「一律允许」更省事）。",
    ),
    (
        ("econnrefused", "connection refused", "socket hang up", "connect timeout"),
        "连不上 Appium 服务。\n\n"
        "回到主窗口点「重新检测」拉起 Appium，或看一眼 logs/appium_server.log。",
    ),
    (
        ("a new session could not be created", "session is already started",
         "requested resource could not be found"),
        "设备上还有上一个没退干净的 Appium 会话。\n\n"
        "等十几秒再连一次；仍失败就在主窗口点「重新检测」，"
        "或重启一次 Appium 服务。",
    ),
    (
        ("instrumentation process cannot be initialized",
         "uiautomator2 server", "cannot be initialized"),
        "uiautomator2 服务在手机上起不来。\n\n"
        "通常是手机上的服务包损坏：拔插数据线重连，"
        "或在手机「设置 → 应用」里卸载 Appium Settings / io.appium.uiautomator2.server 再连。",
    ),
    (
        ("does not exist", "not installed", "unable to find"),
        "手机上找不到被测 App（包名 com.fhit.app_iprinter）。\n\n"
        "确认 App 已安装；如果包名变了，改 utils/ui_inspector.py 里的 APP_PACKAGE。",
    ),
    (
        ("timed out", "timeout"),
        "操作超时了。\n\n"
        "首次连接要装 / 启动服务包，偶尔会慢；等一会儿重试一次。"
        "反复超时的话重启手机最稳。",
    ),
)


def _clip(text, limit=700):
    """取报错里信息量最大的一段：优先 Original error 之后的内容。"""
    low = text.lower()
    idx = low.rfind("original error")
    if idx != -1:
        text = text[idx + len("original error"):].lstrip(" :：")
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " …"


def friendly_error(raw):
    """把 Appium / adb 的原始报错翻成能照着做的中文提示。"""
    text = str(raw or "").strip()
    if not text:
        return "连接失败，但没有拿到具体原因。\n\n完整信息见 logs/ui_picker_error.log。"
    low = text.lower()
    for markers, tip in _ERROR_HINTS:
        if any(m in low for m in markers):
            return f"{tip}\n\n原始信息：{_clip(text)}"
    return f"连接失败：\n\n{_clip(text, 900)}"
