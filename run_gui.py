#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SUPVAN 自动化测试 · 图形化启动器

一个「双击即用」的桌面小工具，把原本需要手敲的三件事串成一步：

    1. 唤起 Appium Server（自动探测 4723 端口，没起就拉起来，跑完不关）
    2. 勾选要执行的脚本 / 用例
    3. 运行前确认测试参数（打印机编号 / 手机号 / 耗材尺寸，直接改写用例源码）
    4. 浏览 / 体检元素定位库 locators.py（顶部「元素定位」按钮，纯静态分析）
    5. 拾取当前屏的元素定位（顶部「元素拾取」按钮，点截图直接出 id/xpath + 可粘贴代码）
    6. 拉起 .venv 里的 pytest 执行，并实时回显日志 + 生成 HTML 报告

用法：
    双击本文件，或执行  .venv/Scripts/python.exe run_gui.py

自测：
    .venv/Scripts/python.exe run_gui.py --list   # 只打印识别到的用例清单，不开窗口

设计约定（与项目其它模块保持一致）：
    - 用例识别规则完全对齐 pytest.ini：只认 testcases/ 下的 test_*.py，
      用 AST 静态解析函数名，不 import 用例文件（避免触发 driver 连接等副作用）。
    - 不重新实现任何等待 / 日志逻辑，只是外部驱动 pytest 进程。
    - 子进程强制 UTF-8 + 不缓冲：保证中文日志不乱码、且能实时滚动而非攒到最后。
"""

import argparse
import ast
import base64
import datetime as _dt
import json
import locator_manager
import math
import os
import pathlib
import platform
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import param_editor
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk
from utils import ui_inspector

# --------------------------------------------------------------------------
# 路径与环境常量
# --------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TESTCASE_DIR = os.path.join(PROJECT_ROOT, "testcases")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
# 失败现场：每次失败一个子目录（截图 + 控件树 + meta.json），
# 设备早就翻页了也能事后复盘当时那一屏
FAILURES_DIR = os.path.join(LOGS_DIR, "failures")
TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")
MAX_LOG_LINES = 6000      # 超过就丢最早的一批，防止长跑把内存吃满

# 参数历史：记下用过的打印机编号，供参数窗下拉选择。
# 放在 config/ 而不是源码里 —— 它是本机使用痕迹，跟「改哪个文件」无关。
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
PARAM_HISTORY = os.path.join(CONFIG_DIR, "param_history.json")
DEVICE_FIELDS = ("device_number1", "device_number2", "device_number3")
HISTORY_LIMIT = 30        # 下拉里最多留多少条，太多反而难找


def _venv_python():
    """虚拟环境解释器：Windows 在 Scripts，macOS/Linux 在 bin。"""
    base = os.path.join(PROJECT_ROOT, ".venv")
    candidates = (
        os.path.join(base, "bin", "python"),
        os.path.join(base, "Scripts", "python.exe"),
    )
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return candidates[0] if sys.platform == "darwin" else candidates[1]


VENV_PYTHON = _venv_python()

APPIUM_HOST = "127.0.0.1"
APPIUM_PORT = 4723
APPIUM_LOG = os.path.join(LOGS_DIR, "appium_server.log")

CHECKED = "\u2611"    # ☑
UNCHECKED = "\u2610"  # ☐

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
# 只有 Windows 有：让子进程自成进程组，「停止」时才能给它发 CTRL_BREAK
CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def mono_font(size=9):
    """等宽字体：macOS 用 Menlo，Windows 用 Consolas。

    Tk 不做字体族替换 —— 写一个系统里没有的名字就静默退回默认字体，
    日志里的中文注释于是变成不等宽、对不齐。两个平台的名字必须分开写。
    """
    return ("Menlo", size) if sys.platform == "darwin" else ("Consolas", size)


# --------------------------------------------------------------------------
# 视觉主题
#
# 原来直接用系统主题（Windows 上是 vista / macOS 上是 aqua），两个平台长相
# 完全不同，而且 LabelFrame 的标题、ttk 控件的内边距都没法调 —— 这是界面
# 显旧的根因。这里改成统一的 clam 主题 + 一套自绘样式：
#
#   · clam 是 Tk 自带的「纯 Tcl 绘制」主题，mac / win 下元素结构一致，
#     因此同一份 style 配置在两个平台上出来是同一个样子；
#   · 颜色、圆角、间距、字号全部收在上面的调色板和下面的 apply_theme()里，
#     以后想换色只动这两处。
# --------------------------------------------------------------------------

# —— 调色板（浅色，中性偏冷）——
C_BG = "#F4F5F7"            # 窗口底色
C_SURFACE = "#FFFFFF"       # 卡片 / 工具栏白底
C_SUNK = "#FAFBFC"          # 略微下沉的区域
C_BORDER = "#E5E7EB"        # 常规描边
C_BORDER2 = "#D3D7DE"       # 控件描边（比卡片略深，才分得清）
C_TEXT = "#1D2129"          # 主文字
C_TEXT2 = "#52596B"         # 次要文字
C_TEXT3 = "#8A92A6"         # 弱化文字 / 占位
C_PRIMARY = "#2B6BE4"
C_PRIMARY_H = "#1F57C7"
C_PRIMARY_D = "#19499F"
C_PRIMARY_SOFT = "#EDF3FF"
C_OK = "#12915A"
C_OK_SOFT = "#E7F6EE"
C_WARN = "#B07406"
C_WARN_SOFT = "#FDF3E2"
C_ERR = "#C93B3B"
C_ERR_SOFT = "#FDECEC"
C_ROW_HOVER = "#F2F6FD"
C_LOG_BG = "#171A20"        # 日志区深色底（比纯 #1e1e1e 更沉）
C_LOG_FG = "#C9CFDA"

# —— 字体 ——
# Tk 不做字体族替换：写一个系统里不存在的名字会静默退回默认字体，
# 所以按平台给首选，再用 font.families() 兜底探测一次。
_UI_FAMILY = None
MONO_FAMILIES = ("Menlo", "SF Mono", "Consolas", "DejaVu Sans Mono", "Courier New")


def ui_font(size=10, bold=False):
    fam = _UI_FAMILY or ("PingFang SC" if sys.platform == "darwin" else "Microsoft YaHei UI")
    return (fam, size, "bold") if bold else (fam, size)


def resolve_fonts(root):
    """在 Tk 起来之后挑一个本机真实存在的中文字体，避免回退成方框/默认字体。"""
    global _UI_FAMILY
    try:
        from tkinter import font as tkfont

        have = set(tkfont.families(root))
    except Exception:
        return
    for cand in (
        "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei",
        "Hiragino Sans GB", "Source Han Sans SC", "Noto Sans CJK SC",
        "Segoe UI", "Helvetica Neue", "Arial",
    ):
        if cand in have:
            _UI_FAMILY = cand
            return


# —— 列表区尺寸 ——
# 左侧不用 ttk.Treeview：它的展开三角由系统主题绘制、尺寸无法调整，
# 勾选框也只能跟树统一字号 —— 满足不了「单独加大」的需求。
# 改用 Canvas + 若干 Label 手工拼行，尺寸完全可控。
ROW_BG = C_SURFACE
ARROW_SIZE = 11          # 展开三角字号
CHECK_SIZE = 15          # 勾选框字号
ROW_H = 32               # 行高（固定，行内元素靠 pack 自动垂直居中）
ROW_PADY = 0             # 行内标签不再用 pady，避免与固定行高打架
INDENT_PX = 26           # 子项相对父项的缩进

# 行尾的结果标记（跑起来以后实时更新）
STATUS_STYLE = {
    "PASSED": ("\u2713", C_OK),         # ✓
    "FAILED": ("\u2717", C_ERR),        # ✗
    "ERROR": ("!", C_ERR),
    "SKIPPED": ("\u2013", C_TEXT3),     # –
    "RUNNING": ("\u25B6", C_PRIMARY),   # ▶
}


def _round_rect(canvas, x1, y1, x2, y2, r, **kw):
    """在 Canvas 上画一个圆角矩形（Tk 没有现成的，用平滑多边形逼近）。"""
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


def apply_theme(root):
    """把整套 ttk 样式装到 root 上。

    只配置 clam 主题，不碰系统主题 —— 这样 macOS 与 Windows 上出来的
    是同一套外观，调色板改一处两个平台同时生效。
    """
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # 全局默认：所有 ttk 控件的底子
    style.configure(
        ".", background=C_BG, foreground=C_TEXT, font=ui_font(10),
        bordercolor=C_BORDER2, focuscolor=C_PRIMARY,
        troughcolor=C_BG, fieldbackground=C_SURFACE,
        selectbackground=C_PRIMARY, selectforeground="#FFFFFF",
    )
    style.configure("TFrame", background=C_BG)
    style.configure("TLabel", background=C_BG, foreground=C_TEXT)
    style.configure("TSeparator", background=C_BORDER)

    # —— 白底容器（卡片 / 工具栏）上的控件副本 ——
    style.configure("Surface.TFrame", background=C_SURFACE)
    style.configure("Surface.TLabel", background=C_SURFACE, foreground=C_TEXT)
    style.configure("Muted.TLabel", background=C_BG, foreground=C_TEXT3)
    style.configure("SurfaceMuted.TLabel", background=C_SURFACE, foreground=C_TEXT3)
    style.configure(
        "Title.TLabel", background=C_SURFACE, foreground=C_TEXT, font=ui_font(13, True)
    )
    style.configure(
        "Sub.TLabel", background=C_SURFACE, foreground=C_TEXT3, font=ui_font(9)
    )
    style.configure(
        "CardTitle.TLabel", background=C_SURFACE, foreground=C_TEXT, font=ui_font(11, True)
    )

    # —— 按钮 ——
    style.configure(
        "TButton", background=C_SURFACE, foreground=C_TEXT,
        bordercolor=C_BORDER2, lightcolor=C_SURFACE, darkcolor=C_SURFACE,
        relief="solid", borderwidth=1, padding=(12, 6), font=ui_font(10),
    )
    style.map(
        "TButton",
        background=[("disabled", C_SURFACE), ("pressed", "#E9EDF3"), ("active", "#F3F5F9")],
        lightcolor=[("pressed", "#E9EDF3"), ("active", "#F3F5F9"), ("disabled", C_SURFACE)],
        darkcolor=[("pressed", "#E9EDF3"), ("active", "#F3F5F9"), ("disabled", C_SURFACE)],
        foreground=[("disabled", C_TEXT3)],
        bordercolor=[("disabled", C_BORDER), ("active", C_BORDER2)],
    )

    # 主操作：实心蓝
    style.configure(
        "Accent.TButton", background=C_PRIMARY, foreground="#FFFFFF",
        bordercolor=C_PRIMARY, lightcolor=C_PRIMARY, darkcolor=C_PRIMARY,
        relief="solid", borderwidth=1, padding=(16, 6), font=ui_font(10, True),
    )
    style.map(
        "Accent.TButton",
        background=[("disabled", "#AFC4EE"), ("pressed", C_PRIMARY_D), ("active", C_PRIMARY_H)],
        lightcolor=[("pressed", C_PRIMARY_D), ("active", C_PRIMARY_H), ("disabled", "#AFC4EE")],
        darkcolor=[("pressed", C_PRIMARY_D), ("active", C_PRIMARY_H), ("disabled", "#AFC4EE")],
        bordercolor=[("disabled", "#AFC4EE"), ("pressed", C_PRIMARY_D), ("active", C_PRIMARY_H)],
        foreground=[("disabled", "#F4F7FE")],
    )

    # 危险操作：默认白底，悬停才泛红
    style.configure(
        "Danger.TButton", background=C_SURFACE, foreground=C_ERR,
        bordercolor=C_BORDER2, lightcolor=C_SURFACE, darkcolor=C_SURFACE,
        relief="solid", borderwidth=1, padding=(14, 6), font=ui_font(10),
    )
    style.map(
        "Danger.TButton",
        background=[("disabled", C_SURFACE), ("pressed", "#F7D9D9"), ("active", C_ERR_SOFT)],
        lightcolor=[("disabled", C_SURFACE), ("pressed", "#F7D9D9"), ("active", C_ERR_SOFT)],
        darkcolor=[("disabled", C_SURFACE), ("pressed", "#F7D9D9"), ("active", C_ERR_SOFT)],
        foreground=[("disabled", "#D9A5A5")],
        bordercolor=[("active", "#EDBDBD"), ("disabled", C_BORDER)],
    )

    # 提示类按钮（失败现场 / 跳到失败）
    style.configure(
        "Ghost.TButton", background=C_SURFACE, foreground=C_TEXT2,
        bordercolor=C_BORDER, lightcolor=C_SURFACE, darkcolor=C_SURFACE,
        relief="solid", borderwidth=1, padding=(12, 6), font=ui_font(10),
    )
    style.map(
        "Ghost.TButton",
        background=[("disabled", C_SURFACE), ("pressed", "#E9EDF3"), ("active", C_PRIMARY_SOFT)],
        lightcolor=[("disabled", C_SURFACE), ("pressed", "#E9EDF3"), ("active", C_PRIMARY_SOFT)],
        darkcolor=[("disabled", C_SURFACE), ("pressed", "#E9EDF3"), ("active", C_PRIMARY_SOFT)],
        foreground=[("active", C_PRIMARY), ("disabled", C_TEXT3)],
        bordercolor=[("active", "#C7D8F8"), ("disabled", C_BORDER)],
    )

    # —— 输入框 ——
    style.configure(
        "TEntry", fieldbackground=C_SURFACE, foreground=C_TEXT,
        bordercolor=C_BORDER2, lightcolor=C_BORDER2, darkcolor=C_BORDER2,
        insertcolor=C_TEXT, padding=(8, 5), relief="flat",
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", C_PRIMARY)],
        lightcolor=[("focus", C_PRIMARY)],
        darkcolor=[("focus", C_PRIMARY)],
    )

    style.configure(
        "TCombobox", fieldbackground=C_SURFACE, background=C_SURFACE,
        foreground=C_TEXT, arrowcolor=C_TEXT2, bordercolor=C_BORDER2,
        lightcolor=C_BORDER2, darkcolor=C_BORDER2, padding=(8, 4),
        relief="flat", arrowsize=14,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", C_SURFACE), ("disabled", C_SUNK)],
        foreground=[("readonly", C_TEXT), ("disabled", C_TEXT3)],
        arrowcolor=[("active", C_PRIMARY)],
        bordercolor=[("focus", C_PRIMARY), ("active", C_BORDER2)],
    )
    root.option_add("*TCombobox*Listbox.background", C_SURFACE)
    root.option_add("*TCombobox*Listbox.foreground", C_TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", C_PRIMARY)
    root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
    root.option_add("*TCombobox*Listbox.borderWidth", 0)

    # —— 勾选框 ——
    for name, bg in (("TCheckbutton", C_BG), ("Surface.TCheckbutton", C_SURFACE)):
        style.configure(
            name, background=bg, foreground=C_TEXT2, font=ui_font(10),
            indicatorbackground=C_SURFACE, indicatorforeground="#FFFFFF",
            upperbordercolor=C_BORDER2, lowerbordercolor=C_BORDER2,
            padding=(2, 3), focuscolor=bg,
        )
        style.map(
            name,
            background=[("active", bg)],
            foreground=[("disabled", C_TEXT3), ("active", C_TEXT)],
            indicatorbackground=[
                ("disabled", "#EEF0F4"), ("selected", C_PRIMARY), ("active", "#F3F5F9"),
            ],
            indicatorforeground=[("selected", "#FFFFFF")],
            upperbordercolor=[("selected", C_PRIMARY), ("active", C_BORDER2)],
            lowerbordercolor=[("selected", C_PRIMARY), ("active", C_BORDER2)],
        )

    # —— 进度条：做成一条细线，压在底部操作栏的顶边 ——
    style.configure(
        "Thin.Horizontal.TProgressbar", background=C_PRIMARY,
        troughcolor="#EDEEF1", bordercolor="#EDEEF1",
        lightcolor=C_PRIMARY, darkcolor=C_PRIMARY, thickness=3,
    )

    # —— 滚动条：细、无箭头 ——
    style.configure(
        "Vertical.TScrollbar", background="#C9CED8", troughcolor=C_BG,
        bordercolor=C_BG, arrowcolor=C_BG, lightcolor="#C9CED8",
        darkcolor="#C9CED8", relief="flat", borderwidth=0, arrowsize=0,
        width=8,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("pressed", "#A9B1BF"), ("active", "#B5BCC8"), ("disabled", C_BG)],
        lightcolor=[("pressed", "#A9B1BF"), ("active", "#B5BCC8")],
        darkcolor=[("pressed", "#A9B1BF"), ("active", "#B5BCC8")],
        arrowcolor=[("pressed", "#A9B1BF"), ("active", "#B5BCC8")],
    )

    # —— 分栏 ——
    style.configure("TPanedwindow", background=C_BG)
    style.configure("Sash", sashthickness=10, gripcount=0, background=C_BG)

    # —— 表格（定位库 / 环境自检 / 失败现场 / 预检都用它）——
    style.configure(
        "Treeview", background=C_SURFACE, fieldbackground=C_SURFACE,
        foreground=C_TEXT, bordercolor=C_BORDER, rowheight=28,
        font=ui_font(10), borderwidth=0, relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", C_PRIMARY_SOFT)],
        foreground=[("selected", C_PRIMARY)],
    )
    style.configure(
        "Treeview.Heading", background=C_SUNK, foreground=C_TEXT2,
        font=ui_font(9, True), relief="flat", borderwidth=0, padding=(8, 7),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#EFF2F6")],
        foreground=[("active", C_TEXT)],
    )

    # —— 分组框：改成「白底 + 1px 细边 + 小标题」的卡片感 ——
    style.configure(
        "TLabelframe", background=C_SURFACE, bordercolor=C_BORDER,
        lightcolor=C_SURFACE, darkcolor=C_SURFACE, relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label", background=C_SURFACE, foreground=C_TEXT2,
        font=ui_font(9, True),
    )

    # —— 分页 ——
    style.configure(
        "TNotebook", background=C_BG, bordercolor=C_BORDER, tabmargins=(2, 6, 2, 0),
    )
    style.configure(
        "TNotebook.Tab", background="#EBEEF3", foreground=C_TEXT2,
        padding=(16, 7), font=ui_font(10), borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", C_SURFACE)],
        foreground=[("selected", C_PRIMARY)],
        expand=[("selected", (0, 0, 0, 0))],
    )

    # 弹窗的默认底色也跟着走，否则 tk.Toplevel 露出系统灰
    root.option_add("*Toplevel.background", C_BG)

    # —— 菜单 ——
    root.option_add("*Menu.background", C_SURFACE)
    root.option_add("*Menu.foreground", C_TEXT)
    root.option_add("*Menu.activeBackground", C_PRIMARY_SOFT)
    root.option_add("*Menu.activeForeground", C_PRIMARY)
    root.option_add("*Menu.relief", "flat")
    root.option_add("*Menu.borderWidth", 0)
    root.option_add("*Menu.activeBorderWidth", 0)


def wheel_steps(event):
    """把滚轮事件换算成「滚动几行」。

    两个平台的 event.delta 量纲完全不同：
      · Windows：恒为 120 的倍数（一格 = ±120）
      · macOS  ：只有 ±1 ~ ±10，触控板还带惯性
    所以原来那句 `-int(delta / 120)` 在 Windows 上没问题，在 macOS 上除出来
    永远是 0 —— 这就是「列表滚不动」的直接原因。
    """
    delta = event.delta
    if not delta:
        return 0
    if sys.platform == "darwin":
        # 触控板一次事件能到 ±10，按行滚会「飞」，限到 ±3 更接近原生手感
        return max(-3, min(3, -int(delta)))
    if abs(delta) >= 120:
        return -int(delta / 120)
    return -1 if delta > 0 else 1


# --------------------------------------------------------------------------
# 基础探测函数
# --------------------------------------------------------------------------
def port_open(port, host=APPIUM_HOST, timeout=0.6):
    """用 TCP 连接判断端口是否已被监听（比发 HTTP 请求更轻、无副作用）。"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except OSError:
        return False


