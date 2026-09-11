#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SUPVAN 自动化测试工具 · 界面主题

把配色、字体、ttk 样式与两个自绘控件集中在这里；`run_gui.py` 只负责布局
和业务逻辑，不再散落颜色字面量。想统一换肤（比如改深色），只动本文件。

为什么不直接用 Windows 默认的 vista 主题：
    它把按钮 / 输入框交给系统绘制（渐变、固定圆角、固定配色），颜色基本
    改不动，观感也跟现代扁平风不搭。这里统一切到 clam 作为底，再把每个
    部件的外观显式声明出来 —— 改得动，才谈得上设计。
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk


# --------------------------------------------------------------------------
# 配色
# --------------------------------------------------------------------------
class COLORS:
    """全局配色表。命名按用途而非色值，换肤时只改这里。

    取向是**对比优先**：
      - 窗口底色压深一档，白卡片才立得起来；
      - 正文用近黑而不是「深灰」，弱化文字也压到 #5C6B85 ——
        上一版 #98A2B3 当行号/提示用时，在浅底上几乎看不清。
    """

    # 面
    bg          = "#DCE3EC"   # 窗口底色
    surface     = "#FFFFFF"   # 卡片
    surface_alt = "#EFF3F8"   # 次级面：表头 / 悬停底
    border      = "#B9C4D4"   # 卡片描边（比底色深，轮廓才清楚）
    divider     = "#E1E7EF"   # 卡片内分隔线

    # 字
    text        = "#0D1526"   # 主要文字（近黑）
    text_2      = "#33415C"   # 次要文字
    text_3      = "#5C6B85"   # 弱化文字（行号、提示）

    # 主色
    primary     = "#1A4FD6"
    primary_h   = "#123BA8"   # hover
    primary_l   = "#D7E3FC"   # 浅底

    # 语义色
    ok          = "#0B6E38"
    ok_l        = "#D3EFDF"
    warn        = "#9C5200"
    warn_l      = "#FBE8CC"
    err         = "#B72214"
    err_l       = "#FADDD9"

    # 日志区（深色终端，GitHub 深色系，对比比上一版更足）
    log_bg      = "#0D1117"
    log_text    = "#D6DEE8"
    log_dim     = "#7E8896"
    log_err     = "#FF7B72"
    log_warn    = "#E3B341"
    log_ok      = "#3FB950"
    log_cmd     = "#79C0FF"
    log_head    = "#8B949E"


UI = "Microsoft YaHei UI"
MONO = "Consolas"


def f(size=10, weight="normal", family=UI):
    """字体工厂 —— 统一从这里取，避免各处硬编码字体名与字号。"""
    return (family, size, weight)


