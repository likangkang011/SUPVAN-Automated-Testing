from asyncio import wait_for
import sys
import os

# 添加项目根目录到sys.path，解决conftest导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import driver
from datetime import datetime
import time
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from appium.webdriver.common.appiumby import AppiumBy
from locators import LOCATORS


# ----------------统一管理变量----------------
device_number1 = "T0013B2507037084"  # 第一台打印机编号（官方耗材）
device_number2 = "T0024B2024071849"  # 第二台打印机编号(自定义耗材)
telephone_number = "17777786604"     # 登录手机号
diy_width = "50"                     # 自定义耗材宽度
diy_height = "30"                    # 自定义耗材高度
diy_gap = "3"                        # 自定义耗材间隙

"""
# ----------------脱机体验机型列表----------------
EXPECTED_MODELS = {
    # T系列
    "T80 Max", "T80 Pro", "T80S", "T50 Max", "T50 Plus", "T50S", "T50/56 Pro", "T50A", "T10/T10Pro/T10Plus", "T16",
    # MP系列
    "MP50 Max", "MP50 Pro", "MP50",
    # G系列
    "G28", "G21", "G15 Max", "G15 Pro", "G15", "G15 Mini", "G12 Mini", "G18 Pro", "G11 Pro", "G18", "G11", "小七", "G10",
    # LP系列
    "LP5125BT", "LP5125", "LP6245E", "LP6125E",
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
"""

# ----------------页面上滑----------------
def swipe_up(driver, duration=800):
    """页面上滑操作

    :param driver: WebDriver实例
    :param duration: 滑动持续时间，默认800ms
    :return: None
    """
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]
    start_x = width * 0.5
    start_y = height * 0.75
    end_x = width * 0.5
    end_y = height * 0.25

    driver.swipe(start_x, start_y, end_x, end_y, duration)


# ----------------元素左右滑动----------------
def swipe_by_element(driver, by, locator, direction="left", duration=600):
    """
    从指定元素中心向左或向右滑动。

    :param driver: Appium driver
    :param by: 定位方式，例如 AppiumBy.XPATH
    :param locator: 元素定位表达式
    :param direction: "left" 或 "right"
    :param duration: 滑动时长，单位毫秒
    """
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((by, locator))
    )

    # 元素中心作为滑动起点
    start_x = element.location["x"] + element.size["width"] // 2
    start_y = element.location["y"] + element.size["height"] // 2

    # 滑到屏幕左右两边附近
    screen_width = driver.get_window_size()["width"]

    if direction.lower() == "left":
        end_x = int(screen_width * 0.05)
    elif direction.lower() == "right":
        end_x = int(screen_width * 0.95)
    else:
        raise ValueError("direction 只能是 'left' 或 'right'")

    driver.swipe(start_x, start_y, end_x, start_y, duration)


# ----------------双击元素----------------
def double_click(element, delay=0.1):
    """模拟双击操作

    :param element: 要双击的元素
    :param delay: 两次点击之间的延迟，默认0.1s
    :return: None
    """
    element.click()
    # 等待短暂时间再点击第二次
    WebDriverWait(element._parent, delay).until(lambda d: True)
    element.click()


# ----------------双击坐标----------------
def perform_double_tap(driver, x: int, y: int,
                       tap_duration: float = 0.1, interval: float = 0.1):
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


# ----------------单击坐标----------------
def perform_single_tap(driver, x: int, y: int, tap_duration: float = 0.1):
    """
    在移动端模拟触摸单击操作（符合安卓单击标准阈值）

    :param driver: WebDriver 实例（如 Appium 驱动）
    :param x: 单击的横坐标
    :param y: 单击的纵坐标
    :param tap_duration: 点击的按下/抬起间隔时间（默认0.1秒）
    :return: None
    :raises Exception: 执行单击操作时抛出的异常
    """
    try:
        # 初始化触摸动作构建器
        action_builder = ActionBuilder(driver)
        action_builder.add_pointer_input(interaction.POINTER_TOUCH, "touch")
        touch_action = action_builder.pointer_action

        # 执行单击操作
        touch_action.move_to_location(x=x, y=y)  # 移动到目标坐标
        touch_action.pointer_down(button=0)      # 按下操作
        touch_action.pause(tap_duration)         # 保持按下状态
        touch_action.pointer_up(button=0)        # 抬起操作

        # 执行所有触摸动作
        action_builder.perform()

    except Exception as e:
        raise Exception(f"执行单击操作失败（坐标：x={x}, y={y}）: {str(e)}")