def find_appium():
    """定位 appium 可执行文件（npm 全局安装后通常是 appium.cmd）。"""
    exe = shutil.which("appium")
    if exe:
        return exe
    home = os.path.expanduser("~")
    candidates = [
        # macOS：Homebrew / npm 全局 / nvm 常见位置
        "/opt/homebrew/bin/appium",
        "/usr/local/bin/appium",
        os.path.join(home, ".npm-global/bin/appium"),
        os.path.join(home, "node_modules/.bin/appium"),
        # Windows
        os.path.expanduser(r"~\AppData\Roaming\npm\appium.cmd"),
        r"C:\Program Files\nodejs\appium.cmd",
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return None


def open_in_os(path):
    """用系统默认方式打开文件或目录（os.startfile 只有 Windows 有）。"""
    path = os.path.abspath(path)
    if hasattr(os, "startfile"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def file_url(path):
    return pathlib.Path(path).resolve().as_uri()


def find_adb():
    """定位 adb 可执行文件。

    双击启动的 GUI（或 IDE 里的非登录 shell）PATH 往往不含 Android SDK，
    只写 "adb" 会直接 FileNotFoundError，被上层误判成「没有设备」。
    """
    exe = shutil.which("adb")
    if exe:
        return exe
    home = os.path.expanduser("~")
    sdk_dirs = [
        os.environ.get("ANDROID_HOME", ""),
        os.environ.get("ANDROID_SDK_ROOT", ""),
        os.path.join(home, "Library/Android/sdk"),          # macOS 默认
        os.path.join(home, "Android/Sdk"),                  # Linux 默认
        os.path.expanduser(r"~\AppData\Local\Android\Sdk"),  # Windows 默认
    ]
    names = ("adb.exe", "adb")
    for sdk in sdk_dirs:
        if not sdk:
            continue
        for name in names:
            cand = os.path.join(sdk, "platform-tools", name)
            if os.path.exists(cand):
                return cand
    for cand in ("/opt/homebrew/bin/adb", "/usr/local/bin/adb"):
        if os.path.exists(cand):
            return cand
    return None


def adb_devices_raw():
    """adb devices 的原始输出，用来区分「没设备」和「没授权」。"""
    adb = find_adb()
    if not adb:
        return ""
    try:
        return subprocess.check_output(
            [adb, "devices"], stderr=subprocess.STDOUT, text=True, timeout=10
        )
    except Exception:
        return ""


def connected_devices():
    """返回当前 adb 在线设备列表，仅用于界面展示。"""
    out = adb_devices_raw()
    if not out:
        return []
    devices = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def pick_udid():
    """本次执行用哪台设备 —— 与界面「环境状态」显示的那台严格一致。

    conftest 里 DeviceDetector.select_device() 的取值顺序是：
      1) 环境变量 ANDROID_UDID
      2) 只有一台设备 → 自动选
      3) 多台设备 → input() 让用户选
    第 3 步在 GUI 下必然炸：子进程的 stdin 是 DEVNULL，input() 直接 EOFError，
    而报错信息跟真实原因（多设备）完全对不上。所以这里替它选好再传下去。
    """
    wanted = os.getenv("ANDROID_UDID", "").strip()
    devs = connected_devices()
    # 显式指定就尊重它（adb 查不到列表时也照用）；否则取列表第一台
    if wanted and (not devs or wanted in devs):
        return wanted
    return devs[0] if devs else None


_RUNTIME_OK = None   # 自检一旦成功就缓存：import appium 有几百毫秒，不必每次点运行都付


def probe_runtime(timeout=30):
    """自检 .venv 的解释器与依赖，返回 (ok, 说明)。

    为什么不能只查文件存在：这个工具在 macOS 和 Windows 上各跑一份，而 .venv
    是不通用的（bin/python vs Scripts\\python.exe），拷过去路径必然对不上；
    就算路径碰巧对上，也可能依赖没装。所以直接让解释器 import 一次，
    问题在「点运行」这一步就说清楚，而不是等 pytest 抛 ModuleNotFoundError。
    """
    global _RUNTIME_OK
    if _RUNTIME_OK:
        return True, _RUNTIME_OK

    if not os.path.exists(VENV_PYTHON):
        return False, (
            "找不到虚拟环境解释器：\n  {}\n\n"
            "换机器后 .venv 必须重建（Windows 与 macOS 的目录结构不同）。\n"
            "在项目根目录执行：\n"
            "  uv venv\n"
            "  uv pip install -r requirements/requirements.txt"
        ).format(VENV_PYTHON)

    try:
        res = subprocess.run(
            [VENV_PYTHON, "-c", "import pytest, appium; print('pytest', pytest.__version__)"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=CREATE_NO_WINDOW,
        )
    except Exception as exc:
        return False, "调用虚拟环境失败：{}\n  {}".format(exc, VENV_PYTHON)

    if res.returncode != 0:
        tail = [ln for ln in (res.stderr or "").strip().splitlines() if ln.strip()][-3:]
        return False, (
            "虚拟环境里缺依赖（pytest / appium）：\n  {}\n\n{}\n\n"
            "修复：uv pip install -r requirements/requirements.txt"
        ).format(
            VENV_PYTHON,
            "\n".join("  " + ln for ln in tail) or "  （无更详细信息）",
        )

    _RUNTIME_OK = res.stdout.strip()
    return True, _RUNTIME_OK


def adb_shell(udid, *args, timeout=20):
    """带 -s 的 adb 调用，返回 (returncode, 输出)。

    必须带 udid：同时插着两台时裸 adb 会直接报 more than one device，
    stdout 为空，调用方会把「查不了」误判成「没装」。
    """
    adb = find_adb()
    if not adb:
        return 127, "找不到 adb"
    cmd = [adb] + (["-s", udid] if udid else []) + list(args)
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, creationflags=CREATE_NO_WINDOW,
        )
        return res.returncode, (res.stdout or "") + (res.stderr or "")
    except Exception as exc:
        return 1, str(exc)


# --------------------------------------------------------------------------
# pytest 输出解析
#
# `-v` 下每条用例完成时打印一行：
#     testcases/test_home_style.py::test_login PASSED     [  1%]
# 末尾的 [ 1%] 正好就是进度，不用再额外加插件。
# --------------------------------------------------------------------------
RE_RESULT = re.compile(
    r"^(?P<node>[^\s]+::[^\s]+)\s+"
    r"(?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b"
)
RE_PERCENT = re.compile(r"\[\s*(?P<pct>\d{1,3})%\]\s*$")
RE_SUMMARY = re.compile(r"^=+ (?P<body>[^=].*?) =+$")
RE_COUNT = re.compile(r"(\d+) (passed|failed|error|errors|skipped|xfailed|xpassed)")


class PytestOutput:
    """边跑边解析 pytest 输出，把「结果 / 进度 / 汇总」分发给界面。"""

    def __init__(self):
        self.results = {}      # nodeid -> PASSED/FAILED/...
        self.percent = 0
        self.summary = ""
        self.counts = {}

    def feed(self, line):
        """喂一行原始输出，返回事件列表。

        事件形式：
          ("result", nodeid, status)   一条用例有了结论
          ("progress", pct)            进度百分比
          ("summary", 文本)            最终那行统计
        """
        events = []
        text = line.strip()

        m = RE_RESULT.match(text)
        if m:
            node, status = m.group("node"), m.group("status")
            self.results[node] = status
            events.append(("result", node, status))

        p = RE_PERCENT.search(text)
        if p:
            pct = min(100, int(p.group("pct")))
            if pct >= self.percent:
                self.percent = pct
                events.append(("progress", pct))

        s = RE_SUMMARY.match(text)
        if s and (" in " in s.group("body") or "no tests ran" in s.group("body")):
            body = s.group("body")
            self.summary = body
            self.counts = {k: int(n) for n, k in RE_COUNT.findall(body)}
            events.append(("summary", body))
        return events


def nodeid_to_iid(nodeid):
    """pytest 的 nodeid（testcases/x.py::test_y）→ 界面里的行 id（x.py::test_y）。"""
    return nodeid.replace("\\", "/").split("testcases/", 1)[-1]


def load_failure_records():
    """列出 logs/failures 下的失败现场，新的在前。"""
    out = []
    if not os.path.isdir(FAILURES_DIR):
        return out
    for name in os.listdir(FAILURES_DIR):
        folder = os.path.join(FAILURES_DIR, name)
        meta_path = os.path.join(folder, "meta.json")
        if not os.path.isdir(folder) or not os.path.exists(meta_path):
            continue
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            continue
        meta["folder"] = folder
        out.append(meta)
    out.sort(key=lambda m: m.get("time", ""), reverse=True)
    return out



# --------------------------------------------------------------------------
# 用例发现：AST 静态解析，不 import
# --------------------------------------------------------------------------
def extract_test_functions(path):
    """解析模块顶层以 test_ 开头的函数名。

    刻意用 AST 而非正则：用例文件里有大量被注释掉的 `# def test_xxx(...)`，
    正则会把它们一起捞进来，AST 不会。
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read(), filename=path)
    except (SyntaxError, OSError):
        return []
    return [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def discover_cases():
    """返回 [(文件名, [用例函数名, ...]), ...]，规则对齐 pytest.ini 的 python_files。"""
    result = []
    if not os.path.isdir(TESTCASE_DIR):
        return result
    for name in sorted(os.listdir(TESTCASE_DIR)):
        if not name.startswith("test_") or not name.endswith(".py"):
            continue
        result.append((name, extract_test_functions(os.path.join(TESTCASE_DIR, name))))
    return result


# --------------------------------------------------------------------------
# Appium 服务管理
# --------------------------------------------------------------------------
class AppiumManager:
    """负责「保证 4723 上有一个可用的 Appium Server」——只启动，不主动关停。"""

    def __init__(self, log):
        self.log = log
        self.proc = None
        self._logfile = None

    def is_running(self):
        return port_open(APPIUM_PORT)

    def ensure(self):
        """探测 -> 已在跑则复用；否则启动并等待端口就绪。返回 True/False。"""
        if self.is_running():
            self.log(f"Appium Server 已在 {APPIUM_PORT} 端口运行，直接复用。", "ok")
            return True

        exe = find_appium()
        if not exe:
            self.log(
                "未找到 appium 可执行文件。请先执行：npm install -g appium",
                "error",
            )
            return False

        os.makedirs(LOGS_DIR, exist_ok=True)
        # 以追加方式持有句柄，让 Appium 输出全程落到 logs/appium_server.log
        self._logfile = open(APPIUM_LOG, "a", encoding="utf-8", errors="replace")
        self._logfile.write(
            f"\n===== {_dt.datetime.now():%Y-%m-%d %H:%M:%S} "
            f"启动 Appium Server =====\n"
        )
        self._logfile.flush()

        self.log(f"正在启动 Appium Server（{exe} --port {APPIUM_PORT}）…", "info")
        try:
            # appium 在 Windows 上是 .cmd，必须交给 shell 解析
            self.proc = subprocess.Popen(
                f'"{exe}" --port {APPIUM_PORT}',
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=self._logfile,
                stderr=subprocess.STDOUT,
                creationflags=CREATE_NO_WINDOW,
            )
        except Exception as exc:
            self.log(f"启动 Appium 失败：{exc}", "error")
            return False

        # 最多等 30 秒
        for _ in range(60):
            if port_open(APPIUM_PORT):
                self.log(
                    f"Appium Server 已就绪（PID {self.proc.pid}，端口 {APPIUM_PORT}）。"
                    f"日志见 logs/appium_server.log",
                    "ok",
                )
                return True
            if self.proc.poll() is not None:
                self.log(
                    "Appium 进程启动后立即退出，请查看 logs/appium_server.log 排查。",
                    "error",
                )
                return False
            time.sleep(0.5)

        self.log("等待 Appium 就绪超时（30s），请检查端口占用或日志。", "error")
        return False


# --------------------------------------------------------------------------
# pytest 执行器
# --------------------------------------------------------------------------
class PytestRunner:
    """在独立线程里跑 pytest，逐行读取输出并投递到消息队列。"""

    def __init__(self, msg_queue):
        self.queue = msg_queue
        self.proc = None
        self.thread = None

    @property
    def busy(self):
        return self.proc is not None and self.proc.poll() is None

    def start(self, targets, max_fail_fast, html_report, udid=None):
        cmd = [VENV_PYTHON, "-m", "pytest", *targets, "-v"]
        # 命令行参数会覆盖 pytest.ini 里 addopts 的同名项：0 表示不限制失败数
        cmd.append(f"--maxfail={1 if max_fail_fast else 0}")
        if html_report:
            cmd += [f"--html={html_report}", "--self-contained-html"]

        env = os.environ.copy()
        # 关键：强制子进程用 UTF-8 写管道并关闭缓冲，
        # 否则中文日志在 Windows 下会按 GBK 编码 → 界面乱码；缓冲会让日志攒到最后才出现。
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"
        # 设备由界面这一层定：conftest → DeviceDetector.select_device() 优先读
        # ANDROID_UDID。传下去才能保证「界面显示的那台」就是「真正跑的那台」。
        if udid:
            env["ANDROID_UDID"] = udid

        # Windows：CREATE_NEW_PROCESS_GROUP 让「停止」能发 CTRL_BREAK 走正常收尾；
        # POSIX：start_new_session 让 pytest 自成进程组，才能整组 killpg 干净收掉。
        # （creationflags=0 在 POSIX 上会被忽略，但 start_new_session 不存在于 Windows，
        #  所以两者只能二选一，不能都传。）
        popen_extra = (
            {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
            if os.name == "nt"
            else {"start_new_session": True}
        )

        self.queue.put(("log", f"$ {' '.join(cmd)}"))
        try:
            self.proc = subprocess.Popen(
                cmd,
                cwd=PROJECT_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
                **popen_extra,
            )
        except Exception as exc:
            self.queue.put(("log", f"启动 pytest 失败：{exc}"))
            self.queue.put(("done", -1, None))
            return False

        self.thread = threading.Thread(target=self._pump, daemon=True)
        self.thread.start()
        return True

    def _pump(self):
        try:
            for line in self.proc.stdout:
                self.queue.put(("log", line.rstrip("\n")))
        finally:
            code = self.proc.wait()
            self.queue.put(("done", code, None))
            try:
                self.proc.stdout.close()
            except Exception:
                pass

    def _wait_exit(self, timeout):
        """最多等 timeout 秒，返回进程是否已退出。"""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if self.proc.poll() is not None:
                return True
            time.sleep(0.1)
        return self.proc.poll() is not None

    def stop(self):
        """终止 pytest 及其派生的子进程（两个平台两套做法）。

        关键不在「杀掉」，而在「让它有机会收尾」：driver 是 session 级 fixture，
        只有 pytest 正常退出才会执行 driver.quit()。直接强杀会让 Appium 侧留着
        一个 session 不释放，下次连接就报 session is already running —— 这也是
        之前「停止之后要拔线重连」的真正原因。

        所以两边都是先礼后兵：
          · Windows：CTRL_BREAK_EVENT（等价控制台 Ctrl+Break）→ taskkill /F /T
          · POSIX  ：SIGINT（等价 Ctrl+C）→ SIGTERM → SIGKILL
        """
        proc = self.proc
        if proc is None or proc.poll() is not None:
            return False

        if os.name == "nt":
            ctrl_break = getattr(signal, "CTRL_BREAK_EVENT", None)
            if ctrl_break is not None:
                try:
                    proc.send_signal(ctrl_break)
                    if self._wait_exit(3.0):
                        return True
                except (OSError, ValueError):
                    # 从 pythonw / 无控制台的进程启动时会失败，退回强杀
                    pass
            try:
                # /T 连带子进程，/F 强制；否则 terminate() 只杀父进程
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=CREATE_NO_WINDOW,
                )
            except Exception:
                proc.terminate()
            return True

        # POSIX：start_new_session=True 时 pgid == pid，整组一起收。
        pgid = None
        try:
            pgid = os.getpgid(proc.pid)
            # 保险：万一 start_new_session 没生效、pgid 恰好吃到本进程的组，
            # killpg 会把 GUI 自己一起杀掉 —— 宁可不收子进程，也不能自杀。
            if pgid == os.getpgid(0):
                pgid = None
        except OSError:
            pgid = None

        def _send(sig):
            try:
                if pgid is not None:
                    os.killpg(pgid, sig)
                else:
                    proc.send_signal(sig)
            except ProcessLookupError:
                pass
            except OSError:
                pass

        for sig, grace in (
            (signal.SIGINT, 3.0),
            (signal.SIGTERM, 2.0),
            (getattr(signal, "SIGKILL", signal.SIGTERM), 1.0),
        ):
            if proc.poll() is not None:
                return True
            _send(sig)
            if self._wait_exit(grace):
                return True
        return True


# --------------------------------------------------------------------------
# 打印机编号历史
#
# 三台机器的编号是「每天可能要换、但来回就那么几台」的值，纯手敲很容易
# 敲错一位、然后卡在元素定位找不到上。这里把它记进 config/param_history.json，
# 下次直接在输入框里挑。三个输入框共用同一套候选：实际使用中一台机器的
# 编号出现在第几台取决于当天测什么，分开记反而要把同一个值输三遍。
# --------------------------------------------------------------------------
def _dedupe(values, limit=None):
    """去重（不分大小写，保留第一次出现的写法），并截断到 limit 条。"""
    out, seen = [], set()
    for v in values:
        v = str(v or "").strip()
        if not v:
            continue
        key = v.upper()
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
        if limit and len(out) >= limit:
            break
    return out


def device_history():
    """读历史编号，最新的排最前；文件缺失或损坏都当作空历史。"""
    try:
        with open(PARAM_HISTORY, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    values = data.get("device_number") if isinstance(data, dict) else None
    if not isinstance(values, list):
        return []
    return _dedupe(values, HISTORY_LIMIT)


def remember_devices(values):
    """把本次用过的编号并入历史并落盘，返回合并后的列表。

    写盘失败只是少了「下次能选」，不该打断保存流程，所以这里吞掉异常。
    """
    old = device_history()
    merged = _dedupe(list(values) + old, HISTORY_LIMIT)
    if merged == old:                   # 没有新值就不碰文件
        return merged
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(PARAM_HISTORY, "w", encoding="utf-8") as f:
            json.dump({"device_number": merged}, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
    return merged


# --------------------------------------------------------------------------
# 测试参数编辑窗口
# --------------------------------------------------------------------------
class ParamDialog(tk.Toplevel):
    """测试参数统一编辑窗口（单页，不再按文件分页）。

    布局分两块：
      · **全局参数**：locators.py 这类共享文件里的值（设备编号），一行一个，
        右侧标出所在文件与行号；
      · **用例参数**：每个用例文件一列、同一参数横向对齐，方便一眼比出两套
        用例的差异（比如耗材尺寸），也免得来回翻 tab 才看得全。

    「确定并保存」会把这些值**直接改写进对应文件的那几行**（源码即配置，项目
    里没有额外的配置文件）。写入前会做语法自检并留备份，所以改完立即生效，
    不需要重启工具。
    """

    def __init__(self, master, files, title="测试参数", on_save=None):
        super().__init__(master)
        self.files = list(files)
        self.on_save = on_save
        self.result = False
        self._vars = {f: {} for f in self.files}   # 文件名 -> {字段: StringVar}
        self._slots = {}                           # 文件名 -> {字段: slot}
        self._hidden = []                          # 没有参数行、未在界面上展示的文件

        self.title(title)
        self.resizable(False, False)
        self.transient(master)

        head = ttk.Frame(self, padding=(14, 12, 14, 2))
        head.pack(fill="x")
        ttk.Label(
            head,
            text="设备编号写在 locators.py，用例参数各写各的文件；改完点「确定并保存」即生效。",
            foreground=C_TEXT2,
        ).pack(anchor="w")

        body = ttk.Frame(self, padding=(14, 8, 14, 2))
        body.pack(fill="both", expand=True)
        self._build_body(body)

        foot = ttk.Frame(self, padding=(14, 6, 14, 12))
        foot.pack(fill="x")
        ttk.Button(foot, text="恢复初始值", width=12, command=self._restore).pack(
            side="left"
        )
        ttk.Button(foot, text="取消", width=10, style="Ghost.TButton",
                   command=self._cancel).pack(side="right")
        ttk.Button(foot, text="确定并保存", width=12, style="Accent.TButton",
                   command=self._save).pack(
            side="right", padx=(0, 8)
        )

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda e: self._cancel())
        self._center(master)
        # 模态：让「运行前确认」必须被响应，避免用户在弹窗期间重复点「开始运行」
        try:
            self.grab_set()
        except tk.TclError:
            pass

    # ---------------- 布局 ----------------
    def _build_body(self, parent):
        """单页布局：全局参数一块 + 用例参数一张表。

        共享文件（param_editor.EXTRA_FILES，目前只有 locators.py）单独成块，
        不与用例参数混排 —— 它管的是「连哪台机器」，跟具体用例无关。
        """
        self._slots = param_editor.scan(self.files)
        shared = [
            f for f in self.files
            if f in param_editor.EXTRA_FILES and self._slots.get(f)
        ]
        cases = [
            f for f in self.files
            if f not in param_editor.EXTRA_FILES and self._slots.get(f)
        ]
        self._hidden = [f for f in self.files if not self._slots.get(f)]

        if not shared and not cases:
            ttk.Label(
                parent, text="没有找到可改写的参数行。", foreground=C_TEXT3
            ).pack(anchor="w", pady=12)
            return

        if shared:
            self._build_shared_block(parent, shared)
        if cases:
            self._build_case_table(parent, cases)
        if self._hidden:
            ttk.Label(
                parent,
                text="未展示（文件里没有参数行）：" + "、".join(self._hidden),
                foreground=C_TEXT3,
            ).pack(anchor="w", pady=(8, 0))

    def _build_shared_block(self, parent, files):
        box = ttk.LabelFrame(parent, text="全局参数（所有用例共用）", padding=(12, 8))
        box.pack(fill="x", pady=(0, 10))
        box.columnconfigure(1, weight=1)

        r = 0
        for fname in files:
            for key, slot in self._slots[fname].items():
                ttk.Label(box, text=param_editor.FIELD_LABELS.get(key, key)).grid(
                    row=r, column=0, sticky="w", padx=(0, 14), pady=4
                )
                var = tk.StringVar(value=self._initial(slot))
                self._make_input(box, var, key, 30).grid(
                    row=r, column=1, sticky="w", pady=4
                )
                # 标出文件+行号：改完能直接去源码核对，也免得以为改错了地方
                ttk.Label(
                    box,
                    text="{} 第 {} 行".format(fname, slot["lineno"]),
                    foreground=C_TEXT3,
                ).grid(row=r, column=2, sticky="w", padx=(10, 0), pady=4)
                self._vars[fname][key] = var
                r += 1

        if any(k in DEVICE_FIELDS for slots in self._slots.values() for k in slots):
            ttk.Label(
                box,
                text="点右侧箭头可选之前用过的编号，三台共用一份历史（最多 {} 条）".format(
                    HISTORY_LIMIT
                ),
                foreground=C_TEXT3,
            ).grid(row=r, column=1, columnspan=2, sticky="w", pady=(6, 0))

    def _make_input(self, parent, var, key, width):
        """参数输入控件：打印机编号给历史下拉，其余是普通输入框。

        下拉特意用 state="normal"（可编辑）而不是 readonly：换了台新机器时
        要能直接敲进去，不能只能从旧值里挑。
        """
        if key in DEVICE_FIELDS:
            return ttk.Combobox(
                parent, textvariable=var, width=width - 2,
                values=self._device_choices(), state="normal",
            )
        return ttk.Entry(parent, textvariable=var, width=width)

    def _device_choices(self):
        """候选项 = 源码里的现值（排最前，免得被历史淹掉）+ 历史记录。"""
        current = []
        for slots in self._slots.values():
            for key in DEVICE_FIELDS:
                slot = slots.get(key)
                if slot and slot["value"]:
                    current.append(slot["value"])
        return _dedupe(current + device_history(), HISTORY_LIMIT)

    def _build_case_table(self, parent, files):
        """列＝用例文件，行＝参数；某文件没有该参数时留「—」。"""
        box = ttk.LabelFrame(parent, text="用例参数（每个文件一列）", padding=(12, 8))
        box.pack(fill="both", expand=True)
        for c in range(1, len(files) + 1):
            box.columnconfigure(c, weight=1)

        for c, fname in enumerate(files, start=1):
            ttk.Label(
                box, text=fname, font=ui_font(10, True)
            ).grid(row=0, column=c, sticky="w", padx=(0, 12))
            ttk.Label(
                box,
                text=self._line_hint(self._slots[fname].values()),
                foreground=C_TEXT3,
            ).grid(row=1, column=c, sticky="w", padx=(0, 12), pady=(0, 4))

        keys = [
            k for k in param_editor.FIELD_ORDER
            if any(k in self._slots[f] for f in files)
        ]
        for r, key in enumerate(keys, start=2):
            ttk.Label(box, text=param_editor.FIELD_LABELS.get(key, key)).grid(
                row=r, column=0, sticky="w", padx=(0, 16), pady=5
            )
            for c, fname in enumerate(files, start=1):
                slot = self._slots[fname].get(key)
                if slot is None:
                    ttk.Label(box, text="—", foreground=C_TEXT3).grid(
                        row=r, column=c, sticky="w", padx=(0, 12), pady=5
                    )
                    continue
                var = tk.StringVar(value=self._initial(slot))
                self._make_input(box, var, key, 18).grid(
                    row=r, column=c, sticky="we", padx=(0, 12), pady=5
                )
                self._vars[fname][key] = var

    @staticmethod
    def _initial(slot):
        return slot["value"] if slot["value"] is not None else ""

    @staticmethod
    def _line_hint(slots):
        """把一组行号压成「第 38-41 行」；不连续就逐个列出。"""
        nums = sorted(s["lineno"] for s in slots)
        if not nums:
            return ""
        if len(nums) == 1:
            return "第 {} 行".format(nums[0])
        if nums[-1] - nums[0] == len(nums) - 1:
            return "第 {}-{} 行".format(nums[0], nums[-1])
        return "第 " + "、".join(str(n) for n in nums) + " 行"

    def _restore(self):
        """把所有输入框恢复成初始值（改造前的原始值），误操作后有退路。

        单页展示后就整体恢复，不再区分「当前页」—— 用户看到的是一张表，
        期望的也是整张表一起回到默认。
        只改输入框内容，仍需点「确定并保存」才写回源码。
        """
        for fname, vars_ in self._vars.items():
            seed = param_editor.SEED.get(fname) or {}
            current = param_editor.read_params(fname)
            for key, var in vars_.items():
                var.set(seed.get(key, current.get(key) or ""))

    def _save(self):
        mapping = {
            fname: {key: var.get().strip() for key, var in vars_.items()}
            for fname, vars_ in self._vars.items()
        }
        changed, errors = param_editor.apply(mapping)
        if errors and not changed:
            messagebox.showerror(
                "保存失败",
                "没能写入源码：\n\n" + "\n".join(errors),
                parent=self,
            )
            return

        # 只记真正写进源码的编号：敲错一位的号码留在下拉里，下次更容易挑错
        remember_devices([
            mapping[fname][key]
            for fname in mapping if fname in param_editor.EXTRA_FILES
            for key in DEVICE_FIELDS if key in mapping[fname]
        ])

        self.result = True
        if self.on_save:
            if changed:
                self.on_save("已直接写入源码：" + "，".join(changed), "ok")
            else:
                self.on_save("参数没有变化，未改动任何文件。", "info")
            for e in errors:
                self.on_save("    " + e, "warn")
        self._close()

    def _cancel(self):
        self.result = False
        self._close()

    def _close(self):
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def _center(self, master):
        """居中于主窗口。

        必须用 reqwidth/reqheight：尚未映射的 Toplevel 调 winfo_width() 会
        返回 1，拿它算位置会把弹窗推到主窗口右边缘之外（实测踩过）。
        """
        self.update_idletasks()
        w = self.winfo_reqwidth() or self.winfo_width()
        h = self.winfo_reqheight() or self.winfo_height()
        try:
            mw, mh = master.winfo_width(), master.winfo_height()
            if mw <= 1 or mh <= 1:              # 主窗口还没完成布局
                mw, mh = self.winfo_screenwidth(), self.winfo_screenheight()
                mx = my = 0
            else:
                mx, my = master.winfo_rootx(), master.winfo_rooty()
            self.geometry(f"+{max(mx + (mw - w) // 2, 0)}+{max(my + (mh - h) // 3, 0)}")
        except tk.TclError:
            pass


# --------------------------------------------------------------------------
# 元素定位库窗口
# --------------------------------------------------------------------------
class LocatorDialog(tk.Toplevel):
    """locators.py 的浏览与体检窗口（**只读**，绝不改 locators.py）。

    体检走纯静态分析：不 import locators.py、不连设备、不占 Appium session，
    所以随时能开、零副作用、也不跟 pytest 抢设备。

    边界要说清楚：静态分析只能报「确定有问题」（引用缺失、重复定义、同一
    定位挂多 key）和「值得看一眼」（@text 硬编码、超长、没注释）。**「某条定位
    在真机上到底还灵不灵」强依赖当前所在页面**，静态看不了 —— 那属于要连设备
    的另一档功能，这里不冒充能做。
    """

    COLUMNS = (
        # (列 id, 表头, 初始宽, 对齐, 是否拉伸)
        ("lineno", "行", 48, "e", False),
        ("key", "key", 190, "w", False),
        ("by", "By", 56, "center", False),
        ("status", "状态", 54, "center", False),
        ("refs", "引用", 46, "e", False),
        ("selector", "selector", 340, "w", True),
        ("comment", "注释", 210, "w", True),
    )
    STATUS_TEXT = {"error": "错误", "warn": "警告", "info": "提示", "": "—"}
    LEVEL_RANK = {"error": 0, "warn": 1, "info": 2, "": 3}

    def __init__(self, master, on_log=None):
        super().__init__(master)
        self.on_log = on_log
        self.title("元素定位库 · locators.py")
        self.geometry("1060x680")
        self.minsize(880, 520)
        self.transient(master)

        self.data = locator_manager.report()
        self._entries = self.data["entries"]
        self._issues_by_key = {}
        for it in self.data["issues"]:
            self._issues_by_key.setdefault(it["key"], []).append(it)

        self._sort_col, self._sort_desc = "lineno", False
        self._by_iid = {}

        self._build()
        self.refresh()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda e: self.destroy())
        self._center(master)
        try:
            self.grab_set()
        except tk.TclError:
            pass

    # ---------------- 界面 ----------------
    def _build(self):
        head = ttk.Frame(self, padding=(12, 10, 12, 4))
        head.pack(fill="x")

        ttk.Label(head, text="搜索").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh())
        ttk.Entry(head, textvariable=self.search_var, width=26).pack(
            side="left", padx=(6, 12)
        )

        ttk.Label(head, text="定位方式").pack(side="left")
        self.by_var = tk.StringVar(value="全部")
        bys = ["全部"] + sorted({e["by"] for e in self._entries})
        ttk.Combobox(
            head, textvariable=self.by_var, values=bys, width=12, state="readonly"
        ).pack(side="left", padx=(6, 12))
        self.by_var.trace_add("write", lambda *a: self.refresh())

        self.only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            head, text="只看有问题的", variable=self.only_var, command=self.refresh
        ).pack(side="left")
        ttk.Button(head, text="重新体检", width=10, command=self._reload).pack(
            side="right"
        )

        self.stat_label = ttk.Label(self, padding=(12, 0, 12, 4), foreground=C_TEXT2)
        self.stat_label.pack(fill="x")

        wrap = ttk.Frame(self, padding=(12, 0, 12, 4))
        wrap.pack(fill="both", expand=True)
        cols = [c[0] for c in self.COLUMNS]
        self.tree = ttk.Treeview(
            wrap, columns=cols, show="headings", selectmode="browse"
        )
        for cid, title, width, anchor, stretch in self.COLUMNS:
            self.tree.heading(cid, text=title, command=lambda c=cid: self._sort_by(c))
            self.tree.column(cid, width=width, anchor=anchor, stretch=stretch)
        vs = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        # 行底色按最严重的问题等级着色，扫一眼就知道哪里要处理
        self.tree.tag_configure("error", background=C_ERR_SOFT, foreground=C_ERR)
        self.tree.tag_configure("warn", background=C_WARN_SOFT, foreground="#7A5B00")
        self.tree.tag_configure("info", background="#FFFFFF", foreground=C_TEXT2)
        self.tree.tag_configure("clean", background="#FFFFFF", foreground=C_TEXT)

        det = ttk.LabelFrame(self, text="详情", padding=(10, 6))
        det.pack(fill="x", padx=12, pady=(6, 0))
        self.detail = tk.Text(
            det, height=5, wrap="word", relief="flat", background=C_SUNK,
            font=ui_font(9), padx=6, pady=4,
        )
        self.detail.pack(fill="x")
        self.detail.configure(state="disabled")

        foot = ttk.Frame(self, padding=(12, 8, 12, 12))
        foot.pack(fill="x")
        ttk.Button(foot, text="复制 key", width=10, command=lambda: self._copy("key")).pack(side="left")
        ttk.Button(foot, text="复制 selector", width=13, command=lambda: self._copy("selector")).pack(side="left", padx=(6, 0))
        ttk.Button(foot, text="打开源码", width=10, command=self._open_source).pack(side="left", padx=(6, 0))
        ttk.Button(foot, text="关闭", width=10, command=self.destroy).pack(side="right")

    # ---------------- 数据与过滤 ----------------
    def _worst(self, issues):
        if not issues:
            return ""
        return min((i["level"] for i in issues), key=lambda l: self.LEVEL_RANK.get(l, 9))

    def refresh(self):
        kw = self.search_var.get().strip().lower()
        by = self.by_var.get()
        only = self.only_var.get()

        rows = []
        for e in self._entries:
            issues = self._issues_by_key.get(e["key"], [])
            if by != "全部" and e["by"] != by:
                continue
            if only and not issues:
                continue
            if kw:
                hay = " ".join(
                    (e["key"], e["selector"], e["comment"], e["section"])
                ).lower()
                if kw not in hay:
                    continue
            refs = sum(c for _, c in self.data["usage"].get(e["key"], []))
            rows.append((e, self._worst(issues), refs))

        rows.sort(key=self._sort_key, reverse=self._sort_desc)
        self.tree.delete(*self.tree.get_children())
        self._by_iid = {}
        for e, level, refs in rows:
            iid = self.tree.insert(
                "", "end",
                values=(
                    e["lineno"], e["key"], e["by"],
                    self.STATUS_TEXT.get(level, "—"),
                    refs or "", e["selector"], e["comment"],
                ),
                tags=(level or "clean",),
            )
            self._by_iid[iid] = e

        st = self.data["stats"]
        self.stat_label.configure(
            text="共 {} 条定位 · 被引用 {} 次 · 错误 {} / 警告 {} / 提示 {} 　│　"
                 "当前显示 {} 条".format(
                     st["total"], st["refs"], st["error"], st["warn"], st["info"],
                     len(rows),
                 )
        )
        self._show_detail(None)

    def _sort_key(self, row):
        e, level, refs = row
        col = self._sort_col
        if col == "lineno":
            return e["lineno"]
        if col == "refs":
            return refs
        if col == "status":
            return self.LEVEL_RANK.get(level, 9)
        return str(e.get(col, "")).lower()

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_desc = not self._sort_desc
        else:
            self._sort_col, self._sort_desc = col, False
        self.refresh()

    def _reload(self):
        """改完 locators.py 不用关窗口，点一下重新解析。"""
        self.data = locator_manager.report()
        self._entries = self.data["entries"]
        self._issues_by_key = {}
        for it in self.data["issues"]:
            self._issues_by_key.setdefault(it["key"], []).append(it)
        self.refresh()
        if self.on_log:
            self.on_log("已重新体检 locators.py。", "info")

    # ---------------- 详情 ----------------
    def _selected(self):
        sel = self.tree.selection()
        return self._by_iid.get(sel[0]) if sel else None

    def _show_detail(self, entry):
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        if entry:
            key = entry["key"]
            usage = self.data["usage"].get(key, [])
            lines = [
                "key：{}        行号：{}        By：{}".format(key, entry["lineno"], entry["by"]),
                "分段：{}    注释：{}".format(entry["section"], entry["comment"] or "(无)"),
                "",
                entry["selector"],
                "",
            ]
            if usage:
                lines.append("被引用 %d 次：" % sum(c for _, c in usage))
                for f, c in usage:
                    lines.append("    %-42s ×%d" % (f, c))
            else:
                lines.append("没有任何用例引用这个 key。")
            issues = self._issues_by_key.get(key, [])
            if issues:
                lines.append("")
                lines.append("体检：")
                for it in issues:
                    lines.append("    [{}] {}：{}".format(
                        self.STATUS_TEXT.get(it["level"], it["level"]), it["kind"], it["detail"]))
            self.detail.insert("1.0", "\n".join(lines))
        else:
            self.detail.insert(
                "1.0",
                "选中左侧任意一行查看完整 selector、被哪些用例引用、以及体检结论。\n"
                "点表头可按该列排序（行号 / key / By / 状态 / 引用）。",
            )
        self.detail.configure(state="disabled")

    def _on_select(self, _event=None):
        self._show_detail(self._selected())

    # ---------------- 动作 ----------------
    def _copy(self, field):
        entry = self._selected()
        if not entry:
            messagebox.showinfo("提示", "请先在列表里选中一行。", parent=self)
            return
        text = str(entry.get(field, ""))
        self.clipboard_clear()
        self.clipboard_append(text)
        if self.on_log:
            self.on_log("已复制 %s：%s" % (field, text[:80]), "info")

    def _open_source(self):
        entry = self._selected()
        lineno = entry["lineno"] if entry else None
        msg = locator_manager.open_source(lineno)
        if self.on_log:
            self.on_log(msg, "info")

    def _center(self, master):
        """居中于主窗口（与 ParamDialog 同理：未映射的窗口取 reqwidth）。"""
        self.update_idletasks()
        w = self.winfo_reqwidth() or self.winfo_width()
        h = self.winfo_reqheight() or self.winfo_height()
        try:
            mw, mh = master.winfo_width(), master.winfo_height()
            if mw <= 1 or mh <= 1:
                mw, mh = self.winfo_screenwidth(), self.winfo_screenheight()
                mx = my = 0
            else:
                mx, my = master.winfo_rootx(), master.winfo_rooty()
            self.geometry(f"+{max(mx + (mw - w) // 2, 0)}+{max(my + (mh - h) // 3, 0)}")
        except tk.TclError:
            pass


# --------------------------------------------------------------------------
# 元素拾取窗口
# --------------------------------------------------------------------------
class ElementPicker(tk.Toplevel):
    """连真机抓当前屏，点截图上的任意位置就出定位。

    与「元素定位」窗口的分工：那个纯静态体检 locators.py，不碰设备；
    这个必须连着设备，解决实际卡点 ——「屏幕上这个东西，定位该怎么写」。

    边界：只认识**当前这一屏**。要翻页就点窗口里的上滑/下滑/返回键，
    工具不猜页面路径，也不改 locators.py，只给你能直接粘贴的代码。
    """

    LEVEL_COLOR = {"ok": C_OK, "warn": C_WARN, "bad": C_ERR}

    def __init__(self, master, on_log=None, offline=None):
        super().__init__(master)
        self.on_log = on_log
        # offline：失败现场的 meta（截图 + 控件树都在磁盘上），此时不连设备
        self.offline = offline
        self.title(
            "元素拾取 · 失败现场（离线）" if offline else "元素拾取 · 点截图出定位"
        )
        self.geometry("1160x780")
        self.minsize(940, 620)
        self.transient(master)

        self.inspector = None
        self.snap = None
        self.node = None
        self.cands = []
        self._existing = ui_inspector.load_existing_entries()
        self._existing_keys = ui_inspector.load_existing_keys()
        self._taken_keys = set()
        self._photo_full = None
        self._photo_disp = None
        self._img_rect = (0, 0, 0, 0)
        self._busy = False
        self._alive = True
        self._exist_hit = None
        self._q = queue.Queue()
        self._logq = queue.Queue()      # 后台线程日志，主线程消费

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())
        self.bind("<F5>", lambda e: self._refresh())
        self._center(master)
        if offline:
            self._load_offline(offline)
            self._set_buttons()   # 立刻禁掉设备按钮，别让人误点「连接设备」
        self.after(120, self._poll)

    def _load_offline(self, meta):
        """用磁盘上的截图 + 控件树拼出一张「快照」。

        Snapshot 只要求 png 字节、解析好的控件树、窗口尺寸，
        所以离线复盘和在线拾取共用同一套点击 / 候选逻辑，不必另写一份。
        """
        folder = meta.get("folder", "")
        png_path = os.path.join(folder, meta.get("screenshot", "screenshot.png"))
        xml_path = os.path.join(folder, meta.get("page_source", "page.xml"))
        try:
            with open(png_path, "rb") as f:
                png = f.read()
            with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
        except Exception as exc:
            messagebox.showerror("打不开失败现场", str(exc), parent=self)
            return

        root = ui_inspector.parse(source)
        size = ui_inspector.png_size(png) or (0, 0)
        window = meta.get("window") or {}
        win = (window.get("width") or size[0], window.get("height") or size[1])
        snap = ui_inspector.Snapshot(
            png, root, source, win, meta.get("activity", ""), meta.get("time", "")
        )
        self._show(snap)
        self._set_status(
            "离线快照 · {} · {}（只看，不连设备）".format(
                meta.get("nodeid", "?"), (meta.get("time", "") or "")[:19].replace("T", " ")
            )
        )

    # ---------------- 界面 ----------------
    def _build(self):
        bar = ttk.Frame(self, padding=(12, 10, 12, 6))
        bar.pack(fill="x")

        self.conn_btn = ttk.Button(bar, text="连接设备", width=11, command=self._connect)
        self.conn_btn.pack(side="left")
        self.refresh_btn = ttk.Button(
            bar, text="刷新 F5", width=9, command=self._refresh, state="disabled"
        )
        self.refresh_btn.pack(side="left", padx=(6, 0))
        self.up_btn = ttk.Button(
            bar, text="上滑", width=6, command=lambda: self._swipe(True), state="disabled"
        )
        self.up_btn.pack(side="left", padx=(14, 0))
        self.down_btn = ttk.Button(
            bar, text="下滑", width=6, command=lambda: self._swipe(False), state="disabled"
        )
        self.down_btn.pack(side="left", padx=(5, 0))
        self.back_btn = ttk.Button(
            bar, text="返回", width=6, command=self._back, state="disabled"
        )
        self.back_btn.pack(side="left", padx=(5, 0))
        self.act_btn = ttk.Button(
            bar, text="拉起 App", width=9, command=self._activate, state="disabled"
        )
        self.act_btn.pack(side="left", padx=(5, 0))

        self.prefer_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            bar, text="优先选可点击控件", variable=self.prefer_var,
            command=self._redraw_marker,
        ).pack(side="left", padx=(16, 0))

        self.stat = ttk.Label(self, padding=(12, 0, 12, 4), foreground=C_TEXT2)
        self.stat.pack(fill="x")
        self._set_status("点「连接设备」开始：工具会拉起 App 并抓取当前这一屏")

        pane = ttk.Panedwindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        left = ttk.LabelFrame(pane, text="手机截图 · 点一下选中该位置的控件", padding=4)
        self.canvas = tk.Canvas(left, background=C_LOG_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        pane.add(left, weight=3)

        right = ttk.Frame(pane)
        pane.add(right, weight=2)

        # 属性
        info = ttk.LabelFrame(right, text="选中元素", padding=(8, 6))
        info.pack(fill="x")
        self.detail = tk.Text(
            info, height=7, wrap="none", relief="flat", background=C_SUNK,
            font=ui_font(9), padx=6, pady=4,
        )
        self.detail.pack(fill="x")
        self.detail.configure(state="disabled")
        ttk.Button(
            info, text="↑ 选父级（点到小图标时用）", command=self._select_parent
        ).pack(anchor="w", pady=(6, 0))

        # 候选
        cand = ttk.LabelFrame(
            right, text="定位方案（按推荐度排序，双击即复制）", padding=(8, 6)
        )
        cand.pack(fill="both", expand=True, pady=(8, 0))
        cols = ("kind", "count", "note")
        self.tree = ttk.Treeview(cand, columns=cols, show="headings", height=5,
                                 selectmode="browse")
        for cid, title, width, anchor, stretch in (
            ("kind", "策略", 152, "w", False),
            ("count", "命中", 46, "center", False),
            ("note", "结论", 210, "w", True),
        ):
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=width, anchor=anchor, stretch=stretch)
        vs = ttk.Scrollbar(cand, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_cand_select)
        self.tree.bind("<Double-1>", lambda e: self._copy("entry"))
        for lv, color in self.LEVEL_COLOR.items():
            self.tree.tag_configure(lv, foreground=color)

        # 代码
        code = ttk.LabelFrame(right, text="复制即用", padding=(8, 6))
        code.pack(fill="both", expand=True, pady=(8, 0))
        mono = mono_font(9)
        self.code = tk.Text(
            code, height=8, wrap="none", relief="flat", background=C_LOG_BG,
            foreground=C_LOG_FG, insertbackground=C_LOG_FG, font=mono, padx=8, pady=6,
        )
        self.code.pack(fill="both", expand=True)
        self.code.configure(state="disabled")

        foot = ttk.Frame(self, padding=(12, 0, 12, 10))
        foot.pack(fill="x")
        ttk.Button(foot, text="复制条目", width=11,
                   command=lambda: self._copy("entry")).pack(side="left")
        ttk.Button(foot, text="复制全部", width=11,
                   command=lambda: self._copy("all")).pack(side="left", padx=(6, 0))
        ttk.Button(foot, text="关闭", width=8, command=self._on_close).pack(side="right")

    # ---------------- 状态与异步 ----------------
    def _set_status(self, text):
        try:
            self.stat.configure(text=text)
        except tk.TclError:
            pass

    def _log(self, msg):
        """连设备跑在后台线程，这里只能入队。

        直接调 on_log 会去写主窗口的 Text 控件 —— Tk 不是线程安全的，
        macOS 上会直接段错误退出（点「连接设备」后窗口直接消失）。
        """
        self._logq.put(str(msg))

    def _flush_logs(self):
        try:
            while True:
                msg = self._logq.get_nowait()
                if self.on_log:
                    self.on_log(msg, "info")
        except queue.Empty:
            pass

    def _bg(self, work, done):
        """后台干活，回主线程更新界面 —— tkinter 不能跨线程碰控件。"""
        if self._busy:
            self._set_status("上一步还没完成，稍等 …")
            return
        self._busy = True
        self._set_buttons()

        def run():
            try:
                self._q.put((done, work(), None))
            except Exception as exc:          # 网络/驱动异常都收敛到这里
                self._q.put((done, None, exc))

        threading.Thread(target=run, daemon=True).start()

    def _poll(self):
        self._flush_logs()      # 后台线程的日志先落到界面
        try:
            while True:
                done, res, err = self._q.get_nowait()
                self._busy = False
                if err is not None:
                    self._set_buttons()
                    self._fail(err)
                elif done and self._alive:
                    # done 里可能抛异常（截图解码、控件树解析等），
                    # 不能让它冒到 tkinter 主循环里去 —— 那样界面会卡在
                    # 「正在连接」且错误只出现在控制台，等于没有提示。
                    try:
                        done(res)
                    except Exception as exc:
                        self._fail(exc)
                    finally:
                        self._set_buttons()
                else:
                    self._set_buttons()
        except queue.Empty:
            pass
        if self._alive:
            self.after(120, self._poll)

    def _fail(self, err):
        raw = str(err).strip() or err.__class__.__name__
        msg = ui_inspector.friendly_error(raw)
        self._set_status(f"出错：{msg.splitlines()[0][:120]}")
        self._write_error_log(err)
        messagebox.showerror("元素拾取", msg, parent=self)

    def _write_error_log(self, err):
        """把完整异常落盘，弹窗只显示人话，细节留着排查用。"""
        try:
            import traceback

            os.makedirs(LOGS_DIR, exist_ok=True)
            path = os.path.join(LOGS_DIR, "ui_picker_error.log")
            with open(path, "a", encoding="utf-8") as f:
                f.write(
                    f"\n===== {_dt.datetime.now():%Y-%m-%d %H:%M:%S} =====\n"
                    f"{''.join(traceback.format_exception(type(err), err, err.__traceback__))}"
                )
            self._log(f"完整报错已写入 logs/ui_picker_error.log", "warn")
        except Exception:
            pass

    def _set_buttons(self):
        if self.offline:
            try:
                self.conn_btn.configure(text="离线快照", state="disabled")
                for b in (self.refresh_btn, self.up_btn, self.down_btn,
                          self.back_btn, self.act_btn):
                    b.configure(state="disabled")
            except tk.TclError:
                pass
            return

        on = self.inspector is not None and self.inspector.connected
        try:
            self.conn_btn.configure(
                text=("断开设备" if on else "连接设备"),
                state="normal" if (not self._busy or on) else "disabled",
            )
            for b in (self.refresh_btn, self.up_btn, self.down_btn, self.back_btn,
                      self.act_btn):
                b.configure(state="normal" if (on and not self._busy) else "disabled")
        except tk.TclError:
            pass

    # ---------------- 设备操作 ----------------
    def _connect(self):
        if self.inspector is not None and self.inspector.connected:
            self._close_session()
            self._set_buttons()
            self._set_status("已断开设备")
            return

        if not port_open(APPIUM_PORT):
            messagebox.showwarning(
                "Appium 未启动",
                "4723 端口没人监听。\n\n请先点主窗口的「重新检测」拉起 Appium，再回到这里连接。",
                parent=self,
            )
            return

        devices = connected_devices()
        if not devices:
            adb = find_adb()
            raw = adb_devices_raw()
            if not adb:
                messagebox.showerror(
                    "找不到 adb",
                    "系统里找不到 adb 可执行文件，没法判断手机是否连上。\n\n"
                    "两种解决办法：\n"
                    "1. 装好 Android SDK Platform-Tools，并把 platform-tools 加进 PATH\n"
                    "2. 设置环境变量 ANDROID_HOME 指向 SDK 目录",
                    parent=self,
                )
            elif "unauthorized" in raw:
                messagebox.showwarning(
                    "手机未授权",
                    "手机连着，但还没允许这台电脑调试。\n\n"
                    "拔插一次数据线，在手机弹出的「允许 USB 调试吗」里点允许"
                    "（建议勾选「一律允许」）。",
                    parent=self,
                )
            elif "offline" in raw:
                messagebox.showwarning(
                    "设备离线",
                    "adb 看到设备但状态是 offline。\n\n"
                    "拔插数据线，或在手机开发者选项里关掉再打开「USB 调试」。",
                    parent=self,
                )
            else:
                messagebox.showwarning(
                    "没有设备",
                    "adb 没看到在线设备，请检查数据线和 USB 调试。",
                    parent=self,
                )
            return
        udid = devices[0]
        if len(devices) > 1:
            self._log(f"检测到 {len(devices)} 台设备，使用第一台 {udid}")

        inspector = ui_inspector.Inspector(
            udid=udid, port=APPIUM_PORT, log=self._log
        )
        self._set_status(f"正在连接 {udid}，首次建会话要几十秒 …")

        def work():
            try:
                inspector.connect()
                return inspector.capture()
            except Exception:
                # 建会话失败时可能已经在设备上留了半个 session，
                # 不清掉下次连接会一直被它挡住
                inspector.close()
                raise

        def done(snap):
            self.inspector = inspector
            self._show(snap)

        self._bg(work, done)

    def _close_session(self):
        if self.inspector is not None:
            try:
                self.inspector.close()
            except Exception:
                pass
        self.inspector = None

    def _refresh(self):
        if self.inspector is None or not self.inspector.connected:
            return
        self._set_status("正在重新抓取 …")
        self._bg(self.inspector.capture, self._show)

    def _swipe(self, up):
        if self.inspector is None or not self.inspector.connected:
            return

        def work():
            if up:
                self.inspector.swipe_up()
            else:
                self.inspector.swipe_down()
            time.sleep(0.5)
            return self.inspector.capture()

        self._set_status("滑动并重新抓取 …")
        self._bg(work, self._show)

    def _back(self):
        if self.inspector is None or not self.inspector.connected:
            return

        def work():
            self.inspector.press_back()
            time.sleep(0.8)
            return self.inspector.capture()

        self._set_status("按返回键并重新抓取 …")
        self._bg(work, self._show)

    def _activate(self):
        if self.inspector is None or not self.inspector.connected:
            return

        def work():
            self.inspector.activate()
            self.inspector.wait_ready()
            return self.inspector.capture()

        self._set_status("正在把 App 拉到前台 …")
        self._bg(work, self._show)

    # ---------------- 渲染 ----------------
    def _show(self, snap):
        self.snap = snap
        self.node = None
        self.cands = []
        self.tree.delete(*self.tree.get_children())
        self._set_detail("")
        self._set_code("")
        self._photo_full = tk.PhotoImage(data=base64.b64encode(snap.png).decode())
        self._draw()
        if not snap.is_app:
            self._set_status(
                "⚠ 这一屏没有抓到被测 App 的控件（可能是启动画面或系统界面）"
                " · 点「拉起 App」或「刷新」重试"
            )
            return
        act = snap.activity or "未知页面"
        self._set_status(
            f"{act} · 截图 {snap.img_w}×{snap.img_h} · 点左侧截图选中元素，选中后看右侧方案"
        )

    def _draw(self):
        """把截图按画布尺寸整数倍缩小居中 —— 只依赖 PhotoImage，不引 Pillow。"""
        if not self._alive:
            return
        if self._photo_full is None:
            self.canvas.delete("all")
            self.canvas.create_text(
                max(self.canvas.winfo_width(), 60) // 2,
                max(self.canvas.winfo_height(), 60) // 2,
                text="还未抓取屏幕", fill=C_TEXT3,
            )
            return
        cw = max(self.canvas.winfo_width(), 60)
        ch = max(self.canvas.winfo_height(), 60)
        iw, ih = self._photo_full.width(), self._photo_full.height()
        n = max(1, math.ceil(max(iw / cw, ih / ch)))     # 只缩不放
        self._photo_disp = self._photo_full.subsample(n) if n > 1 else self._photo_full
        w, h = self._photo_disp.width(), self._photo_disp.height()
        x, y = (cw - w) // 2, (ch - h) // 2
        self.canvas.delete("all")
        self.canvas.create_image(x, y, image=self._photo_disp, anchor="nw")
        self._img_rect = (x, y, w, h)
        self._redraw_marker()

    def _redraw_marker(self):
        if self.snap is None or self._photo_disp is None:
            return
        self.canvas.delete("marker")
        if self.node is None:
            return
        x0, y0, w, h = self._img_rect
        sx = w / (self.snap.win_w or 1)
        sy = h / (self.snap.win_h or 1)
        bx1, by1, bx2, by2 = self.node.bounds
        self.canvas.create_rectangle(
            x0 + bx1 * sx, y0 + by1 * sy, x0 + bx2 * sx, y0 + by2 * sy,
            outline=C_ERR, width=2, tags="marker",
        )

    def _on_click(self, event):
        if self.snap is None or self._photo_disp is None:
            return
        x0, y0, w, h = self._img_rect
        if not (x0 <= event.x <= x0 + w and y0 <= event.y <= y0 + h):
            return
        ix = (event.x - x0) / w * self.snap.img_w
        iy = (event.y - y0) / h * self.snap.img_h
        node = self.snap.hit(ix, iy, self.prefer_var.get())
        if node is None:
            self._set_status("这个位置没有控件（可能是空白区域）")
            return
        self._select(node)

    def _select(self, node):
        self.node = node
        self.cands = ui_inspector.build_candidates(
            self.snap.root, node, self._existing_keys,
            window=(self.snap.win_w, self.snap.win_h),
        )

        # 已经收录过的元素，直接复用原 key，别在库里造重复别名
        exist = None
        if node.rid:
            exist = self._existing.get(node.rid) or self._existing.get(node.short_id)
        if exist:
            key = exist[0]
            self._taken_keys.add(key)
        else:
            key = ui_inspector.key_for_node(node, self._existing_keys, self._taken_keys)
            self._taken_keys.add(key)
        for c in self.cands:
            c.key = key
        self._exist_hit = exist

        self._render_detail()
        self._render_cands()
        self._redraw_marker()
        rows = self.tree.get_children()
        if rows:
            self.tree.selection_set(rows[0])
            self.tree.focus(rows[0])
            self._on_cand_select()        # 不等事件回调，立刻把代码填上
        else:
            self._set_code("（这个控件没有任何可用属性，只能靠坐标盲点）")

    def _select_parent(self):
        if self.node is None:
            return
        parent = self.node.parent
        while parent is not None and parent.cls in ("", "hierarchy"):
            parent = parent.parent
        if parent is None:
            self._set_status("已经是根节点了")
            return
        self._select(parent)

    def _render_detail(self):
        n = self.node
        if n is None:
            self._set_detail("")
            return
        b = n.bounds
        flags = [x for x, on in (
            ("可点击", n.clickable), ("可用", n.enabled), ("可滚动", n.scrollable),
            ("长按", n.long_clickable), ("密码", n.password), ("选中", n.selected),
        ) if on]
        rows = [
            ("类名", n.cls or "—"),
            ("id", n.rid or "—"),
            ("文案", n.text or "—"),
            ("描述", n.desc or "—"),
            ("位置", f"[{b[0]},{b[1]}][{b[2]},{b[3]}]   {n.wid}×{n.hei}"),
            ("状态", " · ".join(flags) or "—"),
        ]
        exist = getattr(self, "_exist_hit", None)
        if exist:
            rows.append(("已收录", f'locators.py 里叫 "{exist[0]}"，直接用这个 key'))
        elif n.rid:
            rows.append(("已收录", "没有，下面是新建议的 key"))
        text = "\n".join(f"{k:<4}{v}" for k, v in rows)
        self._set_detail(text)

    def _render_cands(self):
        self.tree.delete(*self.tree.get_children())
        for i, c in enumerate(self.cands):
            self.tree.insert(
                "", "end", iid=str(i),
                values=(c.kind, c.count, c.note), tags=(c.level,),
            )

    def _set_detail(self, text):
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", text)
        self.detail.configure(state="disabled")

    def _set_code(self, text):
        self.code.configure(state="normal")
        self.code.delete("1.0", "end")
        self.code.insert("1.0", text)
        self.code.configure(state="disabled")

    def _current_cand(self):
        sel = self.tree.selection()
        if not sel or not self.cands:
            return None
        try:
            return self.cands[int(sel[0])]
        except (ValueError, IndexError):
            return None

    def _on_cand_select(self, _event=None):
        c = self._current_cand()
        if c is None:
            return
        head = (
            "# ① 追加到 locators.py 的 LOCATORS 字典\n"
            f"{c.entry_code}\n\n"
            "# ② 用例里这样用\n"
            f"{c.call_code()}\n"
        )
        if getattr(self, "_exist_hit", None):
            head = (
                f'# 这个控件 locators.py 里已经收录："{c.key}"\n'
                f'LOCATORS["{c.key}"]\n\n'
                f"# 用例里\n"
                f"{c.call_code()}\n\n"
                "# 如果你确实要换一种写法，可粘贴这一行替换原条目：\n"
                f"{c.entry_code}\n"
            )
        self._set_code(head)

    # ---------------- 复制 ----------------
    def _copy(self, what):
        c = self._current_cand()
        if c is None:
            return
        if what == "entry":
            text = c.entry_code.strip()
        else:
            text = self.code.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(text)
        self._set_status(f"已复制：{text.splitlines()[0][:70]}")

    # ---------------- 收尾 ----------------
    def _on_close(self):
        self._alive = False
        self._close_session()
        self.destroy()

    def _center(self, master):
        self.update_idletasks()
        w = self.winfo_reqwidth() or self.winfo_width()
        h = self.winfo_reqheight() or self.winfo_height()
        try:
            mw, mh = master.winfo_width(), master.winfo_height()
            if mw <= 1 or mh <= 1:
                mw, mh = self.winfo_screenwidth(), self.winfo_screenheight()
                mx = my = 0
            else:
                mx, my = master.winfo_rootx(), master.winfo_rooty()
            self.geometry(f"+{max(mx + (mw - w) // 2, 0)}+{max(my + (mh - h) // 3, 0)}")
        except tk.TclError:
            pass


# --------------------------------------------------------------------------
# 通用：窗口居中 / 收掉子进程
# --------------------------------------------------------------------------
def center_on(master, win):
    """把 win 摆到 master 中间偏上（未映射的窗口取 reqwidth）。"""
    win.update_idletasks()
    w = win.winfo_reqwidth() or win.winfo_width()
    h = win.winfo_reqheight() or win.winfo_height()
    try:
        mw, mh = master.winfo_width(), master.winfo_height()
        if mw <= 1 or mh <= 1:
            mw, mh = win.winfo_screenwidth(), win.winfo_screenheight()
            mx = my = 0
        else:
            mx, my = master.winfo_rootx(), master.winfo_rooty()
        win.geometry(f"+{max(mx + (mw - w) // 2, 0)}+{max(my + (mh - h) // 3, 0)}")
    except tk.TclError:
        pass


def kill_process_tree(proc, grace=2.0):
    """收掉一个子进程及其派生进程（工具脚本用，不需要 graceful 收尾）。"""
    if proc is None or proc.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW,
            )
        except Exception:
            proc.terminate()
        return

    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        pgid = None
    same_group = pgid is None or pgid == os.getpgid(0)
    try:
        if same_group:
            proc.terminate()
        else:
            os.killpg(pgid, signal.SIGTERM)
    except OSError:
        return
    try:
        proc.wait(timeout=grace)
    except Exception:
        try:
            if same_group:
                proc.kill()
            else:
                os.killpg(pgid, signal.SIGKILL)
        except Exception:
            pass


# --------------------------------------------------------------------------
# 工具菜单：把 tools/ 下四个命令行脚本包成图形界面
#
# 这些脚本原本都得开终端敲参数；这里只把「常用的那几个参数」做成控件，
# 输出原样贴到窗口里，跑完能一键打开产物目录。
# --------------------------------------------------------------------------
TOOL_SPECS = (
    {
        "name": "抓取控件树",
        "script": "ui_tree_dump.py",
        "desc": "逐页 dump 真实控件树 + 截图到 logs/ui_dump/。\n"
                "需要 Appium 已启动、设备已连接；会自己操作 App 翻页。",
        "fields": [
            {"key": "page", "label": "页面", "kind": "choice",
             "choices": ["home", "edit", "text", "more", "newui", "all"],
             "default": "home"},
        ],
        "args": lambda v: [v["page"]],
        "output": os.path.join(LOGS_DIR, "ui_dump"),
    },
    {
        "name": "生成定位",
        "script": "gen_locators.py",
        "desc": "读 logs/ui_dump/*.xml，生成 logs/ui_dump/generated_locators.py。\n"
                "已在 locators.py 里存在的 selector 默认跳过。",
        "fields": [
            {"key": "report", "label": "只统计，不生成文件（--report）",
             "kind": "flag", "default": False},
        ],
        "args": lambda v: ["--report"] if v["report"] else [],
        "output": os.path.join(LOGS_DIR, "ui_dump"),
    },
    {
        "name": "合并定位",
        "script": "merge_locators.py",
        "desc": "把生成结果并进 locators.py 末尾的「自动抓取」段，写完自动校验语法与重名。\n"
                "建议先勾「只看会加多少条」确认一遍。",
        "fields": [
            {"key": "dry", "label": "只看会加多少条（--dry-run）",
             "kind": "flag", "default": True},
        ],
        "args": lambda v: ["--dry-run"] if v["dry"] else [],
        "output": PROJECT_ROOT,
    },
    {
        "name": "抽样校验定位",
        "script": "verify_locators.py",
        "desc": "把指定 key 在真机上真实找一遍，确认定位没失效。\n"
                "留空则用脚本内置的默认样本；多个 key 用空格分隔。",
        "fields": [
            {"key": "keys", "label": "key（可留空）", "kind": "text", "default": ""},
        ],
        "args": lambda v: v["keys"].split(),
        "output": None,
    },
)


class ScriptDialog(tk.Toplevel):
    """跑一个 tools/ 脚本，实时回显输出。"""

    def __init__(self, master, spec, on_log=None):
        super().__init__(master)
        self.spec = spec
        self.on_log = on_log
        self.proc = None
        self._q = queue.Queue()
        self._alive = True
        self._vars = {}

        self.title(f"工具 · {spec['name']}")
        self.geometry("780x580")
        self.minsize(640, 440)
        self.transient(master)
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())
        center_on(master, self)
        self.after(100, self._poll)

    def _build(self):
        head = ttk.Frame(self, padding=(16, 14, 16, 2))
        head.pack(fill="x")
        tk.Label(
            head, text=self.spec["desc"], background=C_BG, foreground=C_TEXT2,
            font=ui_font(9), justify="left", anchor="w",
        ).pack(fill="x")

        form = ttk.Frame(self, padding=(16, 10, 16, 8))
        form.pack(fill="x")
        for f in self.spec["fields"]:
            row = ttk.Frame(form)
            row.pack(fill="x", pady=2)
            if f["kind"] == "flag":
                # 勾选项的说明就是标签本身，不必再左边空出一大列
                var = tk.BooleanVar(value=f["default"])
                ttk.Checkbutton(row, text=f["label"], variable=var).pack(side="left")
            else:
                ttk.Label(row, text=f["label"], width=12, anchor="w").pack(side="left")
                if f["kind"] == "choice":
                    var = tk.StringVar(value=f["default"])
                    ttk.Combobox(
                        row, textvariable=var, values=f["choices"], width=14,
                        state="readonly",
                    ).pack(side="left")
                else:
                    var = tk.StringVar(value=f["default"])
                    ttk.Entry(row, textvariable=var, width=36).pack(side="left")
            self._vars[f["key"]] = var

        bar = ttk.Frame(self, padding=(16, 4, 16, 8))
        bar.pack(fill="x")
        self.run_btn = ttk.Button(bar, text="▶  运行", width=10,
                                  style="Accent.TButton", command=self._run)
        self.run_btn.pack(side="left")
        self.stop_btn = ttk.Button(
            bar, text="■  停止", width=8, command=self._stop, state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="清空输出", width=10, command=self._clear).pack(
            side="left", padx=(6, 0)
        )
        if self.spec.get("output"):
            ttk.Button(bar, text="打开产物目录", width=12,
                       command=self._open_output).pack(side="right")
        self.stat = ttk.Label(bar, text="就绪", foreground=C_TEXT2)
        self.stat.pack(side="right", padx=(0, 12))

        body = ttk.Frame(self, padding=(16, 6, 16, 14))
        body.pack(fill="both", expand=True)
        self.out = tk.Text(
            body, wrap="none", font=mono_font(9), background=C_LOG_BG,
            foreground=C_LOG_FG, insertbackground=C_LOG_FG, state="disabled",
        )
        vs = ttk.Scrollbar(body, orient="vertical", command=self.out.yview)
        self.out.configure(yscrollcommand=vs.set)
        self.out.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.out.tag_config("err", foreground="#FF8B7E")
        self.out.tag_config("ok", foreground="#7CD79B")
        self.out.tag_config("muted", foreground="#6C7484")

    # ---------------- 运行 ----------------
    def _write(self, text, tag=None):
        self.out.configure(state="normal")
        self.out.insert("end", text + "\n", tag or ())
        self.out.see("end")
        self.out.configure(state="disabled")

    def _clear(self):
        self.out.configure(state="normal")
        self.out.delete("1.0", "end")
        self.out.configure(state="disabled")

    def _run(self):
        if self.proc is not None and self.proc.poll() is None:
            return
        script = os.path.join(TOOLS_DIR, self.spec["script"])
        if not os.path.exists(script):
            messagebox.showwarning("脚本不存在", f"找不到 {script}", parent=self)
            return
        try:
            args = self.spec["args"]({k: v.get() for k, v in self._vars.items()})
        except Exception as exc:
            messagebox.showerror("参数有误", str(exc), parent=self)
            return

        cmd = [VENV_PYTHON, script, *args]
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"
        popen_extra = (
            {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
            if os.name == "nt" else {"start_new_session": True}
        )

        self._write(f"$ {' '.join(cmd)}", "muted")
        try:
            self.proc = subprocess.Popen(
                cmd, cwd=PROJECT_ROOT, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                env=env, **popen_extra,
            )
        except Exception as exc:
            self._write(f"启动失败：{exc}", "err")
            return

        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.stat.configure(text="运行中 …", foreground=C_WARN)
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self):
        try:
            for line in self.proc.stdout:
                self._q.put(("line", line.rstrip("\n")))
        finally:
            code = self.proc.wait()
            self._q.put(("done", code))

    def _poll(self):
        try:
            while True:
                kind, payload = self._q.get_nowait()
                if kind == "line":
                    tag = None
                    low = payload.lower()
                    if "error" in low or "traceback" in low or "失败" in payload:
                        tag = "err"
                    elif payload.startswith("✅") or "ok" in low:
                        tag = "ok"
                    self._write(payload, tag)
                else:
                    self._finish(payload)
        except queue.Empty:
            pass
        if self._alive:
            self.after(100, self._poll)

    def _finish(self, code):
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if code == 0:
            self.stat.configure(text="完成（退出码 0）", foreground=C_OK)
            self._write("— 执行完毕 —", "muted")
        else:
            self.stat.configure(text=f"退出码 {code}", foreground=C_ERR)
            self._write(f"— 结束，退出码 {code} —", "err")

    def _stop(self):
        if self.proc is not None and self.proc.poll() is None:
            self.stat.configure(text="正在停止 …", foreground=C_WARN)
            kill_process_tree(self.proc)

    def _open_output(self):
        path = self.spec.get("output")
        if path:
            os.makedirs(path, exist_ok=True)
            open_in_os(path)

    def _on_close(self):
        self._alive = False
        if self.proc is not None and self.proc.poll() is None:
            kill_process_tree(self.proc)
        self.destroy()


# --------------------------------------------------------------------------
# 环境自检
# --------------------------------------------------------------------------
class EnvCheckDialog(tk.Toplevel):
    """一屏看完「这台机器到底能不能跑」：解释器、依赖、Appium、adb、目录。

    检查项里有多条会起子进程（appium --version / driver list 都要几秒），
    所以逐条后台跑、逐条回填，不是一次性等完再显示。
    """

    LEVEL = {
        "ok": ("✓", C_OK),
        "warn": ("!", C_WARN),
        "bad": ("✗", C_ERR),
        "run": ("…", C_TEXT2),
    }

    def __init__(self, master):
        super().__init__(master)
        self.title("环境自检")
        self.geometry("900x520")
        self.minsize(760, 420)
        self.transient(master)
        self._alive = True
        self._q = queue.Queue()
        self._rows = []
        self._deps = None
        self._details = {}

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())
        center_on(master, self)
        self._start()

    def _build(self):
        head = ttk.Frame(self, padding=(14, 12, 14, 4))
        head.pack(fill="x")
        ttk.Label(
            head,
            text="检查「换机器 / 换手机 / 装完依赖」后最常见的几处坑。"
                 "红色必须修，黄色只是提醒。",
            foreground=C_TEXT2,
        ).pack(anchor="w")

        body = ttk.Frame(self, padding=(14, 6, 14, 4))
        body.pack(fill="both", expand=True)
        cols = ("state", "item", "detail")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", selectmode="browse")
        for cid, title, width, anchor, stretch in (
            ("state", "结果", 52, "center", False),
            ("item", "检查项", 170, "w", False),
            ("detail", "说明", 620, "w", True),
        ):
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=width, anchor=anchor, stretch=stretch)
        vs = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.tree.tag_configure("ok", foreground=C_OK)
        self.tree.tag_configure("warn", foreground=C_WARN)
        self.tree.tag_configure("bad", foreground=C_ERR)
        self.tree.tag_configure("run", foreground=C_TEXT2)

        foot = ttk.Frame(self, padding=(14, 4, 14, 12))
        foot.pack(fill="x")
        ttk.Button(foot, text="重新检查", width=10, command=self._start).pack(side="left")
        ttk.Button(foot, text="复制诊断信息", width=13,
                   command=self._copy).pack(side="left", padx=(6, 0))
        ttk.Button(foot, text="关闭", width=8, command=self._on_close).pack(side="right")
        self.stat = ttk.Label(foot, text="", foreground=C_TEXT2)
        self.stat.pack(side="right", padx=(0, 12))

    # ---------------- 检查项 ----------------
    def _checks(self):
        return [
            ("系统 / Python", self._c_python),
            ("虚拟环境解释器", self._c_venv),
            ("Python 依赖", self._c_deps),
            ("requirements 一致性", self._c_requirements),
            ("Appium 可执行文件", self._c_appium),
            ("Appium 驱动", self._c_drivers),
            ("Appium 服务端口", self._c_port),
            ("adb", self._c_adb),
            ("ANDROID_HOME", self._c_android_home),
            ("日志 / 报告目录", self._c_dirs),
        ]

    def _c_python(self):
        return "ok", "{} · Python {} · Tk {}".format(
            platform.platform(terse=True), platform.python_version(),
            self.tk.call("info", "patchlevel"),
        )

    def _c_venv(self):
        if os.path.exists(VENV_PYTHON):
            size = "（可执行）" if os.access(VENV_PYTHON, os.X_OK) else "（无执行权限）"
            return "ok", f"{VENV_PYTHON} {size}"
        return "bad", (
            f"不存在：{VENV_PYTHON}　→ 换机器后 .venv 必须重建："
            "uv venv && uv pip install -r requirements/requirements.txt"
        )

    def _dep_map(self):
        """把 venv 里的关键依赖版本查出来（只起一次子进程）。"""
        if self._deps is not None:
            return self._deps
        # appium 包没有 __version__，版本只能从 importlib.metadata 拿
        code = (
            "import importlib.metadata as m, pytest, appium, selenium, pytest_html;"
            "print('|'.join([pytest.__version__,"
            " m.version('Appium-Python-Client'),"
            " selenium.__version__, pytest_html.__version__]))"
        )
        try:
            res = subprocess.run(
                [VENV_PYTHON, "-c", code], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=30,
                creationflags=CREATE_NO_WINDOW,
            )
            if res.returncode != 0:
                tail = (res.stderr or "").strip().splitlines()
                self._deps = "导入失败：" + (tail[-1] if tail else f"退出码 {res.returncode}")
                return self._deps
            parts = (res.stdout or "").strip().split("|")
            if len(parts) != 4:
                self._deps = {}
                return self._deps
            self._deps = dict(zip(
                ("pytest", "appium_python_client", "selenium", "pytest_html"), parts
            ))
        except Exception as exc:
            self._deps = f"查询失败：{exc}"
        return self._deps

    def _c_deps(self):
        deps = self._dep_map()
        if isinstance(deps, str):
            return "bad", deps
        if not deps:
            return "bad", "无法读取依赖版本（解释器可能不可用）"
        pretty = {
            "pytest": "pytest", "appium_python_client": "Appium-Python-Client",
            "selenium": "selenium", "pytest_html": "pytest-html",
        }
        return "ok", " · ".join(f"{pretty.get(k, k)} {v}" for k, v in deps.items())

    def _c_requirements(self):
        path = os.path.join(PROJECT_ROOT, "requirements", "requirements.txt")
        if not os.path.exists(path):
            return "warn", "找不到 requirements/requirements.txt"
        deps = self._dep_map()
        pinned = {}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if "==" in line:
                    k, v = line.split("==", 1)
                    pinned[k.strip().lower().replace("-", "_")] = v.strip()
        if not pinned:
            return "warn", "清单里没有锁定版本（==）"
        if not isinstance(deps, dict):
            return "warn", "拿不到实际版本，无法比对"
        diff = [
            f"{k} 清单 {v} / 实际 {deps[k]}"
            for k, v in pinned.items() if k in deps and deps[k] != v
        ]
        if diff:
            return "warn", "与清单不一致：" + "；".join(diff)
        return "ok", f"{len(pinned)} 项锁定版本与实际安装一致"

    def _c_appium(self):
        exe = find_appium()
        if not exe:
            return "bad", "找不到 appium　→ npm install -g appium"
        try:
            res = subprocess.run(
                [exe, "--version"], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=40,
                creationflags=CREATE_NO_WINDOW,
            )
            ver = (res.stdout or res.stderr or "").strip().splitlines()
            ver = ver[-1] if ver else "未知版本"
        except Exception as exc:
            ver = f"查询失败：{exc}"
        return "ok", f"{exe} · {ver}"

    def _c_drivers(self):
        exe = find_appium()
        if not exe:
            return "warn", "没有 appium，跳过"
        try:
            res = subprocess.run(
                [exe, "driver", "list", "--installed"], capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=60,
                creationflags=CREATE_NO_WINDOW,
            )
            out = ((res.stdout or "") + (res.stderr or "")).strip()
        except Exception as exc:
            return "warn", f"查询失败：{exc}"
        if "uiautomator2" not in out:
            return "bad", "没有 uiautomator2 驱动　→ appium driver install uiautomator2"
        names = [ln.strip(" -•\t") for ln in out.splitlines() if "@" in ln]
        return "ok", "；".join(names[:4]) or out.splitlines()[0][:120]

    def _c_port(self):
        if port_open(APPIUM_PORT):
            return "ok", f"{APPIUM_HOST}:{APPIUM_PORT} 已在监听（可直接复用）"
        return "warn", f"{APPIUM_PORT} 无人监听 —— 点「开始运行」时会自动拉起"

    def _c_adb(self):
        adb = find_adb()
        if not adb:
            return "bad", "找不到 adb　→ 装 platform-tools 并加进 PATH，或设 ANDROID_HOME"
        code, out = adb_shell(None, "version", timeout=15)
        # 只留版本号：整行 "Android Debug Bridge version 1.0.41" 太长，
        # 表格列又不换行，末尾真正要紧的「设备在不在线」会被挤出去看不见。
        m = re.search(r"version\s+([\d.]+)", out or "")
        ver = f" v{m.group(1)}" if m else ""
        devs = connected_devices()
        if not devs:
            raw = adb_devices_raw()
            state = "设备未授权（手机上点允许）" if "unauthorized" in raw else "无设备在线"
            return "warn", f"{adb}{ver} · {state}"
        return "ok", f"{adb}{ver} · 在线 {len(devs)} 台"

    def _c_android_home(self):
        home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
        if home and os.path.isdir(home):
            return "ok", home
        if home:
            return "warn", f"设了但目录不存在：{home}"
        return "warn", "未设置 ANDROID_HOME（adb 能找到就还能跑；模拟器/新设备建议设上）"

    def _c_dirs(self):
        bad = []
        for d in (LOGS_DIR, REPORTS_DIR, FAILURES_DIR):
            try:
                os.makedirs(d, exist_ok=True)
                probe = os.path.join(d, ".write_test")
                with open(probe, "w", encoding="utf-8") as f:
                    f.write("ok")
                os.remove(probe)
            except Exception as exc:
                bad.append(f"{d}：{exc}")
        if bad:
            return "bad", "不可写：" + "；".join(bad)
        return "ok", "logs/ reports/ logs/failures 均可写"

    # ---------------- 执行 ----------------
    def _start(self):
        self.tree.delete(*self.tree.get_children())
        self._rows = []
        self._details = {}
        self._deps = None
        for i, (name, _fn) in enumerate(self._checks()):
            iid = f"r{i}"
            self.tree.insert("", "end", iid=iid, values=("…", name, "检查中 …"), tags=("run",))
            self._rows.append(iid)
        self.stat.configure(text="检查中 …")
        self._index = 0
        threading.Thread(target=self._worker, daemon=True).start()
        self.after(80, self._poll)

    def _worker(self):
        checks = self._checks()
        for name, fn in checks:
            try:
                level, detail = fn()
            except Exception as exc:
                level, detail = "bad", f"检查本身出错：{exc}"
            self._q.put((name, level, detail))

    def _poll(self):
        try:
            while True:
                name, level, detail = self._q.get_nowait()
                for iid, (_n, fn) in zip(self._rows, self._checks()):
                    if _n != name:
                        continue
                    mark = self.LEVEL.get(level, ("?", "#666"))[0]
                    self.tree.item(iid, values=(mark, name, detail), tags=(level,))
                    self._details[name] = (level, detail)
                    break
                self.stat.configure(text=f"已完成 {len(self._details)} 项")
        except queue.Empty:
            pass
        if self._alive:
            self.after(120, self._poll)

    def _copy(self):
        if not self._details:
            return
        lines = [
            "===== SUPVAN 自动化测试 · 环境诊断 =====",
            f"生成时间：{_dt.datetime.now():%Y-%m-%d %H:%M:%S}",
            "",
        ]
        for name, (level, detail) in self._details.items():
            lines.append(f"[{self.LEVEL.get(level, ('?',))[0]}] {name}：{detail}")
        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.stat.configure(text="诊断信息已复制到剪贴板")

    def _on_close(self):
        self._alive = False
        self.destroy()


# --------------------------------------------------------------------------
# 运行前预检
# --------------------------------------------------------------------------
class PreflightDialog(tk.Toplevel):
    """点「开始运行」后先过一遍：设备、应用、解释器。

    这些检查 conftest 里也有，但那是**建 session 之后**才报错，
    真机上往往已经等了半分钟。提前在这里做，失败就不用白跑。
    """

    def __init__(self, master, udid, files, on_log=None):
        super().__init__(master)
        self.title("运行前预检")
        self.geometry("720x420")
        self.minsize(600, 360)
        self.transient(master)
        self.resizable(False, False)
        self.udid = udid
        self.files = list(files)
        self.on_log = on_log
        self.result = False
        self._alive = True
        self._q = queue.Queue()
        self._rows = {}
        self._critical_failed = False
        self._pending = 0

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda e: self._cancel())
        center_on(master, self)
        self._start()

    def _build(self):
        head = ttk.Frame(self, padding=(14, 12, 14, 4))
        head.pack(fill="x")
        ttk.Label(
            head,
            text="设备 / 应用 / 解释器先确认一遍，避免等半天才发现跑不了。",
            foreground=C_TEXT2,
        ).pack(anchor="w")

        body = ttk.Frame(self, padding=(14, 6, 14, 4))
        body.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(
            body, columns=("state", "item", "detail"), show="headings", height=7,
            selectmode="browse",
        )
        for cid, title, width, anchor, stretch in (
            ("state", "结果", 52, "center", False),
            ("item", "检查项", 150, "w", False),
            ("detail", "说明", 440, "w", True),
        ):
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=width, anchor=anchor, stretch=stretch)
        self.tree.pack(fill="both", expand=True)
        for lv, color in (("ok", C_OK), ("warn", C_WARN),
                          ("bad", C_ERR), ("run", C_TEXT2)):
            self.tree.tag_configure(lv, foreground=color)

        foot = ttk.Frame(self, padding=(14, 4, 14, 12))
        foot.pack(fill="x")
        self.go_btn = ttk.Button(
            foot, text="▶  开始运行", width=14, style="Accent.TButton",
            command=self._go, state="disabled"
        )
        self.go_btn.pack(side="left")
        ttk.Button(foot, text="重新检查", width=10, command=self._start).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(foot, text="取消", width=8, style="Ghost.TButton",
                   command=self._cancel).pack(side="right")
        self.stat = ttk.Label(foot, text="检查中 …", foreground=C_TEXT2)
        self.stat.pack(side="right", padx=(0, 12))

    # ---------------- 检查 ----------------
    def _checks(self):
        return [
            ("设备连接", True, self._c_device),
            ("被测应用已安装", True, self._c_app),
            ("Appium 服务", False, self._c_appium),
            ("解释器与依赖", True, self._c_runtime),
            ("参数块", False, self._c_params),
        ]

    def _c_device(self):
        devs = connected_devices()
        if not devs:
            raw = adb_devices_raw()
            if "unauthorized" in raw:
                return "bad", "设备未授权：在手机上点「允许 USB 调试」"
            if "offline" in raw:
                return "bad", "设备 offline：拔插数据线或重开 USB 调试"
            return "bad", "没有在线设备"
        if self.udid and self.udid not in devs:
            return "bad", f"预检的设备 {self.udid} 已不在线（当前：{'、'.join(devs)}）"
        return "ok", f"{self.udid or devs[0]}（在线 {len(devs)} 台）"

    def _c_app(self):
        if not self.udid:
            return "warn", "没有设备，跳过"
        code, out = adb_shell(
            self.udid, "shell", "pm", "list", "packages", "com.fhit.app_iprinter",
            timeout=30,
        )
        if code != 0:
            return "warn", f"查询失败：{out.strip()[:120]}"
        if "package:com.fhit.app_iprinter" in out:
            return "ok", "com.fhit.app_iprinter"
        return "bad", "设备上没装被测应用 —— 先手动装，或设 APPIUM_APP 指向 apk"

    def _c_appium(self):
        if port_open(APPIUM_PORT):
            return "ok", f"{APPIUM_HOST}:{APPIUM_PORT} 已在运行"
        if not find_appium():
            return "warn", "端口未开且找不到 appium 可执行文件，运行时拉不起来"
        return "warn", "端口未开 —— 运行时会自动拉起（要多等十几秒）"

    def _c_runtime(self):
        ok, detail = probe_runtime()
        return ("ok" if ok else "bad"), detail.replace("\n", " ")

    def _c_params(self):
        missing = [n for n in self.files if not param_editor.has_block(n)]
        if missing:
            return "warn", "读不到参数块：" + "、".join(missing) + "（运行前会被强制确认）"
        return "ok", "、".join(self.files) or "无"

    def _start(self):
        self.tree.delete(*self.tree.get_children())
        self._rows = {}
        self._critical_failed = False
        checks = self._checks()
        self._pending = len(checks)
        for i, (name, _crit, _fn) in enumerate(checks):
            iid = f"r{i}"
            self.tree.insert("", "end", iid=iid, values=("…", name, "检查中 …"),
                             tags=("run",))
            self._rows[name] = iid
        self.go_btn.configure(state="disabled")
        self.stat.configure(text="检查中 …")
        threading.Thread(target=self._worker, args=(checks,), daemon=True).start()
        self.after(80, self._poll)

    def _worker(self, checks):
        for name, critical, fn in checks:
            try:
                level, detail = fn()
            except Exception as exc:
                level, detail = "bad", f"检查出错：{exc}"
            self._q.put((name, critical, level, detail))

    def _poll(self):
        try:
            while True:
                name, critical, level, detail = self._q.get_nowait()
                mark = {"ok": "✓", "warn": "!", "bad": "✗"}.get(level, "?")
                self.tree.item(self._rows[name], values=(mark, name, detail), tags=(level,))
                if level == "bad" and critical:
                    self._critical_failed = True
                self._pending -= 1
                if self._pending <= 0:
                    self._done()
        except queue.Empty:
            pass
        if self._alive:
            self.after(120, self._poll)

    def _done(self):
        if self._critical_failed:
            self.stat.configure(text="有必须修复的问题，无法开始", foreground=C_ERR)
            self.go_btn.configure(state="disabled")
        else:
            self.stat.configure(text="预检通过", foreground=C_OK)
            self.go_btn.configure(state="normal")

    def _go(self):
        self.result = True
        self._alive = False
        self.destroy()

    def _cancel(self):
        self.result = False
        self._alive = False
        self.destroy()


# --------------------------------------------------------------------------
# 失败现场
# --------------------------------------------------------------------------
class FailureDialog(tk.Toplevel):
    """列 logs/failures 下的每次失败，点开可在「元素拾取」里离线复盘那一屏。

    conftest 在用例失败时会存截图 + page_source + meta.json；真机早就翻页了，
    这些文件还在，等于把失败那一刻冻住。
    """

    def __init__(self, master, on_log=None):
        super().__init__(master)
        self.on_log = on_log
        self.title("失败现场")
        self.geometry("820x460")
        self.minsize(680, 380)
        self.transient(master)
        self.records = load_failure_records()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda e: self.destroy())
        center_on(master, self)

    def _build(self):
        head = ttk.Frame(self, padding=(14, 12, 14, 4))
        head.pack(fill="x")
        ttk.Label(
            head,
            text="双击一条 → 用当时的截图 + 控件树离线打开（不连设备）。",
            foreground=C_TEXT2,
        ).pack(anchor="w")

        body = ttk.Frame(self, padding=(14, 6, 14, 4))
        body.pack(fill="both", expand=True)
        cols = ("time", "case", "device", "folder")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", selectmode="browse")
        for cid, title, width, anchor, stretch in (
            ("time", "时间", 130, "w", False),
            ("case", "用例", 260, "w", True),
            ("device", "设备", 130, "w", False),
            ("folder", "目录", 240, "w", False),
        ):
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=width, anchor=anchor, stretch=stretch)
        vs = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._open_picker())

        if not self.records:
            # 空表就是一大块白板，容易让人以为窗口没加载出来
            tk.Label(
                body, text="还没有失败记录\n用例失败时会自动留一份截图 + 控件树",
                background=C_SURFACE, foreground=C_TEXT3, font=ui_font(10),
                justify="center",
            ).place(relx=0.5, rely=0.45, anchor="center")

        self._index = {}
        for i, m in enumerate(self.records):
            iid = f"f{i}"
            self._index[iid] = m
            self.tree.insert(
                "", "end", iid=iid,
                values=(
                    m.get("time", "")[:19].replace("T", " "),
                    m.get("nodeid", m.get("test", "?")),
                    m.get("udid", ""),
                    os.path.basename(m.get("folder", "")),
                ),
            )

        foot = ttk.Frame(self, padding=(14, 4, 14, 12))
        foot.pack(fill="x")
        ttk.Button(foot, text="在元素拾取中打开", width=16,
                   command=self._open_picker).pack(side="left")
        ttk.Button(foot, text="打开文件夹", width=11,
                   command=self._open_folder).pack(side="left", padx=(6, 0))
        ttk.Button(foot, text="关闭", width=8, command=self.destroy).pack(side="right")
        self.stat = ttk.Label(
            foot, text=f"共 {len(self.records)} 条失败记录", foreground=C_TEXT2
        )
        self.stat.pack(side="right", padx=(0, 12))

    def _current(self):
        sel = self.tree.selection()
        if not sel:
            self.stat.configure(text="先选一条（双击也行）")
            return None
        return self._index.get(sel[0])

    def _open_picker(self):
        meta = self._current()
        if not meta:
            return
        win = ElementPicker(self.master, on_log=self.on_log, offline=meta)
        win.lift()

    def _open_folder(self):
        meta = self._current()
        if meta:
            open_in_os(meta["folder"])


# --------------------------------------------------------------------------
# 主界面
# --------------------------------------------------------------------------
class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.queue = queue.Queue()
        self.appium = AppiumManager(self._log_threadsafe)
        self.runner = PytestRunner(self.queue)

        self._state = {}      # iid -> bool（是否勾选）
        self._labels = {}     # iid -> 显示文本
        self._files = []      # 文件节点顺序
        self._children = {}   # 文件 iid -> [用例 iid, ...]
        self._expanded = set()  # 已展开的文件 iid
        self._last_report = None
        self._running = False
        self._stopped_by_user = False
        self._picker = None       # 元素拾取窗口（单实例）

        # —— 本轮新增：运行结果 / 日志缓存 / 筛选 ——
        self.pytest_out = PytestOutput()   # 边跑边解析输出
        self._status = {}                  # iid -> PASSED/FAILED/SKIPPED/RUNNING
        self._run_iids = []                # 本次实际要跑的用例（按列表顺序）
        self._run_start = None
        self._log_lines = []               # [(文本, 级别)]，过滤/搜索时重绘用
        self.log_font_size = 9
        self._jump_seq = 0                 # 「跳到失败」循环指针
        self._summary = ""

        self._build_ui()
        self._load_cases()
        self._refresh_env()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.after(80, self._drain_queue)

    def _quit(self):
        """关主窗口前顺手收掉拾取窗口的 Appium session，别把设备占着。"""
        if self._picker is not None:
            try:
                if self._picker.winfo_exists():
                    self._picker._on_close()
            except tk.TclError:
                pass
        self.root.destroy()

    def _build_menu(self):
        """菜单栏：把 tools/ 下的脚本和几个散落的入口收进来。"""
        menubar = tk.Menu(self.root)

        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="打开报告目录", command=self._open_reports)
        m_file.add_command(label="打开日志目录", command=lambda: open_in_os(LOGS_DIR))
        m_file.add_command(label="失败现场…", command=self._open_failures)
        m_file.add_separator()
        m_file.add_command(label="退出", command=self._quit)
        menubar.add_cascade(label="文件", menu=m_file)

        m_tool = tk.Menu(menubar, tearoff=0)
        for spec in TOOL_SPECS:
            m_tool.add_command(
                label=spec["name"], command=lambda s=spec: self._run_tool(s)
            )
        m_tool.add_separator()
        m_tool.add_command(label="环境自检…", command=self._open_env_check)
        menubar.add_cascade(label="工具", menu=m_tool)

        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="关于", command=self._about)
        menubar.add_cascade(label="帮助", menu=m_help)

        self.root.config(menu=menubar)

    def _about(self):
        messagebox.showinfo(
            "关于",
            "SUPVAN 自动化测试管理工具\n\n"
            "· 勾选用例 → 确认参数 → 预检 → 运行，日志与结果实时回显\n"
            "· 顶部「元素拾取 / 元素定位」找定位，菜单「工具」跑抓取类脚本\n"
            "· 失败会在 logs/failures/ 留一份截图 + 控件树，可离线复盘\n\n"
            f"项目：{PROJECT_ROOT}",
        )

    # ---------------- 界面搭建 ----------------
    # ---------------- 界面搭建 ----------------
    def _card(self, parent):
        """白底卡片：1px 描边 + 白底，替代原来灰扑扑、标题还看不清的 LabelFrame。"""
        return tk.Frame(
            parent, background=C_SURFACE,
            highlightbackground=C_BORDER, highlightthickness=1, bd=0,
        )

    def _card_head(self, card, title):
        """卡片头部：标题 + 右侧插槽，下面压一条 1px 分隔线。"""
        head = tk.Frame(card, background=C_SURFACE)
        head.pack(fill="x", padx=14, pady=(11, 10))
        tk.Label(
            head, text=title, background=C_SURFACE, foreground=C_TEXT,
            font=ui_font(11, True),
        ).pack(side="left")
        slot = tk.Frame(head, background=C_SURFACE)
        slot.pack(side="right")
        tk.Frame(card, background=C_BORDER, height=1).pack(fill="x")
        return head, slot

    def _placeholder(self, entry, var, text):
        """给 ttk.Entry 加一条灰色占位提示（Tk 没有原生 placeholder）。"""
        hint = tk.Label(
            entry, text=text, background=C_SURFACE, foreground=C_TEXT3,
            font=ui_font(9), cursor="xterm",
        )
        hint.place(x=9, rely=0.5, anchor="w")
        hint.bind("<Button-1>", lambda e: entry.focus_set())

        def sync(*_):
            if var.get():
                hint.place_forget()
            else:
                hint.place(x=9, rely=0.5, anchor="w")

        var.trace_add("write", sync)

    def _build_ui(self):
        self.root.title("SUPVAN 自动化测试")
        self.root.configure(background=C_BG)
        self.root.geometry("1180x790")
        self.root.minsize(1040, 660)

        resolve_fonts(self.root)
        apply_theme(self.root)
        self._build_menu()

        # ==================== 顶栏：品牌 + 工具按钮 ====================
        header = tk.Frame(self.root, background=C_SURFACE)
        header.pack(fill="x")
        bar = tk.Frame(header, background=C_SURFACE)
        bar.pack(fill="x", padx=16, pady=10)

        logo = tk.Canvas(
            bar, width=32, height=32, background=C_SURFACE,
            highlightthickness=0, bd=0,
        )
        _round_rect(logo, 1, 1, 31, 31, 9, fill=C_PRIMARY, outline="")
        logo.create_text(16, 16, text="S", fill="#FFFFFF", font=ui_font(15, True))
        logo.pack(side="left")

        brand = tk.Frame(bar, background=C_SURFACE)
        brand.pack(side="left", padx=(10, 0))
        tk.Label(
            brand, text="SUPVAN 自动化测试", background=C_SURFACE,
            foreground=C_TEXT, font=ui_font(13, True),
        ).pack(anchor="w")
        tk.Label(
            brand, text="Appium 真机用例执行台", background=C_SURFACE,
            foreground=C_TEXT3, font=ui_font(9),
        ).pack(anchor="w")

        def head_btn(text, cmd, style="TButton"):
            b = ttk.Button(bar, text=text, command=cmd, style=style)
            b.pack(side="right", padx=(7, 0))
            return b

        # 从右往左 pack：重新检测 | 环境自检 | 测试参数 ‖ 元素定位 | 元素拾取
        head_btn("重新检测", self._refresh_env)
        head_btn("环境自检", self._open_env_check)
        head_btn("测试参数", self._open_params)
        tk.Frame(bar, background=C_BORDER, width=1, height=20).pack(
            side="right", padx=(14, 7)
        )
        head_btn("元素定位", self._open_locators)
        head_btn("元素拾取", self._open_picker)

        tk.Frame(self.root, background=C_BORDER, height=1).pack(fill="x")

        # ==================== 状态条 ====================
        strip = tk.Frame(self.root, background=C_BG)
        strip.pack(fill="x", padx=16, pady=(9, 0))

        self.appium_dot = tk.Label(
            strip, text="\u25CF", background=C_BG, foreground=C_TEXT3,
            font=ui_font(8),
        )
        self.appium_dot.pack(side="left")
        self.appium_label = tk.Label(
            strip, text="Appium 检测中 …", background=C_BG,
            foreground=C_TEXT2, font=ui_font(10),
        )
        self.appium_label.pack(side="left", padx=(5, 0))

        tk.Frame(strip, background=C_BORDER2, width=1, height=12).pack(
            side="left", padx=14
        )

        self.device_dot = tk.Label(
            strip, text="\u25CF", background=C_BG, foreground=C_TEXT3,
            font=ui_font(8),
        )
        self.device_dot.pack(side="left")
        self.device_label = tk.Label(
            strip, text="设备检测中 …", background=C_BG,
            foreground=C_TEXT2, font=ui_font(10),
        )
        self.device_label.pack(side="left", padx=(5, 0))

        # ==================== 主体：左右两栏 ====================
        body = tk.Frame(self.root, background=C_BG)
        body.pack(fill="both", expand=True, padx=16, pady=(9, 0))

        pane = ttk.Panedwindow(body, orient="horizontal")
        pane.pack(fill="both", expand=True)
        left = self._card(pane)
        right = self._card(pane)
        pane.add(left, weight=2)
        pane.add(right, weight=3)

        # ---------- 左：用例列表 ----------
        lhead, lslot = self._card_head(left, "测试脚本")
        self.sel_label = tk.Label(
            lslot, text="已选 0 项", background=C_SURFACE,
            foreground=C_TEXT3, font=ui_font(9),
        )
        self.sel_label.pack(side="right", padx=(10, 0))
        ttk.Button(
            lslot, text="反选", width=5, style="Ghost.TButton", command=self._invert
        ).pack(side="right", padx=(6, 0))
        ttk.Button(
            lslot, text="全选", width=5, style="Ghost.TButton",
            command=lambda: self._set_all(True),
        ).pack(side="right")

        ltool = tk.Frame(left, background=C_SURFACE)
        ltool.pack(fill="x", padx=14, pady=(10, 8))
        self.list_search = tk.StringVar()
        entry = ttk.Entry(ltool, textvariable=self.list_search, width=6)
        entry.pack(side="left", fill="x", expand=True)
        self._placeholder(entry, self.list_search, "搜索用例名 …")
        entry.bind("<KeyRelease>", lambda e: self._rebuild_rows())
        entry.bind("<Escape>", lambda e: self._clear_list_search())
        ttk.Button(
            ltool, text="×", width=3, style="Ghost.TButton",
            command=self._clear_list_search,
        ).pack(side="left", padx=(6, 0))
        self.list_filter = tk.StringVar(value="全部")
        combo = ttk.Combobox(
            ltool, textvariable=self.list_filter, width=6, state="readonly",
            values=("全部", "已勾选", "仅失败"),
        )
        combo.pack(side="left", padx=(6, 0))
        combo.bind("<<ComboboxSelected>>", lambda e: self._rebuild_rows())
        self.expand_btn = ttk.Button(
            ltool, text="展开", width=6, style="Ghost.TButton",
            command=self._toggle_expand_all,
        )
        self.expand_btn.pack(side="left", padx=(6, 0))

        self.rows_canvas = tk.Canvas(
            left, background=ROW_BG, highlightthickness=0, bd=0,
        )
        vs = ttk.Scrollbar(
            left, orient="vertical", style="Vertical.TScrollbar",
            command=self.rows_canvas.yview,
        )
        self.rows_canvas.configure(yscrollcommand=vs.set)
        self.rows_canvas.pack(side="left", fill="both", expand=True, pady=(0, 10))
        vs.pack(side="right", fill="y", padx=(0, 8), pady=(0, 10))

        self.rows_inner = tk.Frame(self.rows_canvas, background=ROW_BG)
        self._inner_id = self.rows_canvas.create_window(
            (0, 0), window=self.rows_inner, anchor="nw"
        )
        self.rows_canvas.bind("<Configure>", self._on_canvas_resize)
        self.rows_canvas.bind_all("<MouseWheel>", self._on_wheel)

        # ---------- 右：运行日志 ----------
        rhead, rslot = self._card_head(right, "运行日志")
        ttk.Button(
            rslot, text="清空", width=5, style="Ghost.TButton",
            command=self._clear_log,
        ).pack(side="right", padx=(6, 0))
        ttk.Button(
            rslot, text="导出", width=5, style="Ghost.TButton",
            command=self._export_log,
        ).pack(side="right")
        ttk.Button(
            rslot, text="A+", width=3, style="Ghost.TButton",
            command=lambda: self._zoom_log(1),
        ).pack(side="right", padx=(6, 0))
        ttk.Button(
            rslot, text="A-", width=3, style="Ghost.TButton",
            command=lambda: self._zoom_log(-1),
        ).pack(side="right")

        rtool = tk.Frame(right, background=C_SURFACE)
        rtool.pack(fill="x", padx=14, pady=(10, 8))
        self.log_search = tk.StringVar()
        lentry = ttk.Entry(rtool, textvariable=self.log_search, width=6)
        lentry.pack(side="left", fill="x", expand=True)
        self._placeholder(lentry, self.log_search, "过滤日志关键字 …")
        lentry.bind("<KeyRelease>", lambda e: self._render_log())
        self.log_level = tk.StringVar(value="全部")
        lcombo = ttk.Combobox(
            rtool, textvariable=self.log_level, width=11, state="readonly",
            values=("全部", "错误与警告", "仅错误", "仅用例结果"),
        )
        lcombo.pack(side="left", padx=(6, 0))
        lcombo.bind("<<ComboboxSelected>>", lambda e: self._render_log())
        self.log_auto = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            rtool, text="自动滚动", variable=self.log_auto,
            style="Surface.TCheckbutton",
        ).pack(side="left", padx=(12, 0))

        logwrap = tk.Frame(right, background=C_SURFACE)
        logwrap.pack(fill="both", expand=True, padx=13, pady=(0, 13))
        self.log_text = tk.Text(
            logwrap,
            wrap="none",
            font=mono_font(self.log_font_size),
            background=C_LOG_BG,
            foreground=C_LOG_FG,
            insertbackground=C_LOG_FG,
            selectbackground="#2F4A7A",
            selectforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#23262E",
            padx=10,
            pady=8,
            state="disabled",
        )
        ls = ttk.Scrollbar(
            logwrap, orient="vertical", style="Vertical.TScrollbar",
            command=self.log_text.yview,
        )
        self.log_text.configure(yscrollcommand=ls.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        ls.pack(side="right", fill="y")

        self.log_text.tag_config("err", foreground="#FF8B7E")
        self.log_text.tag_config("warn", foreground="#E8C56A")
        self.log_text.tag_config("ok", foreground="#7CD79B")
        self.log_text.tag_config("info", foreground=C_LOG_FG)
        self.log_text.tag_config("muted", foreground="#6C7484")
        self.log_text.tag_config("hit", background="#4A3A00", foreground="#FFD75F")
        self.log_text.tag_config("jump", background="#2C4A34")

        # ==================== 底栏：进度 + 操作 ====================
        foot = tk.Frame(self.root, background=C_SURFACE)
        # before=body：底栏优先占位，否则窗口压矮时它会被 expand 的主体挤掉
        foot.pack(fill="x", side="bottom", before=body)
        # 进度条自己画：ttk.Progressbar 在 clam 下的高度被主题写死（18px），
        # 想做成压在底栏顶边的一条细线只能手绘两个 Frame。
        self.prog_var = tk.DoubleVar(value=0)
        self.prog_var.trace_add("write", lambda *a: self._paint_progress())
        self.prog_track = tk.Frame(foot, background="#E7E9EE", height=3, bd=0)
        self.prog_track.pack(fill="x")
        self.prog_track.pack_propagate(False)
        self.prog_fill = tk.Frame(self.prog_track, background=C_PRIMARY, bd=0)
        self.prog_fill.place(x=0, y=0, relheight=1, relwidth=0)

        finner = tk.Frame(foot, background=C_SURFACE)
        finner.pack(fill="x", padx=16, pady=(9, 12))

        row_a = tk.Frame(finner, background=C_SURFACE)
        row_a.pack(fill="x")
        self.prog_label = tk.Label(
            row_a, text="未运行", background=C_SURFACE, foreground=C_TEXT3,
            font=ui_font(9),
        )
        self.prog_label.pack(side="left")
        ttk.Button(
            row_a, text="跳到失败", style="Ghost.TButton",
            command=self._jump_failure,
        ).pack(side="right")
        self.fail_btn = ttk.Button(
            row_a, text="失败现场", style="Ghost.TButton",
            command=self._open_failures,
        )
        self.fail_btn.pack(side="right", padx=(0, 6))

        row_b = tk.Frame(finner, background=C_SURFACE)
        row_b.pack(fill="x", pady=(10, 0))

        self.run_btn = ttk.Button(
            row_b, text="▶  开始运行", style="Accent.TButton", command=self._on_run
        )
        self.run_btn.pack(side="left")
        self.stop_btn = ttk.Button(
            row_b, text="■  停止", style="Danger.TButton",
            command=self._on_stop, state="disabled",
        )
        self.stop_btn.pack(side="left", padx=(8, 0))
        self.report_btn = ttk.Button(
            row_b, text="查看最新报告", command=self._open_last_report,
            state="disabled",
        )
        self.report_btn.pack(side="left", padx=(8, 0))

        self.maxfail_var = tk.BooleanVar(value=False)
        self.html_var = tk.BooleanVar(value=True)
        self.ask_params_var = tk.BooleanVar(value=True)
        self.preflight_var = tk.BooleanVar(value=True)
        for text, var in (
            ("首错即停", self.maxfail_var),
            ("生成 HTML 报告", self.html_var),
            ("运行前确认参数", self.ask_params_var),
            ("运行前预检", self.preflight_var),
        ):
            ttk.Checkbutton(
                row_b, text=text, variable=var, style="Surface.TCheckbutton",
            ).pack(side="right", padx=(14, 0))

    # ---------------- 用例列表 ----------------
    def _load_cases(self):
        self._state.clear()
        self._labels.clear()
        self._files.clear()
        self._children.clear()
        self._expanded.clear()

        cases = discover_cases()
        if not cases:
            self._log(
                "testcases/ 下没有找到 test_*.py，请确认用例命名符合 pytest.ini 规则。",
                "warn",
            )
            self._rebuild_rows()
            return

        for fname, funcs in cases:
            self._labels[fname] = f"{fname}    {len(funcs)} 条"
            self._state[fname] = False
            self._files.append(fname)
            self._children[fname] = []
            for fn in funcs:
                cid = f"{fname}::{fn}"
                self._labels[cid] = fn
                self._state[cid] = False
                self._children[fname].append(cid)

        self._rebuild_rows()
        total = sum(len(f) for _, f in cases)
        self._log(
            f"已识别 {len(cases)} 个用例文件、{total} 条用例（与 pytest 收集规则一致）。",
            "info",
        )
        self._update_sel_label()

    def _rebuild_rows(self):
        """全量重绘可见行 —— 节点统共几十个，重绘成本远低于维护增量状态的复杂度。"""
        keep = self.rows_canvas.yview()[0]   # 保住滚动位置，否则勾选一下会跳回顶部
        for child in self.rows_inner.winfo_children():
            child.destroy()

        # 有筛选条件时一律展开：命中的用例被折在文件里等于没筛
        auto_expand = bool(self._list_keyword()) or self.list_filter.get() != "全部"
        shown = 0
        for fid in self._files:
            kids = [c for c in self._children.get(fid, []) if self._row_visible(c, False)]
            file_ok = self._row_visible(fid, True)
            if not file_ok and not kids:
                continue
            self._make_row(fid, depth=0)
            shown += 1
            if fid in self._expanded or auto_expand:
                for cid in kids:
                    self._make_row(cid, depth=1)
                    shown += 1

        if not shown:
            tk.Label(
                self.rows_inner, text="没有匹配的用例", background=ROW_BG,
                foreground=C_TEXT3, pady=16,
            ).pack(fill="x")

        self.rows_inner.update_idletasks()
        self.rows_canvas.configure(scrollregion=self.rows_canvas.bbox("all"))
        self.rows_canvas.yview_moveto(keep)

    def _list_keyword(self):
        return self.list_search.get().strip().lower()

    def _row_visible(self, iid, is_file):
        """筛选用：文件行只要有一个子用例命中就显示（否则找不到父节点）。"""
        kw = self._list_keyword()
        mode = self.list_filter.get()
        label = self._labels.get(iid, iid).lower()
        kids = self._children.get(iid, [])

        if is_file:
            if mode == "仅失败" and not any(
                self._status.get(c) in ("FAILED", "ERROR") for c in kids
            ):
                return False
            if mode == "已勾选" and not (
                self._state.get(iid) or any(self._state.get(c) for c in kids)
            ):
                return False
            if kw and kw not in label and not any(
                kw in self._labels.get(c, "").lower() for c in kids
            ):
                return False
            return True

        if mode == "仅失败" and self._status.get(iid) not in ("FAILED", "ERROR"):
            return False
        if mode == "已勾选" and not self._state.get(iid):
            return False
        if kw and kw not in label:
            return False
        return True

    def _clear_list_search(self):
        self.list_search.set("")
        self._rebuild_rows()

    def _toggle_expand_all(self):
        if self._expanded:
            self._expanded.clear()
            self.expand_btn.configure(text="展开")
        else:
            self._expanded.update(self._files)
            self.expand_btn.configure(text="收起")
        self._rebuild_rows()

    def _file_status(self, fid):
        """文件行的状态取子用例的汇总：有失败就红，全过才绿。"""
        states = [self._status.get(c) for c in self._children.get(fid, [])]
        if any(s in ("FAILED", "ERROR") for s in states):
            return "FAILED"
        if any(s == "RUNNING" for s in states):
            return "RUNNING"
        if states and all(s in ("PASSED", "SKIPPED") for s in states):
            return "PASSED"
        return None

    def _make_row(self, iid, depth):
        is_file = depth == 0
        has_kids = bool(self._children.get(iid))
        checked = self._state.get(iid, False)
        expanded = iid in self._expanded

        row = tk.Frame(self.rows_inner, background=ROW_BG, height=ROW_H)
        row.pack(fill="x")
        row.pack_propagate(False)   # 高度写死，行内控件垂直居中

        cells = [row]

        if depth:
            pad = tk.Frame(row, width=INDENT_PX, background=ROW_BG)
            pad.pack(side="left", fill="y")
            cells.append(pad)

        # 展开三角：只有文件行有；点它只负责展开 / 收起，不碰勾选状态
        arrow = tk.Label(
            row,
            text=("\u25BE" if expanded else "\u25B8") if has_kids else "",
            font=ui_font(ARROW_SIZE),
            width=2,
            background=ROW_BG,
            foreground=C_TEXT3,
            cursor="hand2" if has_kids else "",
            pady=ROW_PADY,
        )
        arrow.pack(side="left", padx=(14 if is_file else 6, 4))
        cells.append(arrow)

        # 勾选框：系统复选框的字号改不了，这里用 Canvas 自绘一个 16px 方框。
        # 勾选态是实心主色 + 白色对勾，未选是白底浅描边。
        # 注意别用平滑多边形的 outline 画圆角：Tk 不做抗锯齿，1px 的曲线会断成虚线。
        box = tk.Canvas(
            row, width=17, height=17, background=ROW_BG,
            highlightthickness=0, bd=0, cursor="hand2",
        )
        if checked:
            box.create_rectangle(1, 1, 16, 16, fill=C_PRIMARY, outline=C_PRIMARY)
            box.create_line(
                4.6, 8.9, 7.3, 11.7, 12.4, 5.9,
                fill="#FFFFFF", width=2, capstyle="round", joinstyle="round",
            )
        else:
            box.create_rectangle(1, 1, 16, 16, fill=C_SURFACE, outline=C_BORDER2)
        box.pack(side="left", pady=ROW_PADY)
        cells.append(box)

        # 结果标记（空着也占位，保证各行文字左对齐）
        status = self._file_status(iid) if is_file else self._status.get(iid)
        mark, color = STATUS_STYLE.get(status, ("", C_TEXT3))
        badge = tk.Label(
            row, text=mark, width=2, font=ui_font(9), background=ROW_BG,
            foreground=color, pady=ROW_PADY,
        )
        badge.pack(side="left", padx=(4, 0))
        cells.append(badge)

        label = tk.Label(
            row,
            text=self._labels.get(iid, iid),
            anchor="w",
            font=ui_font(10, True) if is_file else ui_font(9),
            background=ROW_BG,
            foreground=C_TEXT if is_file else C_TEXT2,
            cursor="hand2",
            pady=ROW_PADY,
        )
        label.pack(side="left", fill="x", expand=True, padx=(2, 12))
        cells.append(label)

        # 悬停高亮：让「这一行可以点」这件事有反馈
        def _hover(on):
            bg = C_ROW_HOVER if on else ROW_BG
            for w in cells:
                try:
                    w.configure(background=bg)
                except tk.TclError:
                    pass

        for w in cells:
            w.bind("<Enter>", lambda e: _hover(True))
            w.bind("<Leave>", lambda e: _hover(False))

        if has_kids:
            arrow.bind("<Button-1>", lambda e, i=iid: self._toggle_expand(i))
        for widget in (row, box, badge, label):
            widget.bind("<Button-1>", lambda e, i=iid: self._toggle_check(i))

    def _toggle_expand(self, iid):
        if iid in self._expanded:
            self._expanded.discard(iid)
        else:
            self._expanded.add(iid)
        self._rebuild_rows()

    def _toggle_check(self, iid):
        new = not self._state.get(iid, False)
        self._state[iid] = new

        children = self._children.get(iid)
        if children:                       # 文件行 → 级联到全部子用例
            for cid in children:
                self._state[cid] = new
        else:                              # 用例行 → 回算父行状态（全勾才算勾）
            parent = iid.split("::", 1)[0]
            siblings = self._children.get(parent, [])
            if siblings:
                self._state[parent] = all(self._state.get(s) for s in siblings)

        self._rebuild_rows()
        self._update_sel_label()

    def _set_all(self, value):
        for iid in list(self._state):
            self._state[iid] = value
        self._rebuild_rows()
        self._update_sel_label()

    def _invert(self):
        for iid in list(self._state):
            self._state[iid] = not self._state[iid]
        # 反选后父行状态可能和子行不一致，统一由子行重新推导
        for fid in self._files:
            kids = self._children.get(fid, [])
            if kids:
                self._state[fid] = all(self._state.get(c) for c in kids)
        self._rebuild_rows()
        self._update_sel_label()

    def _collect_targets(self):
        targets = []
        for fid in self._files:
            if self._state.get(fid):
                targets.append(f"testcases/{fid}")
                continue
            for cid in self._children.get(fid, []):
                if self._state.get(cid):
                    fname, fn = cid.split("::", 1)
                    targets.append(f"testcases/{fname}::{fn}")
        return targets

    def _on_canvas_resize(self, event):
        self.rows_canvas.itemconfigure(self._inner_id, width=event.width)

    def _on_wheel(self, event):
        """滚轮只在指针位于列表区时生效，不去干扰右侧日志的滚动。"""
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if widget is self.rows_canvas or widget is self.rows_inner:
                steps = wheel_steps(event)
                if steps:
                    self.rows_canvas.yview_scroll(steps, "units")
                return
            widget = getattr(widget, "master", None)

    def _selected_case_iids(self):
        """把勾选展开成「用例粒度」的列表，顺序与列表显示一致（pytest 也按这个顺序跑）。"""
        out = []
        for fid in self._files:
            kids = self._children.get(fid, [])
            if self._state.get(fid):
                out.extend(kids)
            else:
                out.extend(c for c in kids if self._state.get(c))
        return out

    def _update_sel_label(self):
        n = len(self._collect_targets())
        passed = sum(1 for s in self._status.values() if s == "PASSED")
        failed = sum(1 for s in self._status.values() if s in ("FAILED", "ERROR"))
        extra = f"　✓{passed} ✗{failed}" if (passed or failed) else ""
        self.sel_label.configure(text=f"已选 {n} 项{extra}")

    # ---------------- 环境状态 ----------------
    def _refresh_env(self):
        def work():
            if port_open(APPIUM_PORT):
                self._log_threadsafe(
                    f"Appium：运行中（{APPIUM_HOST}:{APPIUM_PORT}）", "ok", target="appium"
                )
            else:
                self._log_threadsafe(
                    f"Appium：未启动（运行测试时会自动拉起）", "warn", target="appium"
                )
            devs = connected_devices()
            if not find_adb():
                text = "找不到 adb（platform-tools 不在 PATH）"
                level = "err"
            elif len(devs) == 1:
                text = f"{devs[0]}（执行时用这台）"
                level = "ok"
            elif devs:
                # 多台时执行的是 adb 列表里的第一台，界面上必须点明；
                # 否则「显示两台、跑在另一台」会被误判成参数没生效。
                text = f"{devs[0]}（共 {len(devs)} 台，执行用第一台）"
                level = "ok"
            else:
                raw = adb_devices_raw()
                if "unauthorized" in raw:
                    text = "已连接但未授权（手机上点允许）"
                elif "offline" in raw:
                    text = "离线（拔插数据线或重开 USB 调试）"
                else:
                    text = "无设备连接"
                level = "warn"
            self._log_threadsafe(f"设备：{text}", level, target="device")

        self.appium_label.configure(text="Appium：检测中 …", foreground=C_TEXT3)
        self.device_label.configure(text="设备：检测中 …", foreground=C_TEXT3)
        self.appium_dot.configure(foreground=C_TEXT3)
        self.device_dot.configure(foreground=C_TEXT3)
        threading.Thread(target=work, daemon=True).start()

    # ---------------- 日志 ----------------
    def _log_threadsafe(self, text, level="info", target=None):
        self.queue.put(("log", text, level, target))

    def _log(self, text, level="info", target=None):
        if target in ("appium", "device"):
            # 状态条上的小圆点承担颜色语义，文字本身保持中性色，
            # 否则一行里红红绿绿的正文比状态本身还抢眼。
            label = self.appium_label if target == "appium" else self.device_label
            dot = self.appium_dot if target == "appium" else self.device_dot
            dot.configure(
                foreground={"ok": C_OK, "warn": C_WARN, "err": C_ERR}.get(level, C_TEXT3)
            )
            label.configure(text=text, foreground=C_TEXT2)
            return

        lines = str(text).splitlines() or [""]
        self._log_lines.extend((ln, level) for ln in lines)

        # 只留最近 MAX_LOG_LINES 行，长跑也不会把内存吃干净
        overflow = len(self._log_lines) - MAX_LOG_LINES
        if overflow > 0:
            del self._log_lines[:overflow + 1000]
            self._render_log()
            return

        if self._log_filtered():
            # 有过滤/搜索时不能直接 append，否则显示的和过滤条件对不上
            self._render_log()
            return

        self.log_text.configure(state="normal")
        for ln in lines:
            self.log_text.insert("end", ln + "\n", level)
        if self.log_auto.get():
            self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log_filtered(self):
        return self.log_level.get() != "全部" or bool(self.log_search.get().strip())

    def _level_ok(self, level, text, mode):
        if mode == "全部":
            return True
        if mode == "错误与警告":
            return level in ("err", "warn")
        if mode == "仅错误":
            return level == "err"
        if mode == "仅用例结果":
            return level == "err" or bool(RE_RESULT.match(text.strip()))
        return True

    def _render_log(self):
        """按当前过滤条件把缓存重绘一遍（Text 是视图，_log_lines 才是数据）。"""
        mode = self.log_level.get()
        kw = self.log_search.get().strip()
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        for text, level in self._log_lines:
            if self._level_ok(level, text, mode):
                self.log_text.insert("end", text + "\n", level)
        if kw:
            self._highlight(kw)
        if self.log_auto.get():
            self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _highlight(self, kw):
        start, hits = "1.0", 0
        while hits < 500:
            pos = self.log_text.search(kw, start, stopindex="end", nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(kw)}c"
            self.log_text.tag_add("hit", pos, end)
            start = end
            hits += 1

    def _export_log(self):
        os.makedirs(LOGS_DIR, exist_ok=True)
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="导出运行日志",
            defaultextension=".log",
            initialdir=LOGS_DIR,
            initialfile=f"run_{_dt.datetime.now():%Y%m%d_%H%M%S}.log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("全部", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(t for t, _ in self._log_lines))
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc), parent=self.root)
            return
        self._log(f"日志已导出：{path}", "ok")

    def _clear_log(self):
        self._log_lines.clear()
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _zoom_log(self, delta):
        self.log_font_size = max(7, min(18, self.log_font_size + delta))
        self.log_text.configure(font=mono_font(self.log_font_size))

    def _drain_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                if item[0] == "log":
                    if len(item) == 2:
                        # pytest 的原始输出：先解析出结果/进度，再原样打进日志
                        self._on_pytest_line(item[1])
                    else:
                        self._log(item[1], item[2], item[3])
                elif item[0] == "done":
                    self._on_finished(item[1])
        except queue.Empty:
            pass
        self.root.after(80, self._drain_queue)

    # ---------------- 运行中的实时反馈 ----------------
    def _on_pytest_line(self, line):
        """一行输出 → 日志 + 用例状态 + 进度。"""
        level = "info"
        for ev in self.pytest_out.feed(line):
            if ev[0] == "result":
                _, node, status = ev
                level = {
                    "PASSED": "ok", "FAILED": "err", "ERROR": "err",
                    "SKIPPED": "warn", "XFAIL": "warn",
                }.get(status, "info")
                self._mark_status(nodeid_to_iid(node), status)
            elif ev[0] == "progress":
                self._set_progress(ev[1])
            elif ev[0] == "summary":
                self._summary = ev[1]
                if "failed" in ev[1] or "error" in ev[1]:
                    level = "err"
                elif "passed" in ev[1]:
                    level = "ok"
        self._log(line, level)

    def _mark_status(self, iid, status):
        if iid not in self._labels:
            return
        self._status[iid] = status
        self._expanded.add(iid.split("::", 1)[0])
        self._advance_running()
        self._rebuild_rows()
        self._update_sel_label()

    def _advance_running(self):
        """pytest -v 只在用例**结束时**打印一行，所以「正在跑哪条」要自己推：
        上一条出结果后，列表里第一条还没有结果的，就是它。"""
        for iid in self._run_iids:
            if iid not in self._status:
                self._status[iid] = "RUNNING"
                self._expanded.add(iid.split("::", 1)[0])
                return

    def _paint_progress(self):
        """把 DoubleVar 的百分比画到底栏顶边那条细线上。"""
        if not hasattr(self, "prog_fill"):
            return
        try:
            pct = max(0.0, min(100.0, float(self.prog_var.get())))
        except (tk.TclError, ValueError):
            pct = 0.0
        self.prog_fill.place_configure(relwidth=pct / 100.0)

    def _set_progress(self, pct):
        self.prog_var.set(pct)
        done = sum(
            1 for i in self._run_iids
            if i in self._status and self._status[i] != "RUNNING"
        )
        done_iids = self._run_iids
        elapsed = max(0.0, time.monotonic() - (self._run_start or time.monotonic()))
        self.prog_label.configure(
            text="{}% · {}/{} · 已用 {}:{:02d}".format(
                pct, done, len(done_iids), int(elapsed // 60), int(elapsed % 60)
            )
        )

    def _reset_run_state(self):
        """开跑前把上一轮的结果清干净，否则新旧标记会混在一起。"""
        self.pytest_out = PytestOutput()
        self._status.clear()
        self._summary = ""
        self._jump_seq = 0
        self._run_iids = self._selected_case_iids()
        self._run_start = time.monotonic()
        self.prog_var.set(0)
        self.prog_label.configure(
            text=f"0% · 0/{len(self._run_iids)} · 已用 0:00"
        )
        self._advance_running()
        self._rebuild_rows()
        self._update_sel_label()

    def _jump_failure(self):
        """在日志里循环跳到最后一次失败的那一行。"""
        nodes = [
            n for n, s in self.pytest_out.results.items()
            if s in ("FAILED", "ERROR")
        ]
        if not nodes:
            messagebox.showinfo(
                "没有失败", "本次运行还没有失败用例。", parent=self.root
            )
            return
        node = nodes[self._jump_seq % len(nodes)]
        self._jump_seq += 1

        # 目标行可能正被过滤掉，先恢复成「全部」，否则搜不到
        if self.log_level.get() != "全部":
            self.log_level.set("全部")
        if self.log_search.get():
            self.log_search.set("")
        self._render_log()

        pos = self.log_text.search(node, "end", backwards=True, stopindex="1.0")
        if not pos:
            pos = self.log_text.search(
                node.split("::")[-1], "end", backwards=True, stopindex="1.0"
            )
        if not pos:
            self._log(f"日志里已找不到 {node}（可能被截断了），可先导出日志", "warn")
            return
        end = f"{pos} lineend"
        self.log_text.tag_add("jump", pos, end)
        self.log_text.see(pos)
        self.root.after(
            1500, lambda: self.log_text.tag_remove("jump", "1.0", "end")
        )

    # ---------------- 测试参数 ----------------
    def _files_in_targets(self, targets):
        """从 pytest 目标里取出涉及的文件名（保序去重）。"""
        names = []
        for t in targets:
            name = os.path.basename(t.split("::", 1)[0])
            if name and name not in names:
                names.append(name)
        return names

    def _with_shared_params(self, files):
        """用例文件之外，再带上 locators.py 这类共享参数文件（保序去重）。

        locators.py 顶部的 device_number* 才是元素定位实际用的值，
        参数窗口不带它，用户就只会改到不生效的副本。
        """
        out = list(files)
        for name in param_editor.EXTRA_FILES:
            if name not in out and param_editor.has_block(name):
                out.append(name)
        return out

    def _open_params(self):
        """随时打开参数窗口（顶部「测试参数」按钮）。"""
        dlg = ParamDialog(
            self.root, self._with_shared_params(self._files), on_save=self._log
        )
        self.root.wait_window(dlg)
        if dlg.result:
            self._log("参数已写入用例源码，本次执行即为新值。", "info")

    def _open_locators(self):
        """打开元素定位库窗口（顶部「元素定位」按钮）。

        纯静态解析 locators.py，不连设备、不占 Appium session，
        所以跟「正在跑用例」也不冲突（虽然模态窗口本身会拦住主界面操作）。
        """
        dlg = LocatorDialog(self.root, on_log=self._log)
        self.root.wait_window(dlg)

    def _open_picker(self):
        """打开元素拾取窗口（顶部「元素拾取」按钮）。

        非模态、单实例：拾取要连着设备，开两个会抢同一个 session。
        已经开着就把它提到前面，不重复建连接。
        """
        if getattr(self, "_picker", None) is not None:
            try:
                if self._picker.winfo_exists():
                    self._picker.deiconify()
                    self._picker.lift()
                    return
            except tk.TclError:
                pass
        self._picker = ElementPicker(self.root, on_log=self._log)
        self._picker.lift()

    # ---------------- 运行 ----------------
    def _on_run(self):
        if self._running:
            return

        # 先探解释器再让用户填参数：跑不起来就直接说清楚，别等填完参数才报错。
        ok, detail = probe_runtime()
        if not ok:
            self._log(detail, "error")
            messagebox.showerror("无法开始运行", detail)
            return

        targets = self._collect_targets()
        if not targets:
            messagebox.showinfo("提示", "请先勾选至少一个脚本或用例。")
            return

        # 运行前确认参数：目标文件里读不到参数行时，无论如何都要弹一次 ——
        # 免得拿着源码里现有的值跑一整轮，回头才发现测的是另一台机器。
        target_files = self._with_shared_params(self._files_in_targets(targets))
        if self.ask_params_var.get() or any(
            not param_editor.has_block(n) for n in target_files
        ):
            dlg = ParamDialog(
                self.root,
                target_files,
                title="运行前确认测试参数",
                on_save=self._log,
            )
            self.root.wait_window(dlg)
            if not dlg.result:
                self._log("参数未确认，本次执行已取消。", "warn")
                return

        # 预检：设备 / 应用 / 解释器。conftest 里也有这些检查，但那是**建 session 时**，
        # 真机上往往已经白等半分钟；放这里，跑不了就当场说清楚。
        udid = pick_udid()
        if self.preflight_var.get():
            pf = PreflightDialog(self.root, udid, target_files)
            self.root.wait_window(pf)
            if not pf.result:
                self._log("预检未通过，本次执行已取消。", "warn")
                return

        self._reset_run_state()
        self._running = True
        self._stopped_by_user = False
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.report_btn.configure(state="disabled")
        self._log("=" * 78)
        self._log(f"本次执行目标（{len(targets)} 项）：")
        for t in targets:
            self._log(f"    {t}", "muted")

        self._log("本次生效参数（直接读自用例源码）：")
        # 带上 locators.py：设备编号是「这次连哪台机器」，日志里必须看得到，
        # 否则用例参数看着对、实际却连了另一台，排查时最费时间。
        for fname in target_files:
            for key, slot in (param_editor.scan([fname]).get(fname) or {}).items():
                label = param_editor.FIELD_LABELS.get(key, key)
                self._log(
                    "    [{}] 第 {} 行  {}：{}".format(
                        fname, slot["lineno"], label, slot["value"]
                    ),
                    "muted",
                )

        html_path = None
        if self.html_var.get():
            os.makedirs(REPORTS_DIR, exist_ok=True)
            stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = os.path.join(REPORTS_DIR, f"report_{stamp}.html")
            self._last_report = html_path

        maxfail = self.maxfail_var.get()

        def work():
            if udid:
                self.queue.put(("log", f"本次执行设备：{udid}", "ok"))
            else:
                self.queue.put(
                    ("log", "未检测到设备，pytest 建 session 时会失败。", "warn")
                )

            if not self.appium.ensure():
                self.queue.put(("log", "Appium 未就绪，本次执行已取消。", "error", None))
                self.queue.put(("done", -1, None))
                return
            # 等 Appium 的这几秒里用户可能已经点了「停止」——那时 proc 还是 None，
            # stop() 无从下手，只能在这里补一次判断，否则会照样把 pytest 拉起来。
            if self._stopped_by_user:
                self.queue.put(("log", "已取消，未启动 pytest。", "warn"))
                self.queue.put(("done", 130, None))
                return
            self.runner.start(targets, maxfail, html_path, udid=udid)

        threading.Thread(target=work, daemon=True).start()

    def _on_stop(self):
        if not self._running:
            return
        self._stopped_by_user = True
        self._log("收到停止指令，正在终止测试进程 …", "warn")
        self.runner.stop()

    def _on_finished(self, returncode):
        self._running = False
        # 没跑到的用例别一直挂着「运行中」
        for iid, st in list(self._status.items()):
            if st == "RUNNING":
                del self._status[iid]
        self._rebuild_rows()
        self._update_sel_label()

        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if self._last_report and os.path.exists(self._last_report):
            self.report_btn.configure(state="normal")
            self._log(f"HTML 报告：{self._last_report}", "ok")

        # 汇总：优先用 pytest 自己那行统计，比退出码信息量大得多
        elapsed = max(0.0, time.monotonic() - (self._run_start or time.monotonic()))
        passed = sum(1 for s in self._status.values() if s == "PASSED")
        failed = sum(1 for s in self._status.values() if s in ("FAILED", "ERROR"))
        self.prog_label.configure(
            text="{}% · 通过 {} / 失败 {} · 用时 {}:{:02d}".format(
                100 if not self._run_iids else int(self.prog_var.get()),
                passed, failed, int(elapsed // 60), int(elapsed % 60),
            )
        )
        if self._summary:
            self._log(f"统计：{self._summary}", "err" if failed else "ok")

        if self._stopped_by_user:
            # 手动停止走的是 SIGINT / CTRL_BREAK，pytest 退出码非 0 属正常，
            # 再打一行「❌ 退出码 2」会让人误以为出了新问题。
            self._log(f"■ 已手动停止（退出码 {returncode}）。", "warn")
            self._stopped_by_user = False
        elif returncode == 0:
            self._log("✅ 全部通过。", "ok")
        else:
            self._log(f"❌ 执行结束，退出码 {returncode}（0 为全部通过）。", "err")
            if failed:
                self._log("点「跳到失败」可直接定位到失败的用例行。", "muted")

    # ---------------- 外部打开 ----------------
    def _open_reports(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        open_in_os(REPORTS_DIR)

    def _open_failures(self):
        FailureDialog(self.root, on_log=self._log)

    def _open_env_check(self):
        EnvCheckDialog(self.root)

    def _run_tool(self, spec):
        ScriptDialog(self.root, spec, on_log=self._log)

    def _open_appium_log(self):
        if os.path.exists(APPIUM_LOG):
            open_in_os(APPIUM_LOG)
        else:
            messagebox.showinfo("提示", "暂无 Appium 日志（本次未启动过 Server）。")

    def _open_last_report(self):
        if self._last_report and os.path.exists(self._last_report):
            webbrowser.open(file_url(self._last_report))


# --------------------------------------------------------------------------
# 入口
# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SUPVAN 自动化测试启动器")
    parser.add_argument(
        "--list", action="store_true", help="只打印识别到的用例清单，不打开界面"
    )
    args = parser.parse_args()

    if args.list:
        cases = discover_cases()
        total = 0
        for fname, funcs in cases:
            print(f"{fname}  ({len(funcs)} 条)")
            for fn in funcs:
                print(f"    {fn}")
                total += 1
        print(f"\n合计：{len(cases)} 个文件 / {total} 条用例")
        print(f"Appium  {APPIUM_HOST}:{APPIUM_PORT}  ->  {'运行中' if port_open(APPIUM_PORT) else '未启动'}")
        print(f"可执行文件  {find_appium()}")
        print(f"解释器      {VENV_PYTHON}  {'✓' if os.path.exists(VENV_PYTHON) else '✗ 缺失'}")
        return 0

    # 高 DPI 屏下避免字体发虚
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
