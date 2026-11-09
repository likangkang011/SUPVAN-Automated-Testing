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
import time
import difflib
import logging
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from locators import COORDINATE, LOCATORS
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


def _wait(driver, by, locator, condition, timeout, name=None, recover=True):
    """所有等待函数的统一内核。

    :param recover: 超时后先尝试关掉「首次连接引导弹窗」再重试一次（弹窗会挡住底层所有元素，
                    且它常在点完「新建」后几秒才淡入，早期版本用 3s 的 click_if_present 经常抢跑）
    """
    desc = _describe(by, locator, name)
    logger.info("⏳ 等待元素 %s（最多 %ss）", desc, timeout)

    try:
        element = WebDriverWait(driver, timeout).until(condition((by, locator)))
    except TimeoutException:
        # 兜底一：被首次连接引导弹窗挡住 → 点掉它，再等一次
        if recover and dismiss_first_connect_guide(driver, timeout=0.6):
            logger.info("🔁 引导弹窗已关闭，重新等待 %s", desc)
            try:
                element = WebDriverWait(driver, timeout).until(condition((by, locator)))
                logger.info("✅ 命中元素 %s（关闭弹窗后）", desc)
                return element
            except TimeoutException:
                pass

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


def tap_ratio(driver, by, ratio, name=None, tap_duration=0.1, times=1, interval=0.1):
    """按屏幕比例盲点（元素坐标点击）。

    用于「元素定位彻底失效、只能盲点」的场景：坐标统一写在 locators.py 里
    （值形如 ``(COORDINATE, (0.5, 2 / 3))``），用例只引用 key：

        tap_ratio(driver, *LOCATORS["view"])                 # 单击
        tap_ratio(driver, *LOCATORS["paint_view"], times=2)  # 双击（进编辑）

    坐标是**比例**不是像素，运行时按 ``driver.get_window_size()`` 换算，
    所以换手机 / 模拟器 / 分辨率都不用改 locators.py。

    :param by: 必须是 locators.py 的 ``COORDINATE`` 占位符，传别的会直接报错
    :param ratio: (x_ratio, y_ratio)，屏幕宽、高的比例（0~1），如 (0.5, 2/3)
    :param name: 日志里的名字，不传则反查 locators.py 的 key
    :param tap_duration: 按下与抬起之间的间隔（秒）
    :param times: 连击次数，2 就是双击（安卓双击阈值内）
    :param interval: 连击之间的间隔（秒）
    :return: 实际点击的像素坐标 (x, y)
    """
    if by != COORDINATE:
        raise ValueError(
            "tap_ratio 只接受 locators.py 的坐标条目 "
            f"(COORDINATE, (x比例, y比例))，收到 by={by!r}；普通元素请用 click()/wait_for_element()"
        )
    try:
        x_ratio, y_ratio = ratio
    except (TypeError, ValueError):
        raise ValueError(f"坐标条目格式应为 (x比例, y比例)，收到 {ratio!r}")

    desc = _describe(by, ratio, name)
    size = driver.get_window_size()
    x, y = int(size["width"] * float(x_ratio)), int(size["height"] * float(y_ratio))
    logger.info(
        "👆 坐标盲点 %s：比例 (%.3f, %.3f) → 像素 (%d, %d)（屏幕 %dx%d，%d 连击）",
        desc, x_ratio, y_ratio, x, y, size["width"], size["height"], times,
    )

    try:
        builder = ActionBuilder(driver)
        builder.add_pointer_input(interaction.POINTER_TOUCH, "touch")
        touch = builder.pointer_action
        for i in range(int(times)):
            if i:
                touch.pause(interval)
            touch.move_to_location(x=x, y=y)
            touch.pointer_down(button=0)
            touch.pause(tap_duration)
            touch.pointer_up(button=0)
        builder.perform()
    except Exception as e:
        raise ElementLocateError(
            f"❌ 坐标点击失败 {desc}：像素 ({x}, {y})，原因：{e}",
            key=name,
            by=by,
            locator=ratio,
        )

    logger.info("✅ 已点击坐标 %s → (%d, %d)", desc, x, y)
    return x, y