# --------------------------------------------------------------------------
# ttk 样式
# --------------------------------------------------------------------------
def apply_theme(root):
    """把 ttk 部件切到 clam 底并逐项声明外观。重复调用是安全的。"""
    st = ttk.Style(root)
    try:
        st.theme_use("clam")
    except tk.TclError:
        return

    C = COLORS

    # 默认字体也一并换成雅黑，否则 ttk 自带的 Segoe/宋体混进来会不协调
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
        try:
            tkfont.nametofont(name).configure(family=UI, size=10)
        except tk.TclError:
            pass

    st.configure(".", background=C.bg, foreground=C.text, font=f(10))
    st.configure("TFrame", background=C.bg)
    st.configure("TLabel", background=C.bg, foreground=C.text)

    # ---- 卡片内的文字（背景是白卡片，必须显式声明，否则会露出灰底方块）----
    st.configure("H1.TLabel", background=C.surface, foreground=C.text, font=f(15, "bold"))
    st.configure("H2.TLabel", background=C.surface, foreground=C.text, font=f(11, "bold"))
    st.configure("Card.TLabel", background=C.surface, foreground=C.text, font=f(10))
    st.configure("Muted.TLabel", background=C.surface, foreground=C.text_2, font=f(9))
    st.configure("Faint.TLabel", background=C.surface, foreground=C.text_3, font=f(9))
    # 弹窗里的空白页 / 内容页同样是白底
    st.configure("Page.TFrame", background=C.surface)

    # ---- 输入框 ----
    st.configure(
        "Card.TEntry",
        fieldbackground=C.surface, background=C.surface, foreground=C.text,
        bordercolor=C.border, lightcolor=C.border, darkcolor=C.border,
        insertcolor=C.text, padding=(9, 6),
    )
    st.map(
        "Card.TEntry",
        bordercolor=[("focus", C.primary)],
        lightcolor=[("focus", C.primary)],
        darkcolor=[("focus", C.primary)],
    )

    # ---- 复选框 ----
    st.configure(
        "Card.TCheckbutton",
        background=C.surface, foreground=C.text_2, font=f(10),
        focuscolor=C.surface, indicatorcolor=C.surface, bordercolor=C.border,
    )
    st.map(
        "Card.TCheckbutton",
        background=[("active", C.surface)],
        foreground=[("active", C.text)],
        indicatorcolor=[("selected", C.primary), ("!selected", C.surface)],
    )

    # ---- 下拉框 ----
    st.configure(
        "Card.TCombobox",
        fieldbackground=C.surface, background=C.surface, foreground=C.text,
        bordercolor=C.border, lightcolor=C.border, darkcolor=C.border,
        arrowcolor=C.text_2, padding=(7, 5), selectbackground=C.primary_l,
        selectforeground=C.text,
    )
    st.map(
        "Card.TCombobox",
        fieldbackground=[("readonly", C.surface), ("disabled", C.surface_alt)],
        bordercolor=[("focus", C.primary)],
        arrowcolor=[("disabled", C.text_3)],
    )

    # ---- 表格（元素定位库用）----
    st.configure(
        "Card.Treeview",
        background=C.surface, fieldbackground=C.surface, foreground=C.text,
        bordercolor=C.border, lightcolor=C.surface, darkcolor=C.surface,
        borderwidth=0, relief="flat", rowheight=26, font=f(9),
    )
    st.map(
        "Card.Treeview",
        background=[("selected", C.primary_l)],
        foreground=[("selected", C.text)],
    )
    st.configure(
        "Card.Treeview.Heading",
        background=C.surface_alt, foreground=C.text_2, font=f(9, "bold"),
        relief="flat", padding=(8, 7), bordercolor=C.border,
    )
    st.map(
        "Card.Treeview.Heading",
        background=[("active", C.primary_l)],
        foreground=[("active", C.text)],
    )

    # ---- 滚动条：细长条、不抢视线 ----
    # arrowsize 同时决定滚动条的**厚度**：设成 0/1 想藏箭头，结果整条被压成
    # 4~5px，细到点不中（踩过）。这里保留正常尺寸，靠 arrowcolor=trough
    # 让箭头与轨道同色 —— 视觉上等于没有箭头，厚度却正常。
    for name, trough, thumb, thumb_hover in (
        ("Slim.Vertical.TScrollbar", C.surface_alt, "#C6CEDA", "#A9B3C2"),
        ("Dark.Vertical.TScrollbar", C.log_bg, "#39414D", "#4C5666"),
        ("Dark.Horizontal.TScrollbar", C.log_bg, "#39414D", "#4C5666"),
    ):
        st.configure(
            name, background=thumb, troughcolor=trough, bordercolor=trough,
            darkcolor=thumb, lightcolor=thumb, arrowcolor=trough,
            relief="flat", arrowsize=11, width=11, borderwidth=0,
        )
        st.map(name, background=[("active", thumb_hover)])

    # ---- 记事本（参数弹窗分页用）----
    st.configure("Card.TNotebook", background=C.surface, borderwidth=0,
                 tabmargins=(0, 4, 0, 0), lightcolor=C.surface, darkcolor=C.surface)
    st.configure(
        "Card.TNotebook.Tab",
        background=C.surface_alt, foreground=C.text_2, font=f(9),
        padding=(16, 8), borderwidth=0, lightcolor=C.surface_alt,
        darkcolor=C.surface_alt,
    )
    st.map(
        "Card.TNotebook.Tab",
        background=[("selected", C.surface), ("active", C.primary_l)],
        foreground=[("selected", C.primary), ("active", C.text)],
        lightcolor=[("selected", C.surface)],
        darkcolor=[("selected", C.surface)],
        expand=[("selected", (0, 0, 0, 0))],
    )

    # ---- 分组框（弹窗里用，去掉默认凹槽）----
    st.configure("Card.TLabelframe", background=C.surface, bordercolor=C.border,
                 relief="solid", borderwidth=1)
    st.configure("Card.TLabelframe.Label", background=C.surface,
                 foreground=C.text_2, font=f(9, "bold"))


# --------------------------------------------------------------------------
# 自绘控件
# --------------------------------------------------------------------------
def round_rect(cv, x1, y1, x2, y2, r, **kw):
    """在 Canvas 上画圆角矩形。

    Tk 没有原生圆角矩形，用平滑多边形近似 —— 这是社区通行做法，
    半径在 4~20px 之间肉眼看不出与真圆角的差别。
    """
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return cv.create_polygon(pts, smooth=True, **kw)


