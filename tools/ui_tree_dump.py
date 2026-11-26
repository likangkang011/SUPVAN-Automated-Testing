# -*- coding: utf-8 -*-
"""
App UI 控件树抓取工具
=====================
用途：逐页 dump App 的真实控件树（page_source），为 locators.py 补充/校验定位。

用法：
    python tools/ui_tree_dump.py home    # 首页 / 我的 / 连接设备 / 新建标签入口
    python tools/ui_tree_dump.py edit    # 编辑页 + 功能栏各入口弹窗
    python tools/ui_tree_dump.py text    # 文本元素各子面板（样式/字体/对齐/字效）
    python tools/ui_tree_dump.py more    # 模板/耗材/打印/保存
    python tools/ui_tree_dump.py newui   # 家用风新版 UI
    python tools/ui_tree_dump.py all     # 依次跑上面全部

产物：
    logs/ui_dump/<序号_页面名>.xml     原始控件树（uiautomator2 层级）
    logs/ui_dump/<序号_页面名>.png     同时刻截图，便于人工对照
    logs/ui_dump/_manifest.json        本次抓取的页面索引
"""
import json
import os
import re
import sys
import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "logs", "ui_dump")
os.makedirs(OUT_DIR, exist_ok=True)

APPIUM_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
UDID = os.getenv("ANDROID_UDID", "4b66ddf")
APP_PACKAGE = "com.fhit.app_iprinter"
APP_ACTIVITY = ".ui.home.activity.HomeActivity"

PREFIX = f"{APP_PACKAGE}:id/"

_manifest = []
_seq = [0]


# --------------------------------------------------------------------------
# session
# --------------------------------------------------------------------------
def create_driver():
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.device_name = UDID
    opts.udid = UDID
    opts.app_package = APP_PACKAGE
    opts.app_activity = APP_ACTIVITY
    opts.auto_grant_permissions = True
    opts.no_reset = True                 # 保留登录态/已连设备，避免每次从头来
    opts.new_command_timeout = 900
    opts.skip_device_initialization = True
    # 首次安装/重启后 instrumentation 启动较慢，默认 60s 容易超时
    opts.set_capability("uiautomator2ServerLaunchTimeout", 180000)
    opts.set_capability("uiautomator2ServerInstallTimeout", 120000)
    # 建 session 时会初始化 NotificationListener，它强依赖 UiAutomation，
    # 设备上 UiAutomation 未连接时直接抛 "UiAutomation not connected"。
    # 本工具只抓控件树，不需要通知栏，关掉即可绕开该故障点。
    opts.set_capability("enableNotificationListener", False)
    opts.set_capability("disableWindowAnimation", True)
    print(f"[session] 连接 Appium {APPIUM_URL} / {UDID}")
    driver = webdriver.Remote(APPIUM_URL, options=opts)
    # noReset 场景下 Appium 不保证拉起 AUT，显式激活一次，避免抓到桌面控件树
    try:
        driver.activate_app(APP_PACKAGE)
    except Exception as e:
        print(f"[session] activate_app 失败：{e}")
    time.sleep(2.5)
    return driver


def dismiss_system_popups(driver, rounds=3):
    """关掉系统权限/引导弹窗：始终允许、允许、我知道了、跳过。"""
    labels = ["始终允许", "仅使用期间允许", "允许", "我知道了", "知道了", "跳过", "同意"]
    for _ in range(rounds):
        hit = False
        for text in labels:
            try:
                els = driver.find_elements(AppiumBy.XPATH, f'//*[@text="{text}"]')
            except Exception:
                continue
            for el in els:
                try:
                    if el.is_displayed():
                        el.click()
                        print(f"[popup] 点击「{text}」")
                        hit = True
                        time.sleep(0.8)
                        break
                except Exception:
                    pass
            if hit:
                break
        if not hit:
            break


