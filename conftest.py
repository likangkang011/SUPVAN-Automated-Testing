import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.device_detector import DeviceDetector
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def handle_privacy_agreement(driver):
    """自动处理隐私协议弹窗（工具函数，非fixture）"""
    try:
        # 等待隐私协议弹窗出现（最多等待10秒）
        agree_button = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((
                AppiumBy.ID,
                "com.fhit.app_iprinter:id/tvUserAgreementConfirm"
            ))
        )
        agree_button.click()
        print("已自动同意隐私协议")
    except Exception as e:
        print(f"未检测到隐私协议弹窗或处理失败: {str(e)}")


@pytest.fixture(scope="session")
def driver():
    # 在fixture内部获取设备配置，确保获取最新状态
    device_config = DeviceDetector.select_device()
    if not device_config:
        pytest.fail("未检测到任何连接的设备，请检查设备连接")

    # 初始化配置
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = device_config.get("platform_version")
    options.device_name = device_config.get("device_name")
    options.udid = device_config.get("udid")
    options.app_package = "com.fhit.app_iprinter"
    options.app_activity = ".ui.home.activity.HomeActivity"
    options.auto_grant_permissions = True
    options.no_reset = False

    # 启动driver（关键：先初始化驱动）
    driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)

    # 驱动初始化后再处理隐私协议（时机正确）
    handle_privacy_agreement(driver)

    yield driver  # 提供driver给测试用例

    # 测试结束后关闭driver
    driver.quit()