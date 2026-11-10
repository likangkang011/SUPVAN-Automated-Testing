# -*- coding: utf-8 -*-
"""系统图片选择器适配层（跨 ROM）
========================================
背景：app 的「图片」功能改成调用**系统相册**（ACTION_PICK / PhotoPicker），
每家 ROM 的图库 UI 完全不同，写死一套定位只能在一台机器上跑通。已实测两台：

    OPPO ColorOS  包名 com.coloros.gallery3d
        首图 = android.widget.TimelineView，content-desc=",第 1 项,图片,,2026年11月9日 15:18"
        取消 = Button id=cancel，text=取消

    小米 MIUI     包名 com.miui.gallery
        首图 = FrameLayout，content-desc="照片，2026年11月3日 15:57:9"
        取消 = Button id=button1，content-desc=取消

两家的 id / class / 描述全不一样，但有三条**跨厂商不变**的事实：
  1. 图库是独立包 → 用 driver.current_package 判断「已进图库」，不用 sleep 猜；
  2. 缩略图的 content-desc 一定带日期，且「最新一张」排在最前；
  3. 单选模式点一下自动回到 app，**没有「完成」按钮**
     （所以不能再等 app 自带的 ps_tv_complete）。

用法（点完「相册」之后一行搞定）：
    from utils.photo_picker import pick_first_photo
    wait_for_element(driver, *LOCATORS["photo_album"]).click()
    pick_first_photo(driver)          # 识别图库 → 选最新一张 → 等回到 app

新增机型：在 PICKER_PROFILES 里按图库包名加一条候选定位即可；
没登记的 ROM 会自动走 locators.py 的 "photo_pick_first" 通用语义候选兜底。
"""

import time

from appium.webdriver.common.appiumby import AppiumBy

from locators import LOCATORS, MULTI
from utils.element_helper import (
    ElementLocateError,
    _dump_artifacts,
    find_any,
    tap_element,
)
from utils.logger import get_logger

logger = get_logger("photo_picker")

# app 自己的包名（判断"是否已切到系统图库"的基准）
APP_PACKAGE = "com.fhit.app_iprinter"

# 各厂商图库的专属候选定位（按 driver.current_package 匹配），命中会排在通用候选前面。
# 这里只放**实测过**的写法；新机型调试时先从失败日志里抓首图的 class + content-desc 再补进来。
PICKER_PROFILES = {
    # OPPO / realme / 一加（ColorOS）
    "com.coloros.gallery3d": (
        (AppiumBy.XPATH, '//android.widget.TimelineView[contains(@content-desc,"第 1 项")]'),
    ),
    # 小米 / 红米（MIUI / HyperOS）
    # 「照片，2026年11月3日 15:57:9」；用 string-length>3 排除同名的「照片」tab
    "com.miui.gallery": (
        (AppiumBy.XPATH, '(//*[starts-with(@content-desc,"照片") and string-length(@content-desc) > 3])[1]'),
    ),
}

# 多选模式的 ROM 才会出现「完成/确定」（定位见 locators.py 的 photo_pick_confirm）


def _app_package(driver, override=None):
    """取 app 包名：显式传参 > capabilities.appPackage > 默认常量。"""
    if override:
        return override
    try:
        caps = driver.capabilities or {}
    except Exception:
        caps = {}
    return caps.get("appPackage") or APP_PACKAGE


def current_package(driver):
    """当前前台包名；取不到返回 None。"""
    try:
        return driver.current_package
    except Exception:
        return None


def wait_enter_picker(driver, app_package=APP_PACKAGE, timeout=10.0, poll=0.25):
    """等前台从 app 切到系统图库，返回图库包名；超时返回 None。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        pkg = current_package(driver)
        if pkg and pkg != app_package:
            return pkg
        time.sleep(poll)
    return None


def wait_back_app(driver, app_package=APP_PACKAGE, timeout=8.0, poll=0.2):
    """等前台回到 app，返回是否回来了。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if current_package(driver) == app_package:
            return True
        time.sleep(poll)
    return False


def _fail(driver, message, name="photo_pick_first"):
    """统一的失败处理：落盘现场 + 点名报错。"""
    png, xml = _dump_artifacts(driver, f"photo_picker_{current_package(driver)}")
    lines = ["", "=" * 72, f"❌ 系统相册选图失败：{message}"]
    if png:
        lines.append(f"   失败截图：{png}")
    if xml:
        lines.append(f"   页面源码：{xml}")
    lines.append("   → 若是新 ROM，请从页面源码里找首图的 class + content-desc，")
    lines.append("     补到 utils/photo_picker.py 的 PICKER_PROFILES 或 locators.py 的 photo_pick_first")
    lines.append("=" * 72)
    msg = "\n".join(lines)
    logger.error(msg)
    raise ElementLocateError(msg, key=name)


def pick_first_photo(driver, app_package=None, enter_timeout=10.0, back_timeout=8.0,
                     candidate_timeout=1.5):
    """在系统相册里选中**第一张（最新那张）**并等回到 app。

    调用前请先点完 app 里的「相册」（LOCATORS["photo_album"]）。

    :param app_package: app 包名，默认从 capabilities 取
    :param enter_timeout: 等系统图库弹出的最长时间（秒）
    :param back_timeout: 选完等回到 app 的最长时间（秒）
    :param candidate_timeout: 每个候选定位的等待时间（秒）
    :return: True 表示已选好并回到 app
    :raise ElementLocateError: 没进图库 / 找不到首图 / 选完回不到 app
    """
    app_pkg = _app_package(driver, app_package)

    # 1) 等系统图库弹出（不同 ROM 弹层动画快慢不一，用包名判定而不是 sleep）
    picker_pkg = wait_enter_picker(driver, app_pkg, enter_timeout)
    if not picker_pkg:
        _fail(driver, f"点了「相册」后 {enter_timeout:.0f}s 内没有切到系统图库"
                      f"（当前仍是 {current_package(driver)}）")
    logger.info("📷 已进入系统图库：%s", picker_pkg)

    # 2) 先试该 ROM 的专属定位，再试通用语义候选
    candidates = tuple(PICKER_PROFILES.get(picker_pkg, ())) + tuple(LOCATORS["photo_pick_first"][1])
    element = find_any(driver, MULTI, candidates, timeout=candidate_timeout,
                       name="photo_pick_first")

    # 3) 点选第一张（自绘控件常吞 click，失败会按元素中心坐标补点）
    if not tap_element(driver, element):
        _fail(driver, f"首图元素已找到但点不动：{picker_pkg}")
    logger.info("👆 已点选相册第一张（%s）", picker_pkg)

    # 4) 单选模式会自动返回；多选模式还要点「完成/确定」
    if wait_back_app(driver, app_pkg, back_timeout):
        logger.info("✅ 选图完成，已回到 app")
        return True

    logger.info("⏳ 仍停在图库（可能是多选模式），尝试点「完成/确定」")
    try:
        confirm = find_any(driver, MULTI, LOCATORS["photo_pick_confirm"][1],
                           timeout=1.0, name="photo_pick_confirm")
    except ElementLocateError:
        logger.warning("⚠️ 没找到「完成/确定」按钮，继续等待返回 app")
    else:
        tap_element(driver, confirm)
        if wait_back_app(driver, app_pkg, back_timeout):
            logger.info("✅ 选图完成，已回到 app（点了完成）")
            return True

    _fail(driver, f"已点选第一张，但 {back_timeout:.0f}s 内没回到 app"
                  f"（当前 {current_package(driver)}）")