# --------------------------------------------------------------------------
# 基础动作
# --------------------------------------------------------------------------
def dump(driver, name):
    """把当前页面控件树 + 截图落盘。"""
    safe = re.sub(r"[^\w\u4e00-\u9fa5\-]+", "_", name)
    xml_path = os.path.join(OUT_DIR, f"{safe}.xml")
    png_path = os.path.join(OUT_DIR, f"{safe}.png")
    try:
        src = driver.page_source
    except Exception as e:
        print(f"[dump] ✗ {name} 取控件树失败：{e}")
        return False
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(src)
    try:
        driver.save_screenshot(png_path)
    except Exception:
        png_path = None
    ids = len(re.findall(r'resource-id="' + re.escape(PREFIX), src))
    pkgs = set(re.findall(r'package="([^"]+)"', src))
    _manifest.append({"name": safe, "xml": xml_path, "png": png_path,
                      "nodes_with_id": ids, "packages": sorted(pkgs)})
    print(f"[dump] ✓ {name}  ({ids} 个带 id 节点, 包={','.join(sorted(pkgs))[:60]})")
    return ids > 0


def find_visible(driver, by, loc, timeout=3.0):
    end = time.time() + timeout
    while time.time() < end:
        try:
            for el in driver.find_elements(by, loc):
                if el.is_displayed():
                    return el
        except Exception:
            pass
        time.sleep(0.3)
    return None