def click_if_present(driver, by, locator, timeout=3, name=None, poll_frequency=0.3):
    """可选元素：出现就点，不出现就静默跳过。

    用于「有时弹、有时不弹」的引导页 / 提示弹窗关闭按钮这类元素：
    - 不抛 ElementLocateError，也不会落失败现场（logs/failure_artifacts 不会被污染）
    - 只会等 timeout 秒（默认 3s），不拖慢主流程
    - 元素出现但点击失败时只告警，不影响后续步骤

    :return: True 表示点到了，False 表示没出现 / 没点成、已忽略
    """
    desc = _describe(by, locator, name)
    logger.info("🔍 检查可选元素 %s（最多等 %ss，未出现则忽略）", desc, timeout)
    try:
        element = WebDriverWait(driver, timeout, poll_frequency=poll_frequency).until(
            EC.element_to_be_clickable((by, locator))
        )
    except TimeoutException:
        logger.info("➖ 可选元素未出现，跳过：%s", desc)
        return False

    try:
        element.click()
    except Exception as e:
        logger.warning("⚠️ 可选元素已出现但点击失败，已忽略：%s（%s）", desc, e)
        return False

    logger.info("✅ 已点击可选元素 %s", desc)
    return True


# ==================== 首次连接引导弹窗（会盖住整个编辑页） ====================
# 这个弹窗在点完「新建 / 新增标签」后几秒才淡入，只要它在，底层元素全都查不到。
# 老写法 click_if_present 有两个坑：
#   ① 只等 3s —— 弹窗淡入往往在 2~6s，经常"抢跑"失败；
#   ② 用的是 element_to_be_clickable（要求 is_enabled），关闭键是自绘 ImageView，
#      属性不稳定，可能永远等不到 —— 日志就成了「弹窗明明在，却说未出现」。
# 这里改成：轮询 find_elements + visibility 判定 → 点 → 校验是否真的消失 → 没消失按
# 元素中心坐标补点一次。全程不抛异常，可被 _wait 当兜底调用。

def _is_visible(element):
    try:
        return bool(element.is_displayed())
    except Exception:
        return False


def _visible_elements(driver, by, locator):
    """当前页面上该定位里「可见」的元素列表（查不到/异常时返回空列表）。"""
    try:
        return [el for el in driver.find_elements(by, locator) if _is_visible(el)]
    except Exception:
        return []


def _safe_rect(element):
    try:
        return element.rect
    except Exception:
        return None


