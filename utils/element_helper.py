# -*- coding: utf-8 -*-
"""
元素定位统一封装（带「定位失败点名」能力）
================================================

解决两个痛点：
  1. 元素定位失败时，报错信息说不清是哪个元素 —— 这里通过反向索引把
     (by, locator) 还原成 locators.py 里的语义化 key，直接在日志/报告里点名。
  2. 失败后脚本还往下跑、日志难看 —— 失败立即抛出 ElementLocateError，
     同时落盘「截图 + 页面源码 + 相似元素建议」，一步到位。


用法一（推荐，零改动迁移：和原来完全一样的调用姿势）
------------------------------------------------------
    from utils.element_helper import wait_for_element, wait_clickable
    wait_for_element(driver, *LOCATORS["create_new"]).click()

用法二（直接用语义 key，日志更可读）
------------------------------------------------------
    from utils.element_helper import find, click_key
    find(driver, "create_new").click()
    click_key(driver, "confirm")
"""
import os
import re
import difflib
import logging
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from locators import LOCATORS
from utils.logger import get_logger

logger = get_logger("element")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ARTIFACT_DIR = os.path.join(_PROJECT_ROOT, "logs", "failure_artifacts")

# ---------- 反向索引：(by, locator) -> LOCATORS 里的语义化 key ----------
_REVERSE_INDEX = {}
for _key, _loc in LOCATORS.items():
    _REVERSE_INDEX.setdefault(tuple(_loc), _key)


class ElementLocateError(AssertionError):
    """元素定位失败。

    继承 AssertionError：pytest 会把它归类为「断言失败」而不是「用例错误」，
    报告更直观，且会触发 conftest 里的失败截图钩子。
    """

    def __init__(self, message, key=None, by=None, locator=None, timeout=None):
        super().__init__(message)
        self.key = key
        self.by = by
        self.locator = locator
        self.timeout = timeout


def _key_of(by, locator):
    """把定位方式还原成 locators.py 中的 key，找不到返回 None。"""
    return _REVERSE_INDEX.get((by, locator))


def _describe(by, locator, name=None):
    """生成人类可读的元素描述，例如：『create_new』 by=id locator=com.xxx/id/ivCreateNew"""
    key = name or _key_of(by, locator)
    tag = f"『{key}』" if key else "『未在 locators.py 登记』"
    return f"{tag} [by={by}, locator={locator}]"


def _similar_ids(driver, locator):
    """从当前页面源码里，找出与被查找 id 相似的元素（疑似改名后的控件）。"""
    if not isinstance(locator, str) or "/" not in locator:
        return []
    try:
        src = driver.page_source
    except Exception:
        return []
    suffix = locator.split("/")[-1]
    all_suffix = {i.split("/")[-1] for i in re.findall(r'resource-id="([^"]+)"', src)}
    return difflib.get_close_matches(suffix, sorted(all_suffix), n=5, cutoff=0.5)


