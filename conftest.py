import os
import re
import glob
import json
import subprocess
import pytest
import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.device_detector import DeviceDetector
from utils.logger import setup_logger, get_logger
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# 🔴 国产 ROM（vivo / OPPO / 小米 / 华为）必查项
# ---------------------------------------------------------------------------
# 现象：Appium session 能建立，handle_privacy_agreement 能通过，
#       但任何 find_element 命令都会 RemoteDisconnected / Connection aborted。
# 根因：厂商定制的"后台耗电管理"把 UIAutomator2 Server 的 HTTP socket 掐掉了，
#       进程还活着（ps 能看到），但端口不监听（/proc/net/tcp 里没有 6790/8200）。
# 手机端修复（AOSP 无对应 API，无法脚本化，必须手动）：
#   设置 → 电池 → 后台耗电管理 / 允许后台活动：
#     ✅ io.appium.uiautomator2.server
#     ✅ io.appium.uiautomator2.server.test
#     ✅ Appium Settings
#       三个全部设为「允许后台高耗电」或「无限制」。
# ---------------------------------------------------------------------------

# 📌 全局日志：控制台实时输出（配合 pytest.ini 的 log_cli）+ 落盘 logs/run.log
setup_logger()
logger = get_logger("conftest")

# 🔴 Appium Server 地址
# ---------------------------------------------------------------------------
# Appium 2.x / 3.x 默认 base path 是 "/"，旧版的 "/wd/hub" 已经移除。
# 继续用 http://localhost:4723/wd/hub 会得到：
#   404 unknown command - The requested resource could not be found
# 只有在启动 server 时显式加了 --base-path=/wd/hub 才需要拼该前缀，
# 这种情况通过环境变量覆盖即可，不用改代码。
# ---------------------------------------------------------------------------
APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")

# 被测应用
APP_PACKAGE = "com.fhit.app_iprinter"
APP_ACTIVITY = ".ui.home.activity.HomeActivity"


def _resolve_arg_against_root(arg, project_root):
    """把「以启动目录为基准找不到」的相对路径，改按项目根重新解析。

    pytest 解析命令行里的相对路径时，基准是**启动目录（cwd）**，不是 rootdir。
    所以在 testcases/ 里执行 `pytest testcases/test_home_style.py` 会直接报
    `ERROR: file or directory not found: testcases/test_home_style.py`
    —— 文件明明在，rootdir 也认对了，只是路径重复拼接了一层目录。

    只在「相对 cwd 不存在、相对项目根存在」时改写，真正写错的路径仍照常报错。
    支持 `文件::用例` 形式的 nodeid。
    """
    path_part, sep, node_part = arg.partition("::")
    if not path_part or os.path.isabs(path_part) or os.path.exists(path_part):
        return arg

    candidate = os.path.join(project_root, path_part)
    if not os.path.exists(candidate):
        return arg

    logger.info(
        "相对路径 %s 不在启动目录下，已按项目根重新解析为 %s", path_part, candidate
    )
    return candidate + sep + node_part


