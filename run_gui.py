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
import locator_manager
import math
import os
import pathlib
import queue
import shutil
import socket
import subprocess
import sys
import param_editor
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from utils import ui_inspector

# --------------------------------------------------------------------------
# 路径与环境常量
# --------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TESTCASE_DIR = os.path.join(PROJECT_ROOT, "testcases")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
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

# --------------------------------------------------------------------------
# 列表区外观
#
# 左侧不用 ttk.Treeview：它的展开三角由系统主题绘制、尺寸无法调整，
# 勾选框也只能跟树统一字号 —— 满足不了「单独加大」的需求。
# 改用 Canvas + 若干 Label 手工拼行，尺寸完全可控。
#
# 想再调大，只改下面这几个数即可。
# --------------------------------------------------------------------------
ROW_BG = "#FFFFFF"
ARROW_SIZE = 13          # 展开三角字号
CHECK_SIZE = 17          # 勾选框字号
ROW_PADY = 4             # 行上下内边距（决定行高）
INDENT_PX = 20           # 子项相对父项的缩进
FONT_FILE_ROW = ("Microsoft YaHei UI", 10, "bold")
FONT_CASE_ROW = ("Microsoft YaHei UI", 9)
FONT_ARROW = ("Segoe UI Symbol", ARROW_SIZE)
FONT_CHECK = ("Segoe UI Symbol", CHECK_SIZE)


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

    def start(self, targets, max_fail_fast, html_report):
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
                creationflags=CREATE_NO_WINDOW,
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

    def stop(self):
        """终止整棵进程树（Windows 下 terminate 只杀父进程，会留下僵尸子进程）。"""
        if not self.proc or self.proc.poll() is not None:
            return
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW,
            )
        except Exception:
            self.proc.terminate()


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
            foreground="#666666",
        ).pack(anchor="w")

        body = ttk.Frame(self, padding=(14, 8, 14, 2))
        body.pack(fill="both", expand=True)
        self._build_body(body)

        foot = ttk.Frame(self, padding=(14, 6, 14, 12))
        foot.pack(fill="x")
        ttk.Button(foot, text="恢复初始值", width=12, command=self._restore).pack(
            side="left"
        )
        ttk.Button(foot, text="取消", width=10, command=self._cancel).pack(side="right")
        ttk.Button(foot, text="确定并保存", width=12, command=self._save).pack(
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
                parent, text="没有找到可改写的参数行。", foreground="#8a8a8a"
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
                foreground="#a0a0a0",
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
                ttk.Entry(box, textvariable=var, width=30).grid(
                    row=r, column=1, sticky="w", pady=4
                )
                # 标出文件+行号：改完能直接去源码核对，也免得以为改错了地方
                ttk.Label(
                    box,
                    text="{} 第 {} 行".format(fname, slot["lineno"]),
                    foreground="#8a8a8a",
                ).grid(row=r, column=2, sticky="w", padx=(10, 0), pady=4)
                self._vars[fname][key] = var
                r += 1

    def _build_case_table(self, parent, files):
        """列＝用例文件，行＝参数；某文件没有该参数时留「—」。"""
        box = ttk.LabelFrame(parent, text="用例参数（每个文件一列）", padding=(12, 8))
        box.pack(fill="both", expand=True)
        for c in range(1, len(files) + 1):
            box.columnconfigure(c, weight=1)

        for c, fname in enumerate(files, start=1):
            ttk.Label(
                box, text=fname, font=("TkDefaultFont", 10, "bold")
            ).grid(row=0, column=c, sticky="w", padx=(0, 12))
            ttk.Label(
                box,
                text=self._line_hint(self._slots[fname].values()),
                foreground="#8a8a8a",
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
                    ttk.Label(box, text="—", foreground="#c8c8c8").grid(
                        row=r, column=c, sticky="w", padx=(0, 12), pady=5
                    )
                    continue
                var = tk.StringVar(value=self._initial(slot))
                ttk.Entry(box, textvariable=var, width=18).grid(
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
        ("lineno", "行", 52, "e", False),
        ("key", "key", 182, "w", False),
        ("by", "By", 62, "center", False),
        ("status", "状态", 58, "center", False),
        ("refs", "引用", 50, "e", False),
        ("selector", "selector", 292, "w", True),
        ("comment", "注释", 166, "w", True),
    )
    STATUS_TEXT = {"error": "错误", "warn": "警告", "info": "提示", "": "—"}
    LEVEL_RANK = {"error": 0, "warn": 1, "info": 2, "": 3}

    def __init__(self, master, on_log=None):
        super().__init__(master)
        self.on_log = on_log
        self.title("元素定位库 · locators.py")
        self.geometry("1000x648")
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

        self.stat_label = ttk.Label(self, padding=(12, 0, 12, 4), foreground="#555555")
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
        self.tree.tag_configure("error", background="#FDECEA", foreground="#8C2A20")
        self.tree.tag_configure("warn", background="#FFF9E6", foreground="#7A5B00")
        self.tree.tag_configure("info", background="#FFFFFF", foreground="#5A5A5A")
        self.tree.tag_configure("clean", background="#FFFFFF", foreground="#222222")

        det = ttk.LabelFrame(self, text=" 详情 ", padding=(10, 6))
        det.pack(fill="x", padx=12)
        self.detail = tk.Text(
            det, height=7, wrap="word", relief="flat", background="#FAFAFA",
            font=("Microsoft YaHei UI", 9), padx=6, pady=4,
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

    LEVEL_COLOR = {"ok": "#1B7F3B", "warn": "#9A6B00", "bad": "#A32020"}

    def __init__(self, master, on_log=None):
        super().__init__(master)
        self.on_log = on_log
        self.title("元素拾取 · 点截图出定位")
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
        self.after(120, self._poll)

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

        self.stat = ttk.Label(self, padding=(12, 0, 12, 4), foreground="#555555")
        self.stat.pack(fill="x")
        self._set_status("点「连接设备」开始：工具会拉起 App 并抓取当前这一屏")

        pane = ttk.Panedwindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        left = ttk.LabelFrame(pane, text=" 手机截图 · 点一下选中该位置的控件 ", padding=4)
        self.canvas = tk.Canvas(left, background="#404040", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        pane.add(left, weight=3)

        right = ttk.Frame(pane)
        pane.add(right, weight=2)

        # 属性
        info = ttk.LabelFrame(right, text=" 选中元素 ", padding=(8, 6))
        info.pack(fill="x")
        self.detail = tk.Text(
            info, height=7, wrap="none", relief="flat", background="#FAFAFA",
            font=("TkDefaultFont", 9), padx=6, pady=4,
        )
        self.detail.pack(fill="x")
        self.detail.configure(state="disabled")
        ttk.Button(
            info, text="↑ 选父级（点到小图标时用）", command=self._select_parent
        ).pack(anchor="w", pady=(6, 0))

        # 候选
        cand = ttk.LabelFrame(
            right, text=" 定位方案（按推荐度排序，双击即复制） ", padding=(8, 6)
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
        code = ttk.LabelFrame(right, text=" 复制即用 ", padding=(8, 6))
        code.pack(fill="both", expand=True, pady=(8, 0))
        mono = ("Menlo", 9) if sys.platform == "darwin" else ("Consolas", 9)
        self.code = tk.Text(
            code, height=8, wrap="none", relief="flat", background="#1E1E1E",
            foreground="#D4D4D4", insertbackground="#D4D4D4", font=mono, padx=8, pady=6,
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
                text="还未抓取屏幕", fill="#BBBBBB",
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
            outline="#E53935", width=2, tags="marker",
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
        self._picker = None       # 元素拾取窗口（单实例）

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

    # ---------------- 界面搭建 ----------------
    def _build_ui(self):
        self.root.title("SUPVAN 自动化测试管理工具")
        self.root.geometry("1060x700")
        self.root.minsize(900, 560)

        style = ttk.Style()
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass

        # 顶部：环境状态条
        top = ttk.Frame(self.root, padding=(12, 10, 12, 6))
        top.pack(fill="x")

        ttk.Label(top, text="环境状态", font=("Microsoft YaHei UI", 9, "bold")).pack(
            side="left"
        )
        self.appium_label = ttk.Label(top, text="Appium：检测中 …")
        self.appium_label.pack(side="left", padx=(12, 20))
        self.device_label = ttk.Label(top, text="设备：检测中 …")
        self.device_label.pack(side="left")
        ttk.Button(top, text="重新检测", width=10, command=self._refresh_env).pack(
            side="right"
        )
        ttk.Button(top, text="测试参数", width=10, command=self._open_params).pack(
            side="right", padx=(0, 6)
        )
        ttk.Button(top, text="元素定位", width=10, command=self._open_locators).pack(
            side="right", padx=(0, 6)
        )
        ttk.Button(top, text="元素拾取", width=10, command=self._open_picker).pack(
            side="right", padx=(0, 6)
        )

        # 中部：左右分栏
        pane = ttk.Panedwindow(self.root, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        left = ttk.LabelFrame(pane, text=" 选择要执行的脚本 ", padding=6)
        right = ttk.LabelFrame(pane, text=" 运行日志 ", padding=6)
        pane.add(left, weight=2)
        pane.add(right, weight=3)

        self.rows_canvas = tk.Canvas(
            left, background=ROW_BG, highlightthickness=0, bd=0
        )
        vs = ttk.Scrollbar(left, orient="vertical", command=self.rows_canvas.yview)
        self.rows_canvas.configure(yscrollcommand=vs.set)
        self.rows_canvas.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        self.rows_inner = tk.Frame(self.rows_canvas, background=ROW_BG)
        self._inner_id = self.rows_canvas.create_window(
            (0, 0), window=self.rows_inner, anchor="nw"
        )
        self.rows_canvas.bind("<Configure>", self._on_canvas_resize)
        self.rows_canvas.bind_all("<MouseWheel>", self._on_wheel)

        self.log_text = tk.Text(
            right,
            wrap="none",
            font=("Consolas", 9),
            background="#1e1e1e",
            foreground="#d4d4d4",
            insertbackground="#d4d4d4",
            state="disabled",
        )
        ls = ttk.Scrollbar(right, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=ls.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        ls.pack(side="right", fill="y")

        self.log_text.tag_config("err", foreground="#f48771")
        self.log_text.tag_config("warn", foreground="#dcdcaa")
        self.log_text.tag_config("ok", foreground="#89d185")
        self.log_text.tag_config("info", foreground="#d4d4d4")
        self.log_text.tag_config("muted", foreground="#808080")

        # 底部：操作区
        bottom = ttk.Frame(self.root, padding=(12, 4, 12, 4))
        bottom.pack(fill="x")
        ttk.Button(bottom, text="全选", width=8, command=lambda: self._set_all(True)).pack(
            side="left"
        )
        ttk.Button(bottom, text="反选", width=8, command=self._invert).pack(
            side="left", padx=(6, 0)
        )
        self.sel_label = ttk.Label(bottom, text="", foreground="#666666")
        self.sel_label.pack(side="left", padx=(12, 0))

        ttk.Button(bottom, text="打开报告目录", width=14, command=self._open_reports).pack(
            side="right"
        )
        ttk.Button(
            bottom, text="打开 Appium 日志", width=16, command=self._open_appium_log
        ).pack(side="right", padx=(0, 6))

        action = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        action.pack(fill="x")

        self.run_btn = ttk.Button(
            action, text="▶  开始运行", width=16, command=self._on_run
        )
        self.run_btn.pack(side="left")
        self.stop_btn = ttk.Button(
            action, text="■  停止", width=10, command=self._on_stop, state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(8, 0))
        self.report_btn = ttk.Button(
            action, text="查看最新报告", width=14, command=self._open_last_report,
            state="disabled",
        )
        self.report_btn.pack(side="left", padx=(8, 0))

        self.maxfail_var = tk.BooleanVar(value=False)
        self.html_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            action, text="首错即停（--maxfail=1）", variable=self.maxfail_var
        ).pack(side="right", padx=(12, 0))
        ttk.Checkbutton(action, text="生成 HTML 报告", variable=self.html_var).pack(
            side="right"
        )
        self.ask_params_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            action, text="运行前确认参数", variable=self.ask_params_var
        ).pack(side="right", padx=(12, 0))

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

        for fid in self._files:
            self._make_row(fid, depth=0)
            if fid in self._expanded:
                for cid in self._children.get(fid, []):
                    self._make_row(cid, depth=1)

        self.rows_inner.update_idletasks()
        self.rows_canvas.configure(scrollregion=self.rows_canvas.bbox("all"))
        self.rows_canvas.yview_moveto(keep)

    def _make_row(self, iid, depth):
        is_file = depth == 0
        has_kids = bool(self._children.get(iid))
        checked = self._state.get(iid, False)
        expanded = iid in self._expanded

        row = tk.Frame(self.rows_inner, background=ROW_BG)
        row.pack(fill="x")

        if depth:
            tk.Frame(row, width=INDENT_PX, background=ROW_BG).pack(side="left", fill="y")

        # 展开三角：只有文件行有；点它只负责展开 / 收起，不碰勾选状态
        arrow = tk.Label(
            row,
            text=("\u25BC" if expanded else "\u25B6") if has_kids else "",
            font=FONT_ARROW,
            width=2,
            background=ROW_BG,
            foreground="#5F5E5A",
            cursor="hand2" if has_kids else "",
            pady=ROW_PADY,
        )
        arrow.pack(side="left", padx=(4 if is_file else 0, 2))

        # 勾选框：点它或点后面的文字都切换勾选
        check = tk.Label(
            row,
            text=CHECKED if checked else UNCHECKED,
            font=FONT_CHECK,
            width=2,
            background=ROW_BG,
            foreground="#1a7f37" if checked else "#9A9890",
            cursor="hand2",
            pady=ROW_PADY,
        )
        check.pack(side="left")

        label = tk.Label(
            row,
            text=self._labels.get(iid, iid),
            anchor="w",
            font=FONT_FILE_ROW if is_file else FONT_CASE_ROW,
            background=ROW_BG,
            foreground="#2C2C2A" if is_file else "#4A4A46",
            cursor="hand2",
            pady=ROW_PADY,
        )
        label.pack(side="left", fill="x", expand=True, padx=(2, 0))

        if has_kids:
            arrow.bind("<Button-1>", lambda e, i=iid: self._toggle_expand(i))
        for widget in (row, check, label):
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
                self.rows_canvas.yview_scroll(-int(event.delta / 120), "units")
                return
            widget = getattr(widget, "master", None)

    def _update_sel_label(self):
        n = len(self._collect_targets())
        self.sel_label.configure(text=f"已选 {n} 项")

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
            elif devs:
                text = "、".join(devs)
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

        self.appium_label.configure(text="Appium：检测中 …")
        self.device_label.configure(text="设备：检测中 …")
        threading.Thread(target=work, daemon=True).start()

    # ---------------- 日志 ----------------
    def _log_threadsafe(self, text, level="info", target=None):
        self.queue.put(("log", text, level, target))

    def _log(self, text, level="info", target=None):
        if target == "appium":
            self.appium_label.configure(text=text)
            self.appium_label.configure(foreground="#1a7f37" if level == "ok" else "#9a6700")
            return
        if target == "device":
            self.device_label.configure(text=text)
            self.device_label.configure(foreground="#1a7f37" if level == "ok" else "#9a6700")
            return

        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n", level)
        self.log_text.see("end")
        # 防止长跑时日志无限堆积
        if int(self.log_text.index("end-1c").split(".")[0]) > 6000:
            self.log_text.delete("1.0", "1500.0")
        self.log_text.configure(state="disabled")

    def _drain_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                if item[0] == "log":
                    if len(item) == 2:
                        self._log(item[1])
                    else:
                        self._log(item[1], item[2], item[3])
                elif item[0] == "done":
                    self._on_finished(item[1])
        except queue.Empty:
            pass
        self.root.after(80, self._drain_queue)

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

        self._running = True
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
            if not self.appium.ensure():
                self.queue.put(("log", "Appium 未就绪，本次执行已取消。", "error", None))
                self.queue.put(("done", -1, None))
                return
            self.runner.start(targets, maxfail, html_path)

        threading.Thread(target=work, daemon=True).start()

    def _on_stop(self):
        if not self._running:
            return
        self._log("收到停止指令，正在终止测试进程 …", "warn")
        self.runner.stop()

    def _on_finished(self, returncode):
        self._running = False
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if self._last_report and os.path.exists(self._last_report):
            self.report_btn.configure(state="normal")
            self._log(f"HTML 报告：{self._last_report}", "ok")
        if returncode == 0:
            self._log("\n✅ 全部通过。", "ok")
        else:
            self._log(f"\n❌ 执行结束，退出码 {returncode}（0 为全部通过）。", "err")

    # ---------------- 外部打开 ----------------
    def _open_reports(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        open_in_os(REPORTS_DIR)

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
