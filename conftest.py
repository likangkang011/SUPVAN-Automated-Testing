import os
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.device_detector import DeviceDetector
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


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
        print("已自动同意隐私协议")
    except Exception as e:
        print(f"未检测到隐私协议弹窗: {str(e)}")


@pytest.fixture(scope="session")
def driver():

    # 自动检测设备
    device_config = DeviceDetector.select_device()
    if not device_config:
        pytest.fail("未检测到任何连接的设备，请检查设备连接")

    # Appium 配置
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = device_config.get("platform_version")
    options.device_name = device_config.get("device_name")
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