# ----------------显示等待----------------
def wait_for_element(driver, by, locator, timeout=10):
    """显示等待元素可见

    :param driver: WebDriver实例
    :param by: 定位方式
    :param locator: 定位器
    :param timeout: 超时时间，默认10s
    :return: 可见的元素
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, locator))
    )


def wait_clickable(driver, by, locator, timeout=20):
    """等待元素可点击

    :param driver: WebDriver实例
    :param by: 定位方式
    :param locator: 定位器
    :param timeout: 超时时间，默认20s
    :return: 可点击的元素
    """
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def wait_visible(driver, by, locator, timeout=20):
    """等待元素可见

    :param driver: WebDriver实例
    :param by: 定位方式
    :param locator: 定位器
    :param timeout: 超时时间，默认20s
    :return: 可见的元素
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, locator))
    )


def wait_disappear(driver, by, locator, timeout=20):
    """等待元素消失（不可见/不存在）

    :param driver: WebDriver实例
    :param by: 定位方式
    :param locator: 定位器
    :param timeout: 超时时间，默认20s
    :return: 布尔值，表示元素是否消失
    """
    return WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((by, locator))
    )


# ----------------测试用例----------------

# # 进入脱机体验页
# def enter_device_select_page(driver):
#     wait_for_element(driver, AppiumBy.ID, 'com.fhit.app_iprinter:id/tvDeviceName').click()

# # 检查脱机体验机型--获取当前页面所有机型
# def get_models_on_current_page(driver):
#     models = set()

#     # 使用Appium的find_elements方法替代execute_script，更可靠
#     text_elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")

#     for el in text_elements:
#         try:
#             text = el.text.strip()
#             if text and text not in EXCLUDE_TEXTS:
#                 models.add(text)
#         except Exception as e:
#             print(f"获取元素文本失败: {e}")
#             continue

#     return models

# # 检查脱机体验机型--滑动获取所有机型
# def get_all_models_by_swipe(driver, max_swipes=10):
#     all_models = set()
#     no_new_rounds = 0

#     for i in range(max_swipes):
#         current_models = get_models_on_current_page(driver)
#         before = len(all_models)

#         all_models.update(current_models)

#         if len(all_models) == before:
#             no_new_rounds += 1
#             print(f"第{i+1}次滑动，未发现新机型，连续无新机型次数: {no_new_rounds}")
#         else:
#             no_new_rounds = 0
#             print(f"第{i+1}次滑动，发现新机型，当前机型总数: {len(all_models)}")

#         if no_new_rounds >= 2:
#             print("连续两次未发现新机型，停止滑动")
#             break

#         swipe_up(driver)
#         time.sleep(0.5)

#     return all_models

# # 检查脱机体验机型--检查机型是否正确
# def assert_all_models_match(driver):
#     actual_models = get_all_models_by_swipe(driver)
#     expected_models = EXPECTED_MODELS

#     extra = actual_models - expected_models
#     missing = expected_models - actual_models

#     # 生成更友好的错误信息
#     error_msg = []
#     if extra:
#         error_msg.append(f"页面多出的机型: {sorted(extra)}")
#     if missing:
#         error_msg.append(f"页面缺少的机型: {sorted(missing)}")
#     if error_msg:
#         error_msg.insert(0, f"机型校验失败！实际机型: {sorted(actual_models)}")
#         error_msg.insert(1, f"预期机型: {sorted(expected_models)}")
#         assert False, "\n".join(error_msg)
#     else:
#         print(f"机型校验成功！所有机型匹配，共{len(actual_models)}个机型")

# def test_offline_device_models(driver):
#     """
#     校验脱机体验页机型是否与配置一致
#     """
#     print("开始执行脱机体验页机型校验测试")
#     enter_device_select_page(driver)
#     assert_all_models_match(driver)
#     print("脱机体验页机型校验测试执行完成")


def test_add_all_function(driver):
    """添加所有编辑功能到功能栏

    :param driver: WebDriver实例
    :return: None
    """
#    # 返回首页
#    wait_for_element(
#        driver,
#        By.ID,
#        'com.fhit.app_iprinter:id/ivActivityOfflineExperienceBack').click()

    # 点击新建标签
    wait_for_element(driver, *LOCATORS["create_new"]).click()

    # 左滑
    swipe_by_element(driver, *LOCATORS["kata_excel"],
        direction="left"
    )

    # 点击更多
    wait_for_element(driver, *LOCATORS["kata_more"]).click()

    # 添加编辑功能到功能栏
    wait_for_element(driver, *LOCATORS["tab_标识"]).click()

    wait_for_element(driver, *LOCATORS["tab_边框"]).click()

    wait_for_element(driver, *LOCATORS["tab_符号"]).click()

    wait_for_element(driver, *LOCATORS["tab_logo"]).click()

    wait_for_element(driver, *LOCATORS["tab_序号"]).click()

    wait_for_element(driver, *LOCATORS["tab_涂鸦"]).click()

    wait_for_element(driver, *LOCATORS["tab_反色"]).click()

    wait_for_element(driver, *LOCATORS["tab_端子端口"]).click()

    wait_for_element(driver, *LOCATORS["tab_日期"]).click()

    wait_for_element(driver, *LOCATORS["tab_表格"]).click()

    wait_for_element(driver, *LOCATORS["tab_识别"]).click()

    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    print('已添加所有功能到功能栏')