def _click_element_or_point(driver, element):
    """先 element.click()；失败或无效时按元素中心坐标补一枪。"""
    try:
        element.click()
        return True
    except Exception as e:
        logger.warning("⚠️ 元素 click 失败（%s），改用元素中心坐标点击", e)
    try:
        rect = element.rect
        driver.tap([(rect["x"] + rect["width"] // 2, rect["y"] + rect["height"] // 2)])
        return True
    except Exception as e:
        logger.warning("⚠️ 坐标补点也失败：%s", e)
        return False


def _wait_until_gone(driver, by, locator, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _visible_elements(driver, by, locator):
            return True
        time.sleep(0.2)
    return False


def dismiss_first_connect_guide(driver, timeout=10.0, poll=0.25, key="first_connection_close"):
    """「首次连接设备」引导弹窗：等到出现就点掉；没出现就静默返回 False。

    :param timeout: 最长等多久（秒）。弹窗常在点完「新建」后 2~6s 才淡入，太小会抢跑
    :param poll: 轮询间隔（秒）
    :param key: locators.py 里关闭按钮的 key
    :return: True 表示确实关掉了；False 表示没出现 / 关不掉（都会写日志）
    """
    if key not in LOCATORS:
        logger.warning("locators.py 里没有 key：%s", key)
        return False

    by, locator = LOCATORS[key]
    desc = _describe(by, locator, key)
    if timeout >= 1:                      # 被 _wait 当兜底探测时（0.6s）不刷这行日志
        logger.info("🔍 等待首次连接引导弹窗 %s（最多 %.0fs，出现就点掉）", desc, timeout)

    deadline = time.time() + timeout
    while time.time() < deadline:
        targets = _visible_elements(driver, by, locator)
        if targets:
            logger.info("👆 发现引导弹窗，点击关闭 %s", desc)
            for el in targets:
                _click_element_or_point(driver, el)
            if _wait_until_gone(driver, by, locator, 2.0):
                logger.info("✅ 引导弹窗已关闭")
                return True

            logger.warning("⚠️ 关闭按钮点过但弹窗还在（位置 %s），重试一次", _safe_rect(targets[0]))
            for el in _visible_elements(driver, by, locator):
                _click_element_or_point(driver, el)
            if _wait_until_gone(driver, by, locator, 2.0):
                logger.info("✅ 引导弹窗已关闭（重试成功）")
                return True

            logger.error("❌ 引导弹窗点不掉：%s（位置 %s）→ 请确认 %s 是否仍是关闭按钮",
                         desc, _safe_rect(targets[0]), locator)
            return False
        time.sleep(poll)

    logger.info("➖ 未出现首次连接引导弹窗，继续")
    return False


def input_text(driver, by, locator, text, timeout=10, name=None, clear=True):
    """等待可见并输入文本。"""
    element = wait_visible(driver, by, locator, timeout, name)
    if clear:
        element.clear()
    element.send_keys(text)
    logger.info("⌨️ 已输入内容：%r → %s", text, _describe(by, locator, name))
    return element


# ==================== 视口判定 / 滚动到可见（「找得到但点不到」专用） ====================
# 背景：UiAutomator2 对「滚出屏幕」的控件仍会返回 displayed=true（只要控件 attach、
# 有 bounds 就行），于是 wait_for_element 打 ✅，紧接着 click() 按元素**中心坐标**
# 注入触摸 —— 中心点在屏幕外，这次点击被系统丢弃，页面毫无反应。这就是
# 「元素明明能找到、inspector 里也能点，脚本却点了没效果」的典型成因。

def is_in_viewport(driver, element, margin=0):
    """元素是否**完整**落在屏幕可视区内（用真实 rect 判定，不看 is_displayed）。"""
    try:
        rect = element.rect
    except Exception:          # 元素已被回收/页面已切换
        return False
    size = driver.get_window_size()
    return (
        rect["x"] >= margin
        and rect["y"] >= margin
        and rect["x"] + rect["width"] <= size["width"] - margin
        and rect["y"] + rect["height"] <= size["height"] - margin
    )


def _swipe_vertical(driver, x, direction, ratio=0.45, duration=300, reason="补齐视口"):
    """在屏幕中部做一次纵向滑动，用来把列表内容滚上来 / 滚下去。

    :param x: 手指的横向位置（传元素中心 x，保证手势落在同一个滚动容器里）
    :param direction: "up" 手指上滑（内容上移，看下面的东西）/ "down" 反之
    :param reason: 只用于日志，说明这次滑动是为了什么
    """
    size = driver.get_window_size()
    height, width = size["height"], size["width"]
    x = int(min(max(x, width * 0.2), width * 0.8))     # 夹在屏内，别滑到边角
    if direction == "up":
        y1, y2 = int(height * 0.75), int(height * (0.75 - ratio))
    else:
        y1, y2 = int(height * 0.25), int(height * (0.25 + ratio))
    logger.info("↕️ 纵向滑动（%s，%s）：(%d, %d) → (%d, %d)", reason, direction, x, y1, x, y2)
    driver.swipe(x, y1, x, y2, duration)


def scroll_into_view(driver, by, locator, timeout=10, max_swipe=3, name=None,
                     settle=0.4):
    """定位元素，并保证它完整落在屏幕内；不在就朝它的方向滑，最多 max_swipe 次。

    用法与 wait_for_element 一致，只是多了一步「滚到可见」：

        scroll_into_view(driver, *LOCATORS["download_more_font"]).click()

    元素在下方 → 手指上滑；元素在上方（滑过头了）→ 手指下滑。滑完等 settle 秒
    让惯性/回弹结束再重新取 rect，避免读到动画中途的旧坐标。

    :raise ElementLocateError: 元素存在但滑 max_swipe 次仍不在屏幕内
    """
    desc = _describe(by, locator, name)
    element = wait_visible(driver, by, locator, timeout, name)
    size = driver.get_window_size()

    for i in range(max_swipe + 1):
        if is_in_viewport(driver, element):
            logger.info("✅ 元素已完整落在屏幕内 %s（第 %d 次判定）", desc, i + 1)
            return element
        if i == max_swipe:
            break
        try:
            rect = element.rect
        except Exception:
            rect = {"x": 0, "y": 0, "width": 0, "height": 0}
        # 元素中心比屏幕底还靠下 → 要往上滑；反之往下滑
        direction = "up" if rect["y"] + rect["height"] > size["height"] else "down"
        _swipe_vertical(driver, rect["x"] + rect["width"] // 2, direction)
        time.sleep(settle)
        element = wait_visible(driver, by, locator, timeout, name)

    try:
        rect = element.rect
    except Exception:
        rect = None
    msg = "\n".join([
        "",
        "=" * 72,
        f"❌ 元素存在但不在屏幕可视区：{desc}",
        f"   元素位置：{rect}，屏幕：{size['width']}x{size['height']}",
        f"   已尝试滑动 {max_swipe} 次仍未进入视口",
        "   → is_displayed() 对滚出视口的控件仍为 True，click() 会点到屏幕外，等于没点。",
        "   → 请加大 max_swipe，或改用手势让容器自己滚（mobile: scrollGesture）。",
        "=" * 72,
    ])
    logger.error(msg)
    raise ElementLocateError(msg, key=name or _key_of(by, locator), by=by, locator=locator)


def click_in_view(driver, by, locator, timeout=10, max_swipe=3, name=None):
    """滚动到可见后点击（scroll_into_view + click 的简写）。"""
    return scroll_into_view(driver, by, locator, timeout, max_swipe, name).click()


# ============ 找不到就滑一下再找（列表项还没渲染出来） ============
# 和 scroll_into_view 的区别：
#   scroll_into_view 解决「元素已在页面里、只是滚出视口」（is_displayed 仍为 True）；
#   这里解决「元素根本没被渲染」—— RecyclerView / 长列表只渲染可见项，
#   没滚到那一条时 find_elements 直接返回空，等再久也等不到。
# 典型场景：连接设备页的设备列表（rvBluetoothList），目标机器排在下面要滑才出来。

def _poll_visible(driver, by, locator, timeout, poll=0.25):
    """在 timeout 秒内轮询「可见元素」，返回第一个；没有就返回 None（不抛错、不落现场）。"""
    deadline = time.time() + timeout
    while True:
        elements = _visible_elements(driver, by, locator)
        if elements:
            return elements[0]
        if time.time() >= deadline:
            return None
        time.sleep(poll)


def _same_id_texts(driver, locator):
    """从 XPath 里取出 resource-id，列出页面上该 id 现有的 text（滚动后仍找不到时的诊断）。"""
    if not isinstance(locator, str):
        return []
    m = re.search(r'resource-id\s*=\s*"([^"]+)"', locator)
    if not m:
        return []
    rid = m.group(1)
    try:
        src = driver.page_source
        if callable(src):          # 兼容把 page_source 实现成方法的驱动/假对象
            src = src()
        if not isinstance(src, str):
            return []
    except Exception:
        return []
    texts = []
    for node in re.findall(r"<[^>]*>", src):
        if f'resource-id="{rid}"' in node:
            t = re.search(r'\btext="([^"]*)"', node)
            if t and t.group(1):
                texts.append(t.group(1))
    return texts


def find_with_swipe(driver, by, locator, timeout=2, max_swipe=5, name=None,
                    direction="up", settle=0.5, swipe_duration=400):
    """找元素；**找不到就滑一下再继续找**，最多滑 max_swipe 次。

    用法和 wait_for_element 一致，只是多了「滑」这一步：

        find_with_swipe(
            driver, By.XPATH,
            f'//android.widget.TextView[@resource-id="...adapter_find_device_mac" and @text="{device_number1}"]'
        ).click()

    每轮逻辑：
      1. 先轮询 timeout 秒（页面刚切过来时列表还在加载）；
      2. 找不到 → 手指在屏幕中部上滑（让列表滚出更多项）→ 等 settle 秒 → 回到 1；
      3. 找到了但被裁在屏幕外 → 朝它所在的方向滑（同上）；
      4. 滑满 max_swipe 次仍找不到 → 落盘现场 + 抛出点名报错（带上同 id 现有内容）。

    :param timeout: 每一轮最多等多久（秒）
    :param max_swipe: 最多滑几次
    :param direction: "up"（手指上滑，看列表下面）/ "down"（手指下滑，看列表上面）
    :param settle: 每次滑动后等多久（等惯性/回弹结束再重新找）
    :param swipe_duration: 单次滑动时长（ms），太快容易变 fling 甩过站
    :raise ElementLocateError: 滑完仍然找不到
    """
    desc = _describe(by, locator, name)
    size = driver.get_window_size()
    logger.info("🔎 查找元素 %s（未找到就%s滑继续找，最多 %d 次）",
                desc, "上" if direction == "up" else "下", max_swipe)

    for i in range(max_swipe + 1):
        element = _poll_visible(driver, by, locator, timeout)
        step_dir = direction

        if element is not None:
            try:
                rect = element.rect
            except Exception:
                rect = None
            if rect and is_in_viewport(driver, element):
                logger.info("✅ 命中元素 %s（第 %d 次查找）", desc, i + 1)
                return element
            if rect:      # 渲染出来了但被屏幕裁掉：朝它的方向滑
                step_dir = "up" if rect["y"] + rect["height"] > size["height"] else "down"
                logger.info("↕️ 元素已渲染但不在视口内 %s：rect=%s（屏幕 %dx%d）",
                            desc, rect, size["width"], size["height"])

        if i == max_swipe:
            break

        _swipe_vertical(driver, size["width"] // 2, step_dir,
                        duration=swipe_duration, reason=f"第 {i + 1} 次滑动查找")
        time.sleep(settle)

    # 滑到底（或滑到顶）都没有 → 把现场和"同 id 现有内容"一起报出来
    found_texts = _same_id_texts(driver, locator)
    png, xml = _dump_artifacts(driver, desc)
    lines = [
        "",
        "=" * 72,
        f"❌ 滑动查找失败：找不到元素 {desc}",
        f"   已{'上' if direction == 'up' else '下'}滑 {max_swipe} 次仍未见该元素（屏幕 {size['width']}x{size['height']}）",
    ]
    if found_texts:
        lines.append(f"   页面上同一 id 现有内容：{found_texts}")
        lines.append("   → 目标值不在上面这几个里，请核对 locators / 参数里的编号是否写错")
    if png:
        lines.append(f"   失败截图：{png}")
    if xml:
        lines.append(f"   页面源码：{xml}")
    lines.append("   → 也可能列表还没加载完，可加大 timeout / max_swipe 后重试")
    lines.append("=" * 72)
    msg = "\n".join(lines)
    logger.error(msg)
    raise ElementLocateError(msg, key=name or _key_of(by, locator), by=by, locator=locator)


def click_with_swipe(driver, by, locator, timeout=2, max_swipe=5, name=None,
                     direction="up", settle=0.5, swipe_duration=400):
    """找不到就滑一下再找，找到后点击（find_with_swipe + click 的简写）。"""
    return find_with_swipe(
        driver, by, locator, timeout, max_swipe, name, direction, settle, swipe_duration
    ).click()


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