def _anchor_collect_args(config):
    """把收集目标修正到项目根，避免「在子目录里跑 pytest」踩坑。

    背景：pytest 只在「启动目录 == rootdir」时才应用 pytest.ini 的 testpaths
    （见 _pytest/config/__init__.py 的 _decide_args），在子目录下执行会静默退化成
    「从当前目录收集」，只在输出头部少一行 `testpaths: xxx`，极难排查。

    config.args_source 精确告诉我们目标是怎么来的：
      - ARGS           用户显式指定了路径  -> 基准是 cwd，需要逐个校验
      - TESTPATHS      testpaths 已生效      -> 正常，不干预
      - INVOCATION_DIR pytest 退化成「用启动目录」 -> 需要修正
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    source = getattr(getattr(config, "args_source", None), "name", None)

    if source == "ARGS":
        resolved = [_resolve_arg_against_root(a, project_root) for a in config.args]
        if resolved != list(config.args):
            config.args = resolved
        return

    if source != "INVOCATION_DIR":
        return

    testpaths = config.getini("testpaths") or ["."]
    targets = [
        os.path.join(project_root, tp)
        for tp in testpaths
        if os.path.exists(os.path.join(project_root, tp))
    ]
    if not targets:
        return

    config.args = targets
    logger.info(
        "检测到 pytest 的启动目录不是项目根，已自动把收集目标修正为：%s",
        ", ".join(targets),
    )


def pytest_cmdline_main(config):
    """返回 None 让 pytest 走默认实现（firstresult，不返回 None 会截断执行）。"""
    _anchor_collect_args(config)
    return None


# SPECIAL_PERMISSIONS = {
#     "android.permission.WRITE_SETTINGS",
#     "android.permission.SYSTEM_ALERT_WINDOW",
#     "android.permission.MANAGE_EXTERNAL_STORAGE",
#     "android.permission.REQUEST_INSTALL_PACKAGES",
#     "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"
# }

# def grant_all_permissions(package):
#     print(">>> 开始自动授予系统权限...")
#
#     result = os.popen(
#         f"adb shell dumpsys package {package}"
#     ).read().splitlines()
#
#     for line in result:
#         line = line.strip()
#
#         if "permission" in line and "android.permission" in line:
#             perm = line.split(":")[0].strip()
#
#             # 跳过无法通过 adb 授权的特殊权限
#             if perm in SPECIAL_PERMISSIONS:
#                 print(f"跳过特殊权限（需手动授权）：{perm}")
#                 continue
#
#             os.system(f"adb shell pm grant {package} {perm}")
#             print(f"已授权：{perm}")
#
#     print(">>> 权限授予完成\n")


def handle_privacy_agreement(driver):
    """自动处理隐私协议弹窗"""
    try:
        agree_button = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((
                AppiumBy.ID,
                "com.fhit.app_iprinter:id/tvUserAgreementConfirm"
            ))
        )
        agree_button.click()
        logger.info("已自动同意隐私协议")
    except Exception as e:
        logger.info("未检测到隐私协议弹窗: %s", e)


def _adb(udid, *args, timeout=20):
    """带 -s 的 adb 调用。

    必须指定 udid：同时插着模拟器 + 真机时，裸 `adb shell ...` 会直接报
    `error: more than one device/emulator`，stdout 为空，于是自检会误报
    「所有 Appium 包都缺失」——之前就是踩了这个坑（真实原因只是多设备）。
    """
    cmd = ["adb"] + ([f"-s", udid] if udid else []) + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _is_package_installed(udid, package):
    """返回 True / False；adb 自身出错（超时、掉线）时返回 None。

    区分「没装」和「没查成」很重要：查询失败不代表应用不存在，
    误判会直接让整个测试在 fixture 阶段挂掉，且提示信息是错的。
    """
    try:
        res = _adb(udid, "shell", "pm", "list", "packages", package, timeout=30)
    except Exception as e:
        logger.warning("查询包 %s 失败：%s", package, e)
        return None
    if res.returncode != 0:
        logger.warning("查询包 %s 失败：%s", package, res.stderr.strip())
        return None
    return f"package:{package}" in res.stdout


def _preflight_check(udid=None):
    """启动前快速自检：三个 Appium 相关包是否都装了。

    不会自动修复「允许后台高耗电」（AOSP 没开放接口），
    但会在缺失时明确点名，减少换设备后的调试时间。
    """
    needed = [
        "io.appium.settings",
        "io.appium.uiautomator2.server",
        "io.appium.uiautomator2.server.test",
    ]
    try:
        out = _adb(udid, "shell", "pm", "list", "packages").stdout
    except Exception as e:
        logger.warning("⚠️ 无法查询设备包列表（%s），跳过依赖自检", e)
        return

    missing = [p for p in needed if p not in out]
    if missing:
        logger.warning("⚠️ 设备上缺失 Appium 依赖包：%s", missing)
        logger.warning("   Appium 会在启动 session 时自动安装，但安装失败请检查网络")
    else:
        logger.info("✅ Appium 三个依赖包已就绪")


def _find_settings_apk():
    """在 Appium 安装目录里找 io.appium.settings 的 apk，找不到返回 None。"""
    patterns = [
        os.path.expanduser("~/.appium/node_modules/**/io.appium.settings/apks/*.apk"),
        "/opt/homebrew/lib/node_modules/appium/node_modules/**/io.appium.settings/apks/*.apk",
    ]
    for pattern in patterns:
        hits = glob.glob(pattern, recursive=True)
        if hits:
            return hits[0]
    return None


def _ensure_settings_app_permissions(udid):
    """确保 io.appium.settings 能活着——否则整个 session 建不起来。

    Android 14 (API 34) 起，前台服务必须声明并**持有**对应的运行时权限。
    io.appium.settings 用 `location` 类型起前台服务，缺 ACCESS_FINE_LOCATION 时：
        SecurityException: Starting FGS with type location ... targetSDK=35
        requires permissions [FOREGROUND_SERVICE_LOCATION]
    结果就是进程秒崩，Appium 等 5 秒后报：
        Appium Settings app is not running after 5000ms

    `autoGrantPermissions` 只对被测应用生效，管不到这个辅助 App，所以在这里补。
    Appium 自己的安装逻辑是同版本跳过，所以这里授过的权限不会被覆盖。
    """
    permissions = [
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
    ]

    installed = _is_package_installed(udid, "io.appium.settings")
    if installed is False:
        apk = _find_settings_apk()
        if not apk:
            logger.warning("⚠️ 未安装 io.appium.settings，且本地找不到 apk，交给 Appium 自行处理")
            return
        logger.info("设备缺少 io.appium.settings，先行安装：%s", apk)
        res = _adb(udid, "install", "-r", "-g", apk, timeout=120)
        if res.returncode != 0:
            logger.warning("安装 io.appium.settings 失败：%s", res.stderr.strip()[-300:])
            return

    for perm in permissions:
        res = _adb(udid, "shell", "pm", "grant", "io.appium.settings", perm)
        if res.returncode != 0:
            # 已授权时会返回非 0，不算错误
            err = (res.stderr or res.stdout).strip()
            if "Operation not allowed" in err or "not a changeable" in err:
                logger.warning("授予 %s 失败：%s", perm, err)
    logger.info("✅ io.appium.settings 定位权限已就绪")


def _grant_aut_permissions(udid):
    """把被测应用声明过、但还没授予的运行时权限全部补上。

    为什么要单独做：`noReset=False` 会走 fastReset，而 `pm clear` 会把运行时权限
    一并重置。Appium 随后会调 grantAllPermissions，但 Android 12+ 的几组权限
    经常漏授，于是运行时弹窗把整个页面盖住：
      - 「允许"硕方打印"获取位置信息？」        (ACCESS_FINE/COARSE_LOCATION)
      - 「允许"硕方打印"发现并连接到附近的设备？」(BLUETOOTH_SCAN/CONNECT、
                                                NEARBY_WIFI_DEVICES)
    用例就卡在"滑动查找找不到元素"，而真正的原因是被弹窗挡住。

    做法：从 dumpsys 里捞出 `xxx: granted=false` 的权限逐个 pm grant，
    不写死清单——App 以后新增权限也不用改这里。
    """
    try:
        out = _adb(udid, "shell", "dumpsys", "package", APP_PACKAGE, timeout=30).stdout
    except Exception as e:
        logger.warning("读取 %s 权限列表失败：%s", APP_PACKAGE, e)
        return

    pending = re.findall(r"(android\.permission\.[A-Z_0-9]+): granted=false", out)
    if not pending:
        logger.info("✅ %s 无待授予的运行时权限", APP_PACKAGE)
        return

    granted, failed = [], []
    for perm in pending:
        res = _adb(udid, "shell", "pm", "grant", APP_PACKAGE, perm)
        if res.returncode == 0:
            granted.append(perm.split(".")[-1])
        else:
            failed.append(perm.split(".")[-1])

    if granted:
        logger.info("✅ 已为 %s 授予：%s", APP_PACKAGE, ", ".join(granted))
    if failed:
        # 安装期权限（non-changeable）也会落在这里，属正常，不必告警
        logger.info("   跳过不可变更的权限：%s", ", ".join(failed))


@pytest.fixture(scope="session")
def driver():

    # 自动检测设备
    device_config = DeviceDetector.select_device()
    if not device_config:
        pytest.fail("未检测到任何连接的设备，请检查设备连接")
    udid = device_config.get("udid")

    # 启动前快速自检（必须带 udid，否则多设备时 adb 直接报错）
    _preflight_check(udid)

    # 必须在建 session 之前补权限，否则 Appium 启动 settings app 时就崩了
    _ensure_settings_app_permissions(udid)

    # Appium 配置
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = device_config.get("platformVersion")
    options.device_name = device_config.get("deviceName")
    options.udid = udid
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.auto_grant_permissions = True
    options.skip_device_initialization = False
    options.skip_server_installation = False

    # 🔴 应用来源：先看环境变量 APPIUM_APP，再退化为「设备上已装」
    # -----------------------------------------------------------------------
    # noReset=False 时 Appium 会先卸载/重置 AUT，没有 app 能力又未安装就会报：
    #   Either provide 'app' option to install '...' or consider setting 'noReset' to 'true'
    # 所以这里提前判定，给出能直接照做的提示，而不是让 Appium 抛原始错误。
    # -----------------------------------------------------------------------
    apk_path = os.getenv("APPIUM_APP")
    installed = None
    if apk_path:
        if not os.path.exists(apk_path):
            pytest.fail(f"APPIUM_APP 指向的安装包不存在：{apk_path}")
        options.app = apk_path
        options.no_reset = False
        logger.info("使用本地安装包启动：%s", apk_path)
    else:
        installed = _is_package_installed(udid, APP_PACKAGE)

    if not apk_path and installed is True:
        options.no_reset = os.getenv("APPIUM_NO_RESET", "false").lower() == "true"
        logger.info("设备上已安装 %s，noReset=%s", APP_PACKAGE, options.no_reset)
    elif not apk_path and installed is None:
        # 查不出来（adb 超时/掉线）时不阻断，退回最保守的 noReset=True 让 Appium 自己报错
        options.no_reset = True
        logger.warning(
            "无法确认 %s 是否已安装，退回 noReset=True 继续启动；"
            "若随后报 Activity 不存在，请先安装 APK 或设置 APPIUM_APP",
            APP_PACKAGE,
        )
    elif not apk_path:
        pytest.fail(
            f"设备 {udid} 上未安装被测应用 {APP_PACKAGE}，且未提供安装包。\n"
            f"两种解法任选其一：\n"
            f"  1) 先手动安装：adb -s {udid} install -r /path/to/app.apk\n"
            f"  2) 让用例自动安装：export APPIUM_APP=/path/to/app.apk 后再跑 pytest"
        )

    # 启动 Appium driver
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)

    # ✅ session 建好后补权限：fastReset 的 pm clear 会把运行时权限清掉
    _grant_aut_permissions(udid)

    # # 📌 在 driver 启动后立即执行权限授权（最佳时机）
    # grant_all_permissions("com.fhit.app_iprinter")

    # 📌 然后处理隐私协议弹窗
    handle_privacy_agreement(driver)

    yield driver

    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时留一份「失败现场」：截图 + 控件树 + meta.json。

    只存截图往往判不出「为什么没找到这个元素」；把当时的 page_source 一起留下，
    GUI 的「失败现场」就能离线打开那一屏、在元素拾取里点着看 ——
    真机早就翻页了，这份快照还在。

    产物：logs/failures/<时间>_<用例名>/{screenshot.png, page.xml, meta.json}
    """
    outcome = yield
    report = outcome.get_result()

    # 只关心「用例主体执行阶段」的失败
    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    stamp = datetime.datetime.now()
    test_name = item.name.replace("/", "_").replace("::", "_")
    folder = os.path.join(
        os.getcwd(), "logs", "failures", f"{stamp:%Y%m%d_%H%M%S}_{test_name}"
    )
    shot_name, page_name = "screenshot.png", "page.xml"
    screenshot_path = os.path.join(folder, shot_name)

    try:
        os.makedirs(folder, exist_ok=True)
        driver.save_screenshot(screenshot_path)
        logger.info("📷 失败截图已保存：%s", screenshot_path)
    except Exception as e:
        logger.warning("失败截图保存失败：%s", e)
        return

    meta = {
        "time": stamp.isoformat(timespec="seconds"),
        "nodeid": item.nodeid,
        "test": test_name,
        "screenshot": shot_name,
    }
    # 窗口尺寸是离线复盘的必需项：截图坐标要按它换算回屏幕坐标才能命中控件
    try:
        size = driver.get_window_size()
        meta["window"] = {
            "width": int(size.get("width", 0)),
            "height": int(size.get("height", 0)),
        }
    except Exception:
        pass
    for key, getter in (("activity", lambda: driver.current_activity),
                        ("udid", lambda: (driver.capabilities or {}).get("udid", ""))):
        try:
            meta[key] = getter()
        except Exception:
            pass

    try:
        with open(os.path.join(folder, page_name), "w", encoding="utf-8") as f:
            f.write(driver.page_source or "")
        meta["page_source"] = page_name
    except Exception as e:
        logger.warning("控件树保存失败：%s", e)

    try:
        with open(os.path.join(folder, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        logger.info("🗂 失败现场已存档：%s", folder)
    except Exception as e:
        logger.warning("meta.json 写入失败：%s", e)

    # 附加到 pytest-html 报告（需安装 pytest-html）
    try:
        from pytest_html import extras

        extra = list(getattr(report, "extras", []))
        extra.append(extras.image(screenshot_path))
        report.extras = extra
    except Exception:
        pass