def test_loginin(driver):
    """登录功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 返回首页
    wait_for_element(driver, *LOCATORS["back_btn"]).click()

    wait_for_element(driver, *LOCATORS["iv_icon_3"])

    # 去登录
    wait_for_element(driver, *LOCATORS["iv_icon_3"]).click()

    wait_for_element(driver, *LOCATORS["personal_info_enter"]).click()
    wait_for_element(driver, *LOCATORS["login_phone"]).send_keys(telephone_number)
    wait_for_element(driver, *LOCATORS["login_code"]).send_keys('8888')
    wait_for_element(driver, *LOCATORS["login_agree"]).click()
    wait_for_element(driver, *LOCATORS["login_confirm_btn"]).click()
    # 返回首页
    wait_for_element(driver, *LOCATORS["home_tab"]).click()
    print('登录成功')

def test_connect_devices(driver):
    """连接设备测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击去连接

    wait_for_element(driver, *LOCATORS["iv_icon_1"]).click()

    wait_for_element(driver, *LOCATORS["go_connect"]).click()

    wait_for_element(
        driver,
        By.XPATH,
        f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number1}"]'
    ).click()

def test_text1(driver):
    """测试文本功能--双击编辑，添加文本，对齐功能

    :param driver: WebDriver实例
    :return: None
    """
    # 点击新建标签
    wait_for_element(driver, *LOCATORS["create_new"]).click()

    wait_for_element(driver, *LOCATORS["first_connection_close"]).click()

    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试123')
    wait_for_element(driver, *LOCATORS["confirm"]).click()

    wait_for_element(driver, *LOCATORS["copy_btn"]).click()

    wait_for_element(driver, *LOCATORS["rotate_btn"]).click()

    wait_for_element(driver, *LOCATORS["align_btn"]).click()

    wait_for_element(driver, *LOCATORS["align_h_left"]).click()
    wait_for_element(driver, *LOCATORS["align_v_top"]).click()
    wait_for_element(driver, *LOCATORS["setting_align"]).click()


def test_text2(driver):
    """测试文本功能--最大/最小字号

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["kata_text"]).click()

    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试123')
    wait_for_element(driver, *LOCATORS["confirm"]).click()

    for _ in range(20):
        wait_for_element(driver, *LOCATORS["shrink_btn"]).click()

    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["kata_text"]).click()

    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试123')
    wait_for_element(driver, *LOCATORS["confirm"]).click()

    for _ in range(20):
        wait_for_element(driver, *LOCATORS["enlarge_btn"]).click()

    wait_for_element(driver, *LOCATORS["align_btn"]).click()

    wait_for_element(driver, *LOCATORS["align_h_center"]).click()
    wait_for_element(driver, *LOCATORS["align_v_center"]).click()
    wait_for_element(driver, *LOCATORS["setting_align"]).click()


def test_font(driver):
    """测试文本功能--字体功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["kata_text"]).click()

    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试123')
    wait_for_element(driver, *LOCATORS["font_btn"]).click()

    wait_for_element(driver, *LOCATORS["download_more_font"]).click()

    wait_for_element(driver, *LOCATORS["font_download_item_1"]).click()

    wait_for_element(driver, *LOCATORS["font_back"]).click()
    wait_for_element(driver, *LOCATORS["view"]).click()

def test_inverse(driver):
    """测试文本功能--反色功能

        :param driver: WebDriver实例
        :return: None
    """
    wait_for_element(driver, *LOCATORS["kata_text"]).click()

    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试123')
    wait_for_element(driver, *LOCATORS["confirm"]).click()
    for _ in range(5):
        wait_for_element(driver, *LOCATORS["enter_right"]).click()

    wait_for_element(driver, *LOCATORS["feature_反色"]).click()

def test_test3(driver):
    """测试文本功能--样式--自动换行

    :param driver: WebDriver实例
    :return: None
    """
    #新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    #回到功能栏首位置
    for _ in range(6):
        wait_for_element(driver, *LOCATORS["enter_left"]).click()
    #点击文本
    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    #点击样式
    wait_for_element(driver, *LOCATORS["typeface"]).click()
    #开启自动换行
    wait_for_element(driver, *LOCATORS["layout_mode_switch"]).click()
    #输入内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试自动换行测试自动换行测试自动换行测试自动换行')
    #点击确定
    wait_for_element(driver, *LOCATORS["confirm"]).click()