def tap(driver, by, loc, name=None, timeout=3.0, quiet=False):
    el = find_visible(driver, by, loc, timeout)
    if el is None:
        if not quiet:
            print(f"[tap] ✗ 未找到 {name or loc}")
        return False
    try:
        el.click()
    except Exception:
        try:
            r = el.rect
            driver.execute_script("mobile: clickGesture",
                                  {"x": r["x"] + r["width"] // 2, "y": r["y"] + r["height"] // 2})
        except Exception as e:
            print(f"[tap] ✗ {name or loc} 点击失败：{e}")
            return False
    print(f"[tap] ✓ {name or loc}")
    time.sleep(1.2)
    return True


def tap_text(driver, text, name=None, timeout=3.0, quiet=False):
    return tap(driver, AppiumBy.XPATH, f'//*[@text="{text}"]', name or text, timeout, quiet)


def tap_id(driver, rid, name=None, timeout=3.0, quiet=False):
    return tap(driver, AppiumBy.ID, PREFIX + rid, name or rid, timeout, quiet)


def press_back(driver, n=1, wait=1.2):
    for _ in range(n):
        try:
            driver.back()
        except Exception:
            pass
        time.sleep(wait)


def current_activity(driver):
    try:
        return driver.current_activity or ""
    except Exception:
        return ""


def back_to_home(driver):
    """通过底部「首页」tab 回首页；被弹窗挡住就先关弹窗，再退回/重启 App。"""
    # 编辑器里按返回会弹「是否保存模板」，先关掉，否则底部 tab 点不到
    for rid in ("tvCancel", "cvCancel", "tvNotSave"):
        tap_id(driver, rid, f"清弹窗-{rid}", 0.8, quiet=True)
    if tap_id(driver, "htwiHomePage", "底部-首页tab", 1.5, quiet=True):
        time.sleep(1.2)
        return True
    for _ in range(4):
        if current_activity(driver).endswith("HomeActivity"):
            return True
        press_back(driver)
    try:
        driver.activate_app(APP_PACKAGE)
        time.sleep(2.5)
    except Exception:
        pass
    return current_activity(driver).endswith("HomeActivity")


CLOSE_IDS = ("ivKataMyDialogLabelProduce", "ivKataMyDialogWireFrame", "ivClose",
             "iv_close", "ivCancel", "ivBack", "iv_back", "ivFirstConnectionClose",
             "tvCancel", "cvCancel", "tvNotSave")


def close_overlay(driver, tries=4):
    """关弹窗/返回上一级：先点关闭按钮，再点「取消/不保存」，最后退一步。"""
    for rid in CLOSE_IDS:
        if tap_id(driver, rid, f"关闭-{rid}", 1.0, quiet=True):
            return True
    for text in ("取消", "不保存", "关闭", "返回"):
        if tap_text(driver, text, f"关闭-{text}", 0.8, quiet=True):
            return True
    for _ in range(tries):
        if current_activity(driver).endswith("HomeActivity"):
            return True
        press_back(driver, 1, 0.8)
        return True
    return False


def swipe_bar_left(driver, y_ratio=0.755):
    """功能宫格是横向分页（ViewPager），在宫格高度上向左滑一页。

    y_ratio 用实测值：屏幕 1/4 处是画布，0.755 处才是功能图标行。
    """
    size = driver.get_window_size()
    w, h = size["width"], size["height"]
    y = int(h * y_ratio)
    driver.execute_script("mobile: swipeGesture", {
        "left": int(w * 0.10), "top": y - int(h * 0.02),
        "width": int(w * 0.80), "height": int(h * 0.04),
        "direction": "left", "percent": 0.85,
    })
    time.sleep(1.0)


def visible_feature_texts(driver):
    """当前宫格里可见的功能入口文字（tvKataMyObjectSetting）。

    直接解析 page_source 而不是读 element.text：宫格是 ViewPager，
    部分 TextView 的 text 属性取回来是空串，但控件树里是有 text 的。
    """
    try:
        src = driver.page_source
    except Exception:
        return []
    pat = r'resource-id="[^"]*tvKataMyObjectSetting"[^>]*text="([^"]+)"'
    pat2 = r'text="([^"]+)"[^>]*resource-id="[^"]*tvKataMyObjectSetting"'
    out = []
    for t in re.findall(pat, src) + re.findall(pat2, src):
        t = t.strip()
        if t and t not in out:
            out.append(t)
    return out


def next_name(tag):
    _seq[0] += 1
    return f"{_seq[0]:02d}_{tag}"


# --------------------------------------------------------------------------
# 阶段一：首页体系
# --------------------------------------------------------------------------
def phase_home(driver):
    dismiss_system_popups(driver)
    back_to_home(driver)
    dump(driver, next_name("首页"))

    # 我的
    if tap_id(driver, "htwiHomeMine", "底部-我的tab", 3):
        time.sleep(1.5)
        dismiss_system_popups(driver)
        dump(driver, next_name("我的"))
        # 我的 -> 各列表项：每次点之前先确认还在「我的」页
        for text in ("连接设备", "我的设备", "我的文件", "应用信息", "进入新版",
                     "软件分享", "官方微信", "联系客服", "多语言", "关于硕方", "语言设置"):
            if find_visible(driver, AppiumBy.XPATH, f'//*[@text="应用信息"]', 1.0) is None:
                if not tap_id(driver, "htwiHomeMine", "回到-我的tab", 1.5, quiet=True):
                    break
                time.sleep(1.2)
            if tap_text(driver, text, f"我的-{text}", 1.8, quiet=True):
                time.sleep(1.5)
                dismiss_system_popups(driver)
                dump(driver, next_name(f"我的_{text}"))
                close_overlay(driver)
                dismiss_system_popups(driver)
                time.sleep(1.0)
        back_to_home(driver)

    # 连接设备（首页「去连接」）
    if tap_id(driver, "tvGoConnect", "首页-去连接", 2, quiet=True):
        time.sleep(2.5)
        dismiss_system_popups(driver)
        dump(driver, next_name("查找设备"))
        close_overlay(driver)
        back_to_home(driver)

    # 线缆编辑 / 定制耗材 / 扫一扫 快捷入口
    for text in ("线缆编辑", "定制耗材"):
        if tap_text(driver, text, f"首页-{text}", 1.5, quiet=True):
            time.sleep(1.8)
            dismiss_system_popups(driver)
            dump(driver, next_name(f"首页_{text}"))
            close_overlay(driver)
            back_to_home(driver)


# --------------------------------------------------------------------------
# 阶段二：编辑页 + 功能栏各入口
# --------------------------------------------------------------------------
FEATURES_OLD = ["文本", "一维码", "二维码", "图片", "Excel", "反色", "形状",
                "线缆标签", "标识", "边框", "符号", "logo", "线", "涂鸦",
                "端子/端口", "日期", "表格", "序号", "更多"]
FEATURES_NEW = ["文本", "条形码", "二维码", "Excel导入", "符号", "AI拍照打印",
                "形状", "涂鸦", "时间", "表格", "图片", "序号", "边框",
                "新增标签", "扫描商品条码", "我的商品"]


def ensure_old_ui(driver):
    """新版首页有「返回旧版」按钮，先切回旧版 UI。"""
    if tap_id(driver, "btnReturnOldVersion", "切回旧版", 1.5, quiet=True):
        time.sleep(2.5)
        dismiss_system_popups(driver)
        return True
    return False


def enter_edit(driver, attempts=2):
    """首页点「新建标签」进入编辑页（失败时重启 Activity 再试）。"""
    for i in range(attempts):
        back_to_home(driver)
        ensure_old_ui(driver)
        back_to_home(driver)
        for rid in ("htwiHomeCreate", "ivCreateNew", "iv_new_label", "new_label"):
            if tap_id(driver, rid, f"新建标签({rid})", 2.0, quiet=True):
                time.sleep(2.5)
                dismiss_system_popups(driver)
                dump(driver, next_name("新建标签_弹窗"))
                # 「上次使用」弹窗：以此标签纸新建
                for rid2 in ("tvUseLabelAndCreate", "llUseLabelAndCreate"):
                    if tap_id(driver, rid2, "以此标签纸新建", 2.0, quiet=True):
                        time.sleep(3)
                        dismiss_system_popups(driver)
                        return True
                return True
        if i < attempts - 1:
            print("[edit] 没找到新建标签入口，重启 App 重试")
            try:
                driver.terminate_app(APP_PACKAGE)
                driver.activate_app(APP_PACKAGE)
                time.sleep(3)
            except Exception:
                pass
    return False


CONFIRM_IDS = ("ivConfirm", "ivAffirm", "tvConfirm", "dialog_terminal_block_confirm",
               "dialog_table_iv_affirm", "my_dialog_repetition_iv_affirm", "ivSimAffirm",
               "confirmTV", "btn_check", "menu_crop")


def close_panel(driver):
    """关掉「文本」这类内嵌编辑面板：先点确定/勾，再退回，直到宫格重新可见。"""
    if visible_feature_texts(driver):
        return True
    for rid in CONFIRM_IDS:
        if tap_id(driver, rid, f"面板确定-{rid}", 1.0, quiet=True):
            time.sleep(1.2)
            if visible_feature_texts(driver):
                return True
    for _ in range(3):
        if visible_feature_texts(driver):
            return True
        if current_activity(driver).endswith("HomeActivity"):
            return False
        press_back(driver, 1, 1.0)
    return bool(visible_feature_texts(driver))


def phase_edit(driver):
    if not enter_edit(driver):
        print("[edit] 未能进入编辑页")
        return
    dump(driver, next_name("编辑页_画布"))

    seen = set()
    for page in range(1, 7):
        for _ in range(2):                      # 最多补两次翻页，防止翻过头
            items = [t for t in visible_feature_texts(driver) if t not in seen]
            if items:
                break
            swipe_bar_left(driver)
        if not items:
            print(f"[edit] 第{page}页没有新入口，结束")
            break
        dump(driver, next_name(f"功能栏_第{page}页"))
        for text in items:
            seen.add(text)
            loc = f'//android.widget.TextView[@resource-id="{PREFIX}tvKataMyObjectSetting" and @text="{text}"]'
            if not tap(driver, AppiumBy.XPATH, loc, f"功能入口-{text}", 1.5, quiet=True):
                continue
            time.sleep(1.8)
            dismiss_system_popups(driver)
            dump(driver, next_name(f"功能_{text}"))
            # 弹窗里的二级 Tab
            for tab in ("标识", "边框", "符号", "logo", "序号", "涂鸦", "反色",
                        "端子/端口", "日期", "表格", "识别"):
                tloc = f'//android.widget.TextView[@resource-id="{PREFIX}tvTabTitle" and @text="{tab}"]'
                if find_visible(driver, AppiumBy.XPATH, tloc, 0.6):
                    if tap(driver, AppiumBy.XPATH, tloc, f"  弹窗Tab-{tab}", 1.0, quiet=True):
                        time.sleep(1.2)
                        dump(driver, next_name(f"功能_{text}_Tab{tab}"))
            if not close_panel(driver):
                print("[edit] 已离开编辑页，重新进入")
                if not enter_edit(driver):
                    return
        swipe_bar_left(driver)


# --------------------------------------------------------------------------
# 阶段三：文本元素子面板
# --------------------------------------------------------------------------
def phase_text(driver):
    if not enter_edit(driver):
        return
    # 在画布上先放一个文本元素：点功能栏「文本」
    loc = f'//android.widget.TextView[@resource-id="{PREFIX}tvKataMyObjectSetting" and @text="文本"]'
    if not tap(driver, AppiumBy.XPATH, loc, "功能-文本", 2):
        return
    time.sleep(1.8)
    dump(driver, next_name("文本_输入弹窗"))
    el = find_visible(driver, AppiumBy.ID, PREFIX + "etInput", 2)
    if el is not None:
        try:
            el.send_keys("测试文本")
            time.sleep(0.6)
        except Exception:
            pass
    for rid in ("ivConfirm", "ivAffirm", "tvConfirm"):
        if tap_id(driver, rid, "文本-确定", 1.5, quiet=True):
            break
    time.sleep(1.8)
    dump(driver, next_name("文本_编辑面板"))

    # 各子面板（样式/字体/对齐/份数/字效）
    sub_panels = [("tvTypeface", "样式"), ("tvFont", "字体"), ("htiSettingAlign", "对齐"),
                  ("htiSettingRepeat", "重复份数"), ("tv_style_setting", "样式_新版"),
                  ("align_setting", "对齐设置_新版")]
    for rid, label in sub_panels:
        if tap_id(driver, rid, f"文本-{label}", 1.2, quiet=True):
            time.sleep(1.6)
            dump(driver, next_name(f"文本_{label}"))
            if not tap_id(driver, "my_activity_font_back", "字体页返回", 1.0, quiet=True):
                close_overlay(driver)
            time.sleep(0.6)

    # 字效与对齐按钮
    for rid, label in (("ivEffectItalic", "倾斜"), ("ivEffectUnderline", "下划线"),
                       ("ivKataMyFragmentStyleStrikeThrough", "删除线"),
                       ("ivHorizontalLeft", "水平左对齐"), ("ivHorizontalCenter", "水平居中"),
                       ("ivVerticalTop", "垂直顶对齐"), ("ivVerticalCenter", "垂直居中")):
        if tap_id(driver, rid, f"文本-{label}", 1.0, quiet=True):
            time.sleep(0.6)
    dump(driver, next_name("文本_字效与对齐后"))


# --------------------------------------------------------------------------
# 阶段四：模板/耗材/打印/保存
# --------------------------------------------------------------------------
def phase_print(driver):
    """打印 / 模板 / 耗材 / 保存：从编辑页底部入口逐个进入。"""
    if not enter_edit(driver):
        return
    dump(driver, next_name("编辑页_底部入口"))

    for text in ("耗材", "保存", "打印", "模板"):
        if not tap_text(driver, text, f"底部-{text}", 1.5, quiet=True):
            continue
        time.sleep(2.5)
        dismiss_system_popups(driver)
        dump(driver, next_name(f"页面_{text}"))
        # 二级 Tab / 分组
        for sub in ("自定义耗材", "官方耗材", "系统模板", "我的保存", "最近打印",
                    "行业模板", "我的模板", "打印设置"):
            if tap_text(driver, sub, f"  {text}-{sub}", 1.0, quiet=True):
                time.sleep(1.5)
                dump(driver, next_name(f"页面_{text}_{sub}"))
        close_overlay(driver)
        time.sleep(1.0)
        if not current_activity(driver).endswith("HomeActivity"):
            continue
        if not enter_edit(driver):
            return
    back_to_home(driver)


def phase_more(driver):
    if not enter_edit(driver):
        return
    dump(driver, next_name("编辑页_准备打印"))

    # 预览
    if tap_id(driver, "my_activity_main_lp_preview_tv", "预览", 1.2, quiet=True) or \
            tap_text(driver, "预览", "预览(text)", 1.0, quiet=True):
        time.sleep(2)
        dump(driver, next_name("预览"))
        close_overlay(driver)
        time.sleep(0.8)

    # 保存模板
    if tap_id(driver, "my_activity_main_lp_save_iv", "保存", 1.2, quiet=True) or \
            tap_text(driver, "保存", "保存(text)", 1.0, quiet=True):
        time.sleep(1.6)
        dump(driver, next_name("保存模板弹窗"))
        close_overlay(driver)
        time.sleep(0.8)

    # 打印
    if tap_text(driver, "打印", "打印", 1.5, quiet=True):
        time.sleep(3)
        dismiss_system_popups(driver)
        dump(driver, next_name("打印页"))
        close_overlay(driver)
        time.sleep(1.0)

    # 底部：模板 / 耗材
    for text in ("模板", "耗材"):
        if tap_text(driver, text, f"底部-{text}", 1.5, quiet=True):
            time.sleep(2)
            dump(driver, next_name(f"页_{text}"))
            # 模板页 / 耗材页内的分组
            for sub in ("自定义耗材", "系统模板", "我的保存", "最近打印", "行业模板"):
                if tap_text(driver, sub, f"  {text}-{sub}", 1.0, quiet=True):
                    time.sleep(1.2)
                    dump(driver, next_name(f"页_{text}_{sub}"))
            close_overlay(driver)
            time.sleep(0.8)
    back_to_home(driver)


def phase_snapshot(driver):
    """只抓当前这一屏，名字取命令行第二个参数。"""
    tag = sys.argv[2] if len(sys.argv) > 2 else "snapshot"
    dismiss_system_popups(driver)
    dump(driver, next_name(tag))


# --------------------------------------------------------------------------
# 阶段：家用风新版 UI
# --------------------------------------------------------------------------
def phase_newui(driver):
    dismiss_system_popups(driver)
    dump(driver, next_name("新版_首页"))

    # 去编辑（上次使用的标签）
    if tap_id(driver, "tvGotoEdit", "新版-去编辑", 2, quiet=True) or \
            tap_id(driver, "clGoToEdit", "新版-去编辑(容器)", 2, quiet=True):
        time.sleep(2.5)
        dismiss_system_popups(driver)
        dump(driver, next_name("新版_编辑页"))
        # 功能栏逐项
        for text in FEATURES_NEW:
            loc = f'//android.widget.TextView[@resource-id="{PREFIX}tvKataMyObjectSetting" and @text="{text}"]'
            if find_visible(driver, AppiumBy.XPATH, loc, 1.0) is None:
                swipe_bar_left(driver)
            if not tap(driver, AppiumBy.XPATH, loc, f"新版功能-{text}", 1.5, quiet=True):
                continue
            time.sleep(1.8)
            dump(driver, next_name(f"新版功能_{text}"))
            close_overlay(driver)
            time.sleep(0.8)
        close_overlay(driver)
        time.sleep(1.0)

    # 底部：定制耗材 / 我的
    for rid, label in (("llCustomizedConsumables", "定制耗材"), ("llMine", "我的")):
        if tap_id(driver, rid, f"新版底部-{label}", 2, quiet=True):
            time.sleep(2)
            dismiss_system_popups(driver)
            dump(driver, next_name(f"新版_{label}"))
            close_overlay(driver)
            time.sleep(1.0)


# --------------------------------------------------------------------------
def main():
    phases = sys.argv[1:] or ["home"]
    if phases == ["all"]:
        phases = ["home", "newui", "edit", "text", "more"]
    if phases[0] == "snapshot":
        phases = ["snapshot"]
    driver = create_driver()
    try:
        for p in phases:
            print(f"\n===== 阶段 {p} =====")
            try:
                globals()[f"phase_{p}"](driver)
            except Exception as e:
                print(f"[{p}] ✗ 阶段中断：{type(e).__name__}: {e}")
    finally:
        with open(os.path.join(OUT_DIR, "_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(_manifest, f, ensure_ascii=False, indent=2)
        driver.quit()
        print(f"[done] 共 {len(_manifest)} 个页面，产物在 {OUT_DIR}")


if __name__ == "__main__":
    main()