class RoundButton(tk.Canvas):
    """圆角按钮。

    ttk 按钮的圆角和配色由主题决定、改不动，只能自绘。四种变体：
    primary（主操作）/ secondary（常规）/ soft（轻量、浅蓝底）/ danger（危险）。

    对外接口刻意不重写 `configure`（那是 Canvas 自己的方法），改用
    `set_state()` / `set_text()`。
    """

    VARIANTS = {
        "primary": dict(
            bg=COLORS.primary, hover=COLORS.primary_h, fg="#FFFFFF",
            border=COLORS.primary,
            off_bg="#D3DAE5", off_fg="#8B95A6", off_bd="#D3DAE5",
        ),
        "secondary": dict(
            bg=COLORS.surface, hover=COLORS.primary_l, fg=COLORS.text,
            # 描边比卡片边框浅一档：与卡片同色的话，白底按钮在白卡上
            # 会跟输入框长得一模一样
            border="#C8D2E0",
            off_bg=COLORS.surface_alt, off_fg="#9AA5B5", off_bd=COLORS.divider,
        ),
        "soft": dict(
            bg=COLORS.primary_l, hover="#C2D6F9", fg=COLORS.primary,
            border=COLORS.primary_l,
            off_bg=COLORS.surface_alt, off_fg="#9AA5B5", off_bd=COLORS.surface_alt,
        ),
        "danger": dict(
            bg=COLORS.err, hover="#96180D", fg="#FFFFFF",
            border=COLORS.err,
            off_bg="#E6C7C3", off_fg="#FBF0EF", off_bd="#E6C7C3",
        ),
    }

    def __init__(self, master, text="", command=None, variant="secondary",
                 minwidth=0, height=34, padx=18, radius=9, font=None,
                 parent_bg=None, state="normal"):
        self._v = dict(self.VARIANTS.get(variant, self.VARIANTS["secondary"]))
        pbg = parent_bg or COLORS.surface
        self._font = font or f(10)

        # 宽度按文字**实测**自适应。原先写死像素宽，一旦系统缩放变成
        # 125%/150%，中文字宽等比放大就会把文字挤出按钮 —— 这正是
        # 「按钮显示不全」的根源。minwidth 只用于需要视觉对齐的场景。
        self._edge = padx
        # 尺寸字段刻意不用 _w/_h —— 那是 tkinter.Misc 存窗口路径名的内部
        # 属性，覆盖它会让 self.tk.call 拿到错误窗口名（踩过）。
        self._bw = max(int(minwidth), self._text_width(text) + 2 * padx)
        self._bh = height

        super().__init__(
            master, width=self._bw, height=self._bh, background=pbg,
            highlightthickness=0, bd=0, cursor="hand2",
        )
        self._text = text
        self._command = command
        self._radius = radius
        self._state = state
        self._hover = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._render()

    def _text_width(self, text):
        try:
            return tkfont.Font(font=self._font).measure(text)
        except tk.TclError:
            # 窗口还没建好时退化成按字数粗估，保证不炸
            return len(text) * 14

    # ---- 绘制 ----
    def _render(self):
        self.delete("all")
        v, on = self._v, self._state != "disabled"
        if not on:
            bg, fg, bd = v["off_bg"], v["off_fg"], v["off_bd"]
        elif self._hover:
            bg, fg, bd = v["hover"], v["fg"], v["hover"]
        else:
            bg, fg, bd = v["bg"], v["fg"], v["border"]
        round_rect(
            self, 0.5, 0.5, self._bw - 0.5, self._bh - 0.5, self._radius,
            fill=bg, outline=bd, width=1,
        )
        self.create_text(
            self._bw / 2, self._bh / 2, text=self._text, fill=fg,
            font=self._font, anchor="center",
        )

    # ---- 事件 ----
    def _on_enter(self, _e=None):
        if self._state == "disabled":
            return
        self._hover = True
        self._render()

    def _on_leave(self, _e=None):
        self._hover = False
        self._render()

    def _on_press(self, _e=None):
        if self._state == "disabled" or not self._command:
            return
        self._command()

    def _on_release(self, _e=None):
        # 按下即触发，这里只负责把 hover 态收回来（防止鼠标移出后残留）
        self._on_leave()

    # ---- 对外接口 ----
    def set_state(self, state):
        """state: 'normal' | 'disabled'（对齐 tk 的习惯叫法）。"""
        self._state = state
        self.configure(cursor="hand2" if state != "disabled" else "arrow")
        self._render()

    def set_text(self, text):
        self._text = text
        need = self._text_width(text) + 2 * self._edge
        if need > self._bw:                 # 只增不减，免得布局来回跳
            self._bw = need
            self.configure(width=self._bw)
        self._render()

    def is_disabled(self):
        return self._state == "disabled"