def test_text4(driver):
    #调整字宽（放大两次）
    # 新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    # 点击文本
    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    #输入内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试自动换行测试自动换行测试自动换行测试自动换行')
    #点击样式
    wait_for_element(driver, *LOCATORS["typeface"]).click()
    #放大两次字宽
    wait_for_element(driver, *LOCATORS["word_width_add"]).click()
    wait_for_element(driver, *LOCATORS["word_width_add"]).click()
    #点击确定
    wait_for_element(driver, *LOCATORS["confirm"]).click()

    #文字方向
def test_text5(driver):
    # 新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    # 点击文本
    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    # 输入内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('文字方向文字方向')
    # 点击样式
    wait_for_element(driver, *LOCATORS["typeface"]).click()
    #选择弧形文字方向
    wait_for_element(driver, *LOCATORS["text_direction_c"]).click()
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm"]).click()
#------------测试字效-----------------------------
def test_text6(driver):
    # 新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    # 点击文本
    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    # 输入内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('添加不同字效')
    # 点击样式
    wait_for_element(driver, *LOCATORS["typeface"]).click()
    #页面上滑
    swipe_up(driver)
    #单击字效开关（倾斜）
    wait_for_element(driver, *LOCATORS["effect_italic"]).click()
    #下划线
    wait_for_element(driver, *LOCATORS["effect_underline"]).click()
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm"]).click()

def test_text7(driver):
    # 新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    #点击文本
    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    #点击样式
    wait_for_element(driver, *LOCATORS["typeface"]).click()
    #关闭自动换行
    wait_for_element(driver, *LOCATORS["layout_mode_switch"]).click()
    #开启自动字号
    wait_for_element(driver, *LOCATORS["font_size_auto"]).click()
    #输入内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试自动字号功能测试自动字号')
    # 点击确定--关闭样式弹窗
    wait_for_element(driver, *LOCATORS["confirm"]).click()
def test_text8(driver):
    # 新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    # 点击文本
    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    # 点击样式
    wait_for_element(driver, *LOCATORS["typeface"]).click()
    # 开启自动换行
    wait_for_element(driver, *LOCATORS["layout_mode_switch"]).click()
    #页面上滑（有些机型该页面看不到行间距）
    swipe_up(driver)
    #输入内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试文本设置字间距和行间距测试文本设置字间距和行间距')
    #设置字间距为10
    wait_for_element(driver, *LOCATORS["font_space"]).send_keys('10')
    #设置行间距为-10
    wait_for_element(driver, *LOCATORS["line_space"]).clear()
    wait_for_element(driver, *LOCATORS["line_space"]).send_keys('-10')
    #关闭样式弹窗
    wait_for_element(driver, *LOCATORS["confirm"]).click()
def test_repeat(driver):
    """测试文本功能--重复份数

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["repeat_btn"]).click()
    wait_for_element(driver, *LOCATORS["repeat_input"]).clear()
    wait_for_element(driver, *LOCATORS["repeat_input"]).send_keys('3')
    wait_for_element(driver, *LOCATORS["repeat_affirm"]).click()

#---------------一维码----------------------
def test_barcode(driver):
    """测试一维码功能

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["feature_一维码"]).click()

    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('6901236040287')
    #关闭字符开关
    wait_for_element(driver, *LOCATORS["barcode_chars_switch"]).click()
    wait_for_element(driver, *LOCATORS["affirm"]).click()
def test_barcode2(driver):
    # 新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["feature_一维码"]).click()
    #选择条码类型--CODE-11
    wait_for_element(driver, *LOCATORS["barcode_type_dropdown"]).click()
    wait_for_element(driver, *LOCATORS["barcode_type_code11"]).click()
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('12345678912')
    #清空字符字号
    wait_for_element(driver, *LOCATORS["char_size_input"]).clear()
    #输入字符字号
    wait_for_element(driver, *LOCATORS["char_size_input"]).send_keys('10')
    #开启字符加粗
    wait_for_element(driver, *LOCATORS["chars_bold"]).click()
    #字符对齐方式选择居右对齐
    wait_for_element(driver, *LOCATORS["align_right"]).click()
    #点击字体
    wait_for_element(driver, *LOCATORS["barcode_typeface"]).click()
    #页面上滑可看到下载更多字体的元素（可点击）
    swipe_up(driver)
    #下载更多字体
    wait_for_element(driver, *LOCATORS["download_more_font"]).click()
    wait_for_element(driver, *LOCATORS["font_download_item_2"]).click()
    #返回
    wait_for_element(driver, *LOCATORS["font_back"]).click()
    #点击确定
    wait_for_element(driver, *LOCATORS["affirm"]).click()

