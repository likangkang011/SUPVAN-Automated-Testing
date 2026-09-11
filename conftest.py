import os
import pytest
import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.device_detector import DeviceDetector
from utils.logger import setup_logger, get_logger
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# 📌 全局日志：控制台实时输出（配合 pytest.ini 的 log_cli）+ 落盘 logs/run.log
setup_logger()
logger = get_logger("conftest")


def _anchor_collect_args(config):
    """把收集目标修正到项目根，避免「在子目录里跑 pytest → collected 0 items」。

    背景：pytest 只在「启动目录 == rootdir」时才应用 pytest.ini 的 testpaths
    （见 _pytest/config/__init__.py 的 _decide_args），在子目录下执行会静默退化成
    「从当前目录收集」，只在输出头部少一行 `testpaths: xxx`，极难排查。

    config.args_source 精确告诉我们目标是怎么来的：
      - ARGS           用户显式指定了路径  -> 尊重，不干预
      - TESTPATHS      testpaths 已生效      -> 正常，不干预
      - INVOCATION_DIR pytest 退化成「用启动目录」 -> 需要修正
    """
    if getattr(getattr(config, "args_source", None), "name", None) != "INVOCATION_DIR":
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
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


@pytest.fixture(scope="session")
def driver():

    # 自动检测设备
    device_config = DeviceDetector.select_device()
    if not device_config:
        pytest.fail("未检测到任何连接的设备，请检查设备连接")

    # Appium 配置
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = device_config.get("platformVersion")
    options.device_name = device_config.get("deviceName")
    options.udid = device_config.get("udid")
    options.app_package = "com.fhit.app_iprinter"
    options.app_activity = ".ui.home.activity.HomeActivity"
    options.auto_grant_permissions = True
    options.no_reset = False
    options.skip_device_initialization = False
    options.skip_server_installation = False

    # 启动 Appium driver
    driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)

    # # 📌 在 driver 启动后立即执行权限授权（最佳时机）
    # grant_all_permissions("com.fhit.app_iprinter")

    # 📌 然后处理隐私协议弹窗
    handle_privacy_agreement(driver)

    yield driver

    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图，并把截图附加到 pytest-html 报告里。

    - 截图保存到 logs/screenshots/
    - 生成 HTML 报告时（pytest --html=report.html）截图会内嵌到报告
    """
    outcome = yield
    report = outcome.get_result()

    # 只关心「用例主体执行阶段」的失败
    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    try:
        screenshots_dir = os.path.join(os.getcwd(), "logs", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        test_name = item.name.replace("/", "_").replace("::", "_")
        screenshot_path = os.path.join(screenshots_dir, f"{test_name}_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        logger.info("📷 失败截图已保存：%s", screenshot_path)
    except Exception as e:
        logger.warning("失败截图保存失败：%s", e)
        return

    # 附加到 pytest-html 报告（需安装 pytest-html）
    try:
        from pytest_html import extras

        extra = list(getattr(report, "extras", []))
        extra.append(extras.image(screenshot_path))
        report.extras = extra
    except Exception:
        pass
