from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import driver
from datetime import datetime
import time
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from appium.webdriver.common.appiumby import AppiumBy


#----------------统一管理变量----------------
device_number1 = "T0109A2024041502"  # 第一台打印机编号（官方耗材）
device_number2 = "T0171A2504150001"  # 第二台打印机编号(自定义耗材)
telephone_number = "17777786604"     # 登录手机号
diy_width  =  "30"                   # 自定义耗材宽度
diy_height  =  "20"                  # 自定义耗材高度
diy_gap  =  "8"                      # 自定义耗材间隙

#----------------脱机体验机型列表----------------
EXPECTED_MODELS = {
    # T系列
    "T80 Max", "T80 Pro", "T80S","T50 Max", "T50 Plus", "T50S","T50/56 Pro", "T50A","T10/T10Pro/T10Plus", "T16",
    # MP系列
    "MP50 Max", "MP50 Pro", "MP50",
    # G系列
    "G28", "G21", "G15 Max","G15 Pro", "G15", "G15 Mini","G12 Mini", "G18 Pro", "G11 Pro","G18", "G11", "小七", "G10",
    # LP系列
    "LP5125BT", "LP5125", "LP6245E", "LP6125E"
    # TP系列
    "TP20", "TP86A", "TP80A", "TP76i", "TP70", "TP66i", "TP60i", "TP56", "TP50",
    # 热缩管打印机系列
    "TP2000",
    # BP系列
    "BP106T",
    # A4打印机系列
    "HP220/CH203",
}

EXCLUDE_TEXTS = {
    "选择设备",
    "T系列标签机",
    "MP系列标签机",
    "G系列标签机",
    "LP系列覆膜标签机",
    "TP系列线号机",
    "热缩管打印机",
    "BP系列条码机",
    "A4便携热转印打印机",
}

#----------------页面上滑----------------
def swipe_up(driver, duration=800):
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]

    start_x = width * 0.5
    start_y = height * 0.75
    end_x = width * 0.5
    end_y = height * 0.25

    driver.swipe(start_x, start_y, end_x, end_y, duration)

#----------------双击元素----------------
def double_click(element, delay=0.1):

    """模拟双击操作"""
    element.click()
    # 等待短暂时间再点击第二次
    WebDriverWait(element._parent, delay).until(lambda d: True)
    element.click()

#----------------双击坐标----------------
def perform_double_tap(driver, x: int, y: int, tap_duration: float = 0.1, interval: float = 0.1):
    """
    在移动端模拟触摸双击操作（符合安卓双击标准阈值）

    :param driver: WebDriver 实例（如 Appium 驱动）
    :param x: 双击的横坐标
    :param y: 双击的纵坐标
    :param tap_duration: 单次点击的按下/抬起间隔时间（默认0.1秒）
    :param interval: 两次点击之间的间隔时间（默认0.1秒，安卓标准阈值）
    :return: None
    :raises Exception: 执行双击操作时抛出的异常
    """
    try:
        # 初始化触摸动作构建器
        action_builder = ActionBuilder(driver)
        action_builder.add_pointer_input(interaction.POINTER_TOUCH, "touch")
        touch_action = action_builder.pointer_action

        # 第一次点击
        touch_action.move_to_location(x=x, y=y)
        touch_action.pointer_down(button=0)
        touch_action.pause(tap_duration)
        touch_action.pointer_up(button=0)

        # 两次点击间隔
        touch_action.pause(interval)

        # 第二次点击（完成双击）
        touch_action.pointer_down(button=0)
        touch_action.pause(tap_duration)
        touch_action.pointer_up(button=0)

        # 执行所有触摸动作
        action_builder.perform()

    except Exception as e:
        raise Exception(f"执行双击操作失败（坐标：x={x}, y={y}）: {str(e)}")


#----------------显示等待----------------
def wait_for_element(driver, by, locator, timeout=10):
    """显示等待元素可见"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, locator))
    )


def wait_clickable(driver, by, locator, timeout=20):
    """等待元素可点击"""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def wait_visible(driver, by, locator, timeout=20):
    """等待元素可见"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, locator))
    )


def wait_disappear(driver, by, locator, timeout=20):
    """等待元素消失（不可见/不存在）"""
    return WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((by, locator))
    )