def test_qrcode(driver):
    """测试二维码功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["feature_二维码"]).click()

    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('硕方打印')
    wait_for_element(driver, *LOCATORS["affirm"]).click()


def test_photo(driver):
    """测试图片功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["feature_图片"]).click()

    wait_for_element(driver, *LOCATORS["photo_album"]).click()

    wait_for_element(driver, *LOCATORS["photo_check_1"]).click()

    wait_for_element(driver, *LOCATORS["photo_complete"]).click()
    wait_for_element(driver, *LOCATORS["menu_crop"]).click()

def test_excel(driver):
    """测试Excel功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["enter_right"]).click()

    wait_for_element(driver, *LOCATORS["feature_Excel"]).click()

    wait_for_element(driver, *LOCATORS["local_import"]).click()

    wait_for_element(driver, *LOCATORS["file_title"]).click()

    wait_for_element(driver, *LOCATORS["excel_row_1"]).click()

    wait_for_element(driver, *LOCATORS["excel_row_2"]).click()

    wait_for_element(driver, *LOCATORS["create_btn"]).click()
    wait_for_element(driver, *LOCATORS["affirm"]).click()

def test_shape(driver):
    """测试形状功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["feature_形状"]).click()

    wait_for_element(driver, *LOCATORS["shape_item_1"]).click()

    wait_for_element(driver, *LOCATORS["cancel"]).click()


def test_cable_label1(driver):
    """测试线缆标签功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["enter_right"]).click()

    wait_for_element(driver, *LOCATORS["feature_线缆标签"]).click()

    #输入内容--测试线缆
    wait_for_element(driver, *LOCATORS["cable_first_content"]).send_keys('测试线缆')
    #选择第四个展示效果
    wait_for_element(driver, *LOCATORS["cable_align_upper_lower_left"]).click()
    wait_for_element(driver, *LOCATORS["affirm"]).click()

def test_cable_label2(driver):
    #新增标签
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    #选择线缆标签
    wait_for_element(driver, *LOCATORS["feature_线缆标签"]).click()
    #类型选择两折不同
    wait_for_element(driver, *LOCATORS["cable_both_different"]).click()
    #页面上滑--展示出编辑区
    swipe_up(driver)
    wait_for_element(driver, *LOCATORS["cable_first_content"]).send_keys('第一段内容')
    #点击第二折
    wait_for_element(driver, *LOCATORS["cable_second_fold"]).click()
    #输入第二段内容
    wait_for_element(driver, *LOCATORS["cable_second_content"]).send_keys('第二段内容')
    #点击字体
    wait_for_element(driver, *LOCATORS["cable_typeface"]).click()
    #切换字体--使用楷体
    wait_for_element(driver, *LOCATORS["font_kaiti"]).click()
    #点击字效
    wait_for_element(driver, *LOCATORS["cable_effect"]).click()
    #取消加粗
    wait_for_element(driver, *LOCATORS["cable_effect_bold"]).click()
    #选择斜体
    wait_for_element(driver, *LOCATORS["cable_effect_italic"]).click()
    #选择下划线
    wait_for_element(driver, *LOCATORS["effect_underline"]).click()
    #点击确定
    wait_for_element(driver, *LOCATORS["affirm"]).click()

def test_symbol_frame(driver):
    """测试标识，边框，符号功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["enter_right"]).click()

    wait_for_element(driver, *LOCATORS["feature_标识"]).click()

    wait_for_element(driver, *LOCATORS["symbol_0"]).click()
    #单击屏幕画布区域关闭标识弹窗
    perform_single_tap(driver,500,900)

    wait_for_element(driver, *LOCATORS["feature_边框"]).click()

    wait_for_element(driver, *LOCATORS["border_item_2"]).click()
    #单击屏幕画布区域关闭边框弹窗
    perform_single_tap(driver,500,900)
    '''   
    #再次运行--确认是否需要删除
    wait_for_element(driver, *LOCATORS["cancel"]).click()
    '''
    wait_for_element(driver, *LOCATORS["feature_符号"]).click()

    wait_for_element(driver, *LOCATORS["symbol_hash"]).click()
    #单击屏幕画布区域关闭符号弹窗
    perform_single_tap(driver,500,900)

def test_logo(driver):
    """测试LOGO功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["feature_logo"]).click()

    wait_for_element(driver, *LOCATORS["logo_item_4"]).click()


def test_line(driver):
    """测试线功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["enter_right"]).click()

    for _ in range(3):
        wait_for_element(driver, *LOCATORS["feature_线"]).click()