def _dump_artifacts(driver, desc):
    """定位失败时落盘现场：截图 + 页面源码。返回 (png路径, xml路径)。"""
    try:
        os.makedirs(_ARTIFACT_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = re.sub(r"[^\w\u4e00-\u9fa5]+", "_", desc)[:60].strip("_")
        png = os.path.join(_ARTIFACT_DIR, f"{ts}_{safe}.png")
        xml = os.path.join(_ARTIFACT_DIR, f"{ts}_{safe}.xml")
        driver.save_screenshot(png)
        with open(xml, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        return png, xml
    except Exception as e:  # 兜底：绝不能因为保存现场而掩盖真正的定位错误
        logger.warning("保存失败现场时出错：%s", e)
        return None, None


def _wait(driver, by, locator, condition, timeout, name=None):
    """所有等待函数的统一内核。"""
    desc = _describe(by, locator, name)
    logger.info("⏳ 等待元素 %s（最多 %ss）", desc, timeout)

    try:
        element = WebDriverWait(driver, timeout).until(condition((by, locator)))
    except TimeoutException:
        similar = _similar_ids(driver, locator)
        png, xml = _dump_artifacts(driver, desc)

        lines = [
            "",
            "=" * 72,
            f"❌ 元素定位失败：{desc}",
            f"   等待条件：{condition.__name__}",
            f"   超时时间：{timeout}s",
        ]
        if similar:
            lines.append(f"   当前页面相似元素（疑似改名）：{similar}")
        if png:
            lines.append(f"   失败截图：{png}")
        if xml:
            lines.append(f"   页面源码：{xml}")
        lines.append("   → 请排查：是否被改名 / 未加载 / 被弹窗遮挡 / 需先滑动，或同步更新 locators.py")
        lines.append("=" * 72)
        msg = "\n".join(lines)

        logger.error(msg)
        raise ElementLocateError(
            msg,
            key=name or _key_of(by, locator),
            by=by,
            locator=locator,
            timeout=timeout,
        )

    logger.info("✅ 命中元素 %s", desc)
    return element


# ============================ 对外等待 API ============================
# 签名与原来测试文件里的本地函数完全一致，可直接替换导入。

def wait_for_element(driver, by, locator, timeout=10, name=None):
    """等待元素可见（等价于 EC.visibility_of_element_located）。"""
    return _wait(driver, by, locator, EC.visibility_of_element_located, timeout, name)


def wait_visible(driver, by, locator, timeout=20, name=None):
    """等待元素可见（兼容旧命名，默认超时 20s）。"""
    return _wait(driver, by, locator, EC.visibility_of_element_located, timeout, name)


def wait_present(driver, by, locator, timeout=10, name=None):
    """等待元素出现在 DOM（不要求可见）。"""
    return _wait(driver, by, locator, EC.presence_of_element_located, timeout, name)


def wait_clickable(driver, by, locator, timeout=20, name=None):
    """等待元素可点击。"""
    return _wait(driver, by, locator, EC.element_to_be_clickable, timeout, name)


def wait_disappear(driver, by, locator, timeout=20, name=None):
    """等待元素消失。不抛错，超时返回 False（保持原有语义）。"""
    desc = _describe(by, locator, name)
    logger.info("⏳ 等待元素消失 %s（最多 %ss）", desc, timeout)
    try:
        return bool(
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((by, locator))
            )
        )
    except TimeoutException:
        logger.warning("⚠️ 元素在 %ss 内未消失：%s", timeout, desc)
        return False


# ============================ 常用动作快捷方式 ============================

def click(driver, by, locator, timeout=20, name=None):
    """等待可点击并点击。"""
    return wait_clickable(driver, by, locator, timeout, name).click()


def input_text(driver, by, locator, text, timeout=10, name=None, clear=True):
    """等待可见并输入文本。"""
    element = wait_visible(driver, by, locator, timeout, name)
    if clear:
        element.clear()
    element.send_keys(text)
    logger.info("⌨️ 已输入内容：%r → %s", text, _describe(by, locator, name))
    return element


# ============================ 按语义 key 调用 ============================

_CONDITIONS = {
    "visible": EC.visibility_of_element_located,
    "present": EC.presence_of_element_located,
    "clickable": EC.element_to_be_clickable,
}


def find(driver, key, timeout=10, condition="visible"):
    """直接用 locators.py 的 key 定位，例如 find(driver, "create_new")。

    :param key: locators.py 中的语义化 key
    :param condition: "visible" | "present" | "clickable"
    """
    if key not in LOCATORS:
        raise KeyError(f"locators.py 中不存在 key：{key}")
    if condition not in _CONDITIONS:
        raise ValueError(f"condition 只能是 {list(_CONDITIONS)}，收到：{condition}")
    by, locator = LOCATORS[key]
    return _wait(driver, by, locator, _CONDITIONS[condition], timeout, name=key)


def click_key(driver, key, timeout=20):
    """按 key 等待可点击并点击。"""
    by, locator = LOCATORS[key]
    return _wait(driver, by, locator, EC.element_to_be_clickable, timeout, name=key).click()