class Card(tk.Frame):
    """圆角卡片容器。

    用法：把子控件放进 `card.body`（一个普通 Frame），不要直接放进 card。

    原理：Canvas 铺满整块并画圆角矩形，内容 Frame 内缩 radius 像素 ——
    内缩量 ≥ 圆角半径时，内容区的方角恰好落在圆角之内，不会露出方角
    （Tk 没有透明背景，这是唯一能做到真圆角的办法）。
    """

    def __init__(self, master, radius=14, bg=None, border=None,
                 parent_bg=None, **kw):
        self.radius = radius
        self._fill = bg or COLORS.surface
        self._border = border or COLORS.border
        pbg = parent_bg or COLORS.bg

        super().__init__(master, background=pbg, highlightthickness=0, bd=0, **kw)

        # Canvas 只当背景：必须用 place —— 它不参与父容器的尺寸传播，
        # 否则 Tk 会给 Canvas 一个 378x265 的默认需求尺寸，把卡片撑高
        # （顶部那张卡片一度被撑成一大块空白，就是这么来的）。
        self._cv = tk.Canvas(self, background=pbg, highlightthickness=0, bd=0)
        self._cv.place(x=0, y=0, relwidth=1, relheight=1)

        # 由 body 决定卡片大小，内缩 radius 使方角恰好落在圆角之内
        self.body = tk.Frame(self, background=self._fill)
        self.body.pack(fill="both", expand=True, padx=radius, pady=radius)

        self.bind("<Configure>", self._redraw)

    def _redraw(self, _event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 2 or h <= 2:
            return
        self._cv.delete("all")
        round_rect(
            self._cv, 0.5, 0.5, w - 0.5, h - 0.5, self.radius,
            fill=self._fill, outline=self._border, width=1,
        )


class CheckBox(tk.Frame):
    """自绘复选框（18px 圆角方块 + 对勾）。

    不用 ttk.Checkbutton：clam 的指示器由主题的绘制逻辑牵制，选中态跟这套
    圆角风格对不齐；自绘反而更可控，hover 也能顺带做出来。
    """

    def __init__(self, master, text="", variable=None, command=None,
                 parent_bg=None, font=None, box=18):
        pbg = parent_bg or COLORS.surface
        super().__init__(master, background=pbg)
        self.var = variable if variable is not None else tk.BooleanVar()
        self._command = command
        self._box = box
        self._font = font or f(10)

        self._cv = tk.Canvas(
            self, width=box, height=box, background=pbg,
            highlightthickness=0, bd=0, cursor="hand2",
        )
        self._cv.pack(side="left")
        self._lbl = tk.Label(
            self, text=text, background=pbg, foreground=COLORS.text_2,
            font=self._font, cursor="hand2",
        )
        self._lbl.pack(side="left", padx=(7, 0))

        for w in (self._cv, self._lbl):
            w.bind("<Button-1>", self.toggle)
            w.bind("<Enter>", lambda e: self._lbl.configure(foreground=COLORS.text))
            w.bind("<Leave>", lambda e: self._lbl.configure(foreground=COLORS.text_2))

        self.var.trace_add("write", lambda *a: self._draw())
        self._draw()

    def _draw(self):
        c, s = self._cv, self._box
        c.delete("all")
        if self.var.get():
            round_rect(c, 1, 1, s - 1, s - 1, 5,
                       fill=COLORS.primary, outline=COLORS.primary)
            c.create_line(
                s * 0.28, s * 0.52, s * 0.44, s * 0.68, s * 0.73, s * 0.34,
                fill="#FFFFFF", width=2, capstyle="round", joinstyle="round",
            )
        else:
            round_rect(c, 1.5, 1.5, s - 1.5, s - 1.5, 5,
                       fill=COLORS.surface, outline=COLORS.border, width=1.5)

    def toggle(self, _event=None):
        self.var.set(not self.var.get())
        if self._command:
            self._command()

    def get(self):
        return bool(self.var.get())


def divider(parent, pady=10, bg=None):
    """1px 分隔线（放在卡片内）。"""
    line = tk.Frame(parent, height=1, background=bg or COLORS.divider)
    line.pack(fill="x", pady=pady)
    return line