def test_sketch(driver):
    """测试涂鸦功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["enter_right"]).click()

    wait_for_element(driver, *LOCATORS["feature_涂鸦"]).click()

    # 定位坐标在涂鸦区域进行涂鸦
    driver.swipe(100, 1300, 700, 1300)
    driver.swipe(200, 1100, 200, 1500)
    driver.swipe(100, 1400, 700, 1400)

    #使用橡皮功能
    wait_for_element(driver, *LOCATORS["eraser"]).click()
    #擦除部分已涂鸦内容
    driver.swipe(100, 1400, 700, 1400)
    #撤销上一次操作
    wait_for_element(driver, *LOCATORS["revocation"]).click()
    #取消撤销操作
    wait_for_element(driver, *LOCATORS["recover"]).click()
    #点击确定
    wait_for_element(driver, *LOCATORS["confirm"]).click()


def test_terminal_port(driver):
    """测试端子/端口功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["feature_端子端口"]).click()
    #点击绘制边框
    wait_for_element(driver, *LOCATORS["terminal_border"]).click()
    #清除端子宽度B的内容
    wait_for_element(driver, *LOCATORS["terminal_clear_second"]).click()
    #输入端子宽度B的内容
    wait_for_element(driver, *LOCATORS["et_width"]).send_keys('8')
    #清除默认的端子格数
    wait_for_element(driver, *LOCATORS["terminal_frame"]).clear()
    #输入端子个数为4
    wait_for_element(driver, *LOCATORS["terminal_frame"]).send_keys('4')
    #选择分割线的样式
    wait_for_element(driver, *LOCATORS["terminal_line_rectangle"]).click()
    #点击内容板块
    wait_for_element(driver, *LOCATORS["terminal_tab_content"]).click()

    wait_for_element(driver, *LOCATORS["terminal_content_1"]).send_keys('测试1')

    wait_for_element(driver, *LOCATORS["terminal_content_2"]).send_keys('测试2')
    #点击样式
    wait_for_element(driver, *LOCATORS["terminal_tab_style"]).click()
    #设置字间距
    wait_for_element(driver, *LOCATORS["terminal_font_space"]).clear()
    wait_for_element(driver, *LOCATORS["terminal_font_space"]).send_keys('3')

    #设置行间距
    wait_for_element(driver, *LOCATORS["terminal_line_space"]).clear()
    wait_for_element(driver, *LOCATORS["terminal_line_space"]).send_keys('3')
    #选择字效（加粗、斜体，下划线）
    wait_for_element(driver, *LOCATORS["terminal_effect_bold"]).click()
    wait_for_element(driver, *LOCATORS["terminal_effect_italic"]).click()
    wait_for_element(driver, *LOCATORS["terminal_effect_underline"]).click()

    #点击字体板块
    wait_for_element(driver, *LOCATORS["terminal_tab_font"]).click()
    #选择字体--站酷快乐体
    wait_for_element(driver, *LOCATORS["font_zhanku"]).click()



    wait_for_element(driver, *LOCATORS["terminal_confirm"]).click()


def test_date(driver):
    """测试日期功能

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["add_label"]).click()
    wait_for_element(driver, *LOCATORS["enter_right"]).click()

    wait_for_element(driver, *LOCATORS["feature_日期"]).click()
    #开启实时时间
    wait_for_element(driver, *LOCATORS["date_realtime"]).click()
    wait_for_element(driver, *LOCATORS["date_read_tip"]).click()
    #开启星期开关
    wait_for_element(driver, *LOCATORS["date_week"]).click()
    #点击前缀下拉框
    wait_for_element(driver, *LOCATORS["date_prefix_dropdown"]).click()
    #选择生产日期
    wait_for_element(driver, *LOCATORS["date_first_prefix"]).click()
    wait_for_element(driver, *LOCATORS["date_add_association"]).click()
    wait_for_element(driver, *LOCATORS["affirm"]).click()


def test_table(driver):
    """测试表格功能
    :param driver: WebDriver实例
    :return: None
    """
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]
    wait_for_element(driver, *LOCATORS["add_label"]).click()

    wait_for_element(driver, *LOCATORS["feature_表格"]).click()


    perform_double_tap(driver, x=width * 0.33, y=height * 0.29)
    wait_visible(driver, *LOCATORS["table_edit"]).send_keys("表格1")

    wait_clickable(driver, *LOCATORS["table_affirm"]).click()


def  test_prewiew(driver):
    """测试预览功能

    :param driver: WebDriver实例
    :return: None
    """
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]
    # 测试预览功能
    wait_for_element(driver, *LOCATORS["preview_btn"]).click()

    driver.swipe(
        width * 0.5,
        height * 0.8,
        width * 0.5,
        height * 0.2,
        800
    )

    driver.swipe(
        width * 0.5,
        height * 0.2,
        width * 0.5,
        height * 0.8,
        800
    )

    wait_for_element(driver, *LOCATORS["interior_handle"]).click()


def test_savetemplate1(driver):
    """保存文本，一维码模板测试

    :param driver: WebDriver实例
    :return: None
    """
    # 保存模板
    wait_for_element(driver, *LOCATORS["save_btn"]).click()
    wait_for_element(driver, *LOCATORS["template_name_input"]).send_keys('文本，一维码模板')
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()


def test_savetemplate2(driver):
    """保存序号模板测试

    :param driver: WebDriver实例
    :return: None
    """
    # 添加序号模板
    #返回
    wait_for_element(driver, *LOCATORS["main_back_btn"]).click()
    #不保存
    wait_for_element(driver, *LOCATORS["not_save"]).click()
    #创建新标签
    wait_for_element(driver, *LOCATORS["create_new"]).click()
    #标签旋转
    wait_for_element(driver, *LOCATORS["canvas_rotation"]).click()
    for _ in range(4):
        wait_for_element(driver, *LOCATORS["enter_right"]).click()
    #选择序号
    wait_for_element(driver, *LOCATORS["feature_序号"]).click()

    #点击样式下拉框
    wait_for_element(driver, *LOCATORS["sequence_style_dropdown"]).click()
    #选择其他样式
    wait_for_element(driver, *LOCATORS["sequence_style_0999"]).click()

    wait_for_element(driver, *LOCATORS["seq_prefix"]).send_keys('前缀')
    wait_for_element(driver, *LOCATORS["seq_suffix"]).send_keys('后缀')
    wait_for_element(driver, *LOCATORS["seq_start"]).send_keys('1')
    wait_for_element(driver, *LOCATORS["seq_end"]).send_keys('5')
    #设置间隔为2
    wait_for_element(driver, *LOCATORS["seq_clear_interval"]).click()
    wait_for_element(driver, *LOCATORS["seq_interval"]).send_keys('2')
    #点击字体
    wait_for_element(driver, *LOCATORS["cable_typeface"]).click()
    #使用其他字体
    wait_for_element(driver, *LOCATORS["font_heiti"]).click()
    #点击确定
    wait_for_element(driver, *LOCATORS["affirm"]).click()

    # 保存模板
    wait_for_element(driver, *LOCATORS["save_btn"]).click()
    wait_for_element(driver, *LOCATORS["template_name_input"]).send_keys('序号模板')
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()

    # 返回
    wait_for_element(driver, *LOCATORS["main_back_btn"]).click()


def test_print_personal_template1(driver):
    """打印序号模板测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击我的保存
    wait_for_element(driver, *LOCATORS["my_save"]).click()

    # 点击第一个已保存的模板
    wait_for_element(driver, *LOCATORS["template_序号"]).click()

    # 点击打印
    wait_for_element(driver, *LOCATORS["iv_icon_3"]).click()

    # 点击确定
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()

    wait_disappear(driver, *LOCATORS["print_cancel"])

    # 点击模板
    wait_clickable(driver, *LOCATORS["iv_icon_4"]).click()


def test_print_personal_template2(driver):
    """打印文本，一维码模板测试

    :param driver: WebDriver实例
    :return: None
    """
    # 切换成第二个模板
    wait_for_element(driver, *LOCATORS["template_文本一维码"]).click()

    # 点击打印
    wait_for_element(driver, *LOCATORS["iv_icon_3"]).click()

    wait_disappear(driver, *LOCATORS["print_cancel"])

    wait_clickable(driver, *LOCATORS["range_add"]).click()

    # 设置excel打印范围
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()

    wait_disappear(driver, *LOCATORS["print_cancel"])


def test_print_system_template(driver):
    """打印系统模板测试

    :param driver: WebDriver实例
    :return: None
    """
    # 打印系统模板
    # 点击模板
    wait_for_element(driver, *LOCATORS["template_tab"]).click()

    # 点击系统模板
    wait_for_element(driver, *LOCATORS["system_template"]).click()

    # 任选一个系统模板
    wait_for_element(driver, *LOCATORS["template_file_item_1"]).click()

    # 点击打印
    wait_for_element(driver, *LOCATORS["iv_icon_3"]).click()

    # 点击确定
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()


def test_print_setting(driver):
    """打印设置测试

    :param driver: WebDriver实例
    :return: None
    """
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]
    # 点击返回
    wait_for_element(driver, *LOCATORS["main_back_btn"]).click()

    # 点击不保存
    wait_for_element(driver, *LOCATORS["not_save"]).click()

    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]

    # 需验证能否滑倒底部--滑动距离足够
    driver.swipe(
        width * 0.2,
        height * 0.5,
        width * 0.2,
        height * 0.9)

    # 断开机器
    wait_for_element(driver, *LOCATORS["go_connect"]).click()
    # 点击去连接
    wait_for_element(driver, *LOCATORS["iv_icon_1"]).click()
    wait_for_element(driver, *LOCATORS["go_connect"]).click()
    # 连接另一台机器
    wait_for_element(
        driver,
        By.XPATH,
        f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number2}"]'
    ).click()


def test_DIY(driver):
    """自定义耗材测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击新建标签
    wait_for_element(driver, *LOCATORS["create_new"]).click()

    # 点击耗材
    wait_for_element(driver, *LOCATORS["consumable_tab"]).click()
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]

    # 需验证能否滑倒底部
    driver.swipe(
        width * 0.2,
        height * 0.9,
        width * 0.2,
        height * 0.5)

    # 选中自定义耗材
    wait_for_element(driver, *LOCATORS["consumable_custom_group"]).click()

    # 点击新增自定义耗材
    wait_for_element(driver, *LOCATORS["consumable_add"]).click()

    # 设置耗材的宽高
    wait_for_element(driver, *LOCATORS["consumable_name"]).send_keys(
        "自定义耗材" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    wait_for_element(driver, *LOCATORS["et_width"]).clear()
    wait_for_element(driver, *LOCATORS["et_height"]).clear()
    wait_for_element(driver, *LOCATORS["consumable_gap"]).clear()
    wait_for_element(driver, *LOCATORS["et_width"]).send_keys(diy_width)
    wait_for_element(driver, *LOCATORS["et_height"]).send_keys(diy_height)
    wait_for_element(driver, *LOCATORS["consumable_gap"]).send_keys(diy_gap)
    wait_for_element(driver, *LOCATORS["consumable_delete_picture"]).click()

    # 点击保存
    wait_for_element(driver, *LOCATORS["consumable_save"]).click()
    time.sleep(3)
    print('已保存自定义耗材')
    wait_for_element(driver, *LOCATORS["template_file_item_1"]).click()
    wait_for_element(driver, *LOCATORS["affirm"]).click()

    for _ in range(3):
        wait_for_element(driver, *LOCATORS["enter_right"]).click()

    # 点击添加一个边框
    wait_for_element(driver, *LOCATORS["feature_边框"]).click()

    # 添加一个边框
    wait_for_element(driver, *LOCATORS["border_item_2"]).click()

    # 关闭边框弹窗
    wait_for_element(driver, *LOCATORS["cancel"]).click()

    # 添加文本
    # 双击编辑区进行编辑
    double_click(
        wait_for_element(driver, *LOCATORS["paint_view"]).click()
    )
    # 输入文本
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试123')

    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm"]).click()

    # 点击打印
    wait_for_element(driver, *LOCATORS["print_tab"]).click()

    # 设置打印份数
    # 清空输入框
    wait_for_element(driver, *LOCATORS["copies_input"]).clear()

    # 设置打印份数为2
    wait_for_element(driver, *LOCATORS["copies_input"]).send_keys('2')

    # 水平，垂直偏移为-16
    wait_for_element(driver, *LOCATORS["h_shift"]).clear()
    wait_for_element(driver, *LOCATORS["h_shift"]).send_keys('-16')
    wait_for_element(driver, *LOCATORS["v_shift"]).clear()
    wait_for_element(driver, *LOCATORS["v_shift"]).send_keys('-16')

    # 点击确定，开始进行打印
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()

    # 点击打印
    wait_for_element(driver, *LOCATORS["print_tab"]).click()

    # 设置打印份数
    # 清空输入框
    wait_for_element(driver, *LOCATORS["copies_input"]).clear()

    # 设置打印份数为3
    wait_for_element(driver, *LOCATORS["copies_input"]).send_keys('3')

    # 打印当前页
    wait_for_element(driver, *LOCATORS["range_add"]).click()

    # 设置打印浓度为9
    wait_for_element(driver, *LOCATORS["density"]).clear()
    wait_for_element(driver, *LOCATORS["density"]).send_keys('9')

    # 水平，垂直偏移为16
    wait_for_element(driver, *LOCATORS["h_shift"]).clear()
    wait_for_element(driver, *LOCATORS["h_shift"]).send_keys('16')
    wait_for_element(driver, *LOCATORS["v_shift"]).clear()
    wait_for_element(driver, *LOCATORS["v_shift"]).send_keys('16')


    # 打印设置页面上滑
    driver.swipe(
        width * 0.5,
        height * 0.5,
        width * 0.5,
        height * 0.4)

    # 切换翻转方式为水平翻转
    wait_for_element(driver, *LOCATORS["flip_add"]).click()

    # 点击确定开始打印
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()

    wait_disappear(driver, *LOCATORS["print_cancel"])
