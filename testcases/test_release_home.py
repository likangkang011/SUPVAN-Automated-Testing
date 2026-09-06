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
device_number1 = "T0109A2024041502"  # 第一台打印机编号（官方耗材）
device_number2 = "T0171A2504150001"  # 第二台打印机编号(自定义耗材)
device_number3 = "T0109A2024041502"  # 第三台打印机编号（商超耗材）
telephone_number = "17777786604"     # 登录手机号
diy_width = "30"                     # 自定义耗材宽度
diy_height = "20"                    # 自定义耗材高度
diy_gap = "8"                        # 自定义耗材间隙

# # ----------------脱机体验机型列表----------------
# EXPECTED_MODELS = {
#     # T系列
#     "T80 Max", "T80 Pro", "T80S", "T50 Max", "T50 Plus", "T50S", "T50/56 Pro", "T50A", "T10/T10Pro/T10Plus", "T16",
#     # MP系列
#     "MP50 Max", "MP50 Pro", "MP50",
#     # G系列
#     "G28", "G21", "G15 Max", "G15 Pro", "G15", "G15 Mini", "G12 Mini", "G18 Pro", "G11 Pro", "G18", "G11", "小七", "G10",
#     # LP系列
#     "LP5125BT", "LP5125", "LP6245E", "LP6125E",
#     # TP系列
#     "TP20", "TP86A", "TP80A", "TP76i", "TP70", "TP66i", "TP60i", "TP56", "TP50",
#     # 热缩管打印机系列
#     "TP2000",
#     # BP系列
#     "BP106T",
#     # A4打印机系列
#     "HP220/CH203",
# }

# EXCLUDE_TEXTS = {
#     "选择设备",
#     "T系列标签机",
#     "MP系列标签机",
#     "G系列标签机",
#     "LP系列覆膜标签机",
#     "TP系列线号机",
#     "热缩管打印机",
#     "BP系列条码机",
#     "A4便携热转印打印机",
# }

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

# ----------------底部页面左滑----------------


def swipe_left(driver):
    """底部页面左滑操作

    :param driver: WebDriver实例
    :return: None
    """
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]

    start_x = width * 0.8
    start_y = height * 0.75
    end_x = width * 0.3
    end_y = height * 0.75
    driver.swipe(start_x, start_y, end_x, end_y)

# ----------------双击元素----------------


def double_click(element, delay=0.1):
    """模拟双击操作

    :param element: 要双击的元素
    :param delay: 两次点击之间的延迟,默认0.1s
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
    :param tap_duration: 单次点击的按下/抬起间隔时间(默认0.1秒）
    :param interval: 两次点击之间的间隔时间(默认0.1秒，安卓标准阈值）
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


def wait_disappear(driver, by, locator, timeout=30):
    """等待元素消失（不可见/不存在）

    :param driver: WebDriver实例
    :param by: 定位方式
    :param locator: 定位器
    :param timeout: 超时时间,默认30s
    :return: 布尔值，表示元素是否消失
    """
    return WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((by, locator))
    )

# ----------------测试用例----------------


def test_login(driver):
    """登录功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击我的
    wait_for_element(driver, *LOCATORS["iv_icon_3"]).click()
    # 进入家用风主页
    wait_for_element(driver, *LOCATORS["enter_new_version"]).click()
    # 点击去登陆
    wait_for_element(driver, *LOCATORS["login_btn"]).click()
    wait_for_element(driver, *LOCATORS["login_phone"]).send_keys(telephone_number)
    wait_for_element(driver, *LOCATORS["login_code"]).send_keys('8888')
    wait_for_element(driver, *LOCATORS["login_agree"]).click()
    wait_for_element(driver, *LOCATORS["login_confirm_btn"]).click()


def test_connect_devices(driver):
    """连接设备测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击去连接
    wait_for_element(driver, *LOCATORS["connect_state"]).click()
    # 匹配连接机器型号，点击连接按钮
    wait_for_element(
        driver,
        By.XPATH,
        f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number1}"]').click()


def test_add_text(driver):
    """添加文本功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击去编辑
    wait_for_element(driver, *LOCATORS["goto_edit"]).click()
    # 关闭新建标签引导图
    wait_for_element(driver, *LOCATORS["first_connection"]).click()
    # 使用文本功能
    wait_for_element(driver, *LOCATORS["kata_text"]).click()
    # 输入内容
    wait_for_element(driver, *LOCATORS["edit_text_class"]).send_keys('添加文本')
    # 点击复制
    wait_for_element(driver, *LOCATORS["copy_btn"]).click()
    # 旋转
    wait_for_element(driver, *LOCATORS["rotate_btn"]).click()
    # 左对齐,上对齐
    wait_for_element(driver, *LOCATORS["align_setting"]).click()
    wait_for_element(driver, *LOCATORS["align_h_left"]).click()
    wait_for_element(driver, *LOCATORS["align_v_top"]).click()


def test_add_barcode(driver):
    """添加条形码功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 点击条形码
    wait_for_element(driver, *LOCATORS["kata_barcode"]).click()
    # 输入条形码内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('6939947707670')
    # 点击确定
    wait_for_element(driver, *LOCATORS["affirm"]).click()


def test_add_qrcode(driver):
    """添加二维码功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 导入二维码
    wait_for_element(driver, *LOCATORS["kata_qrcode"]).click()
    # 输入二维码内容
    wait_for_element(driver, *LOCATORS["input_edit"]).send_keys('测试二维码')
    # 点击确定
    wait_for_element(driver, *LOCATORS["affirm"]).click()


def test_add_excel(driver):
    """Excel导入功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 导入二维码
    wait_for_element(driver, *LOCATORS["kata_excel_import"]).click()
    # 选择本地导入
    wait_for_element(driver, *LOCATORS["local_import"]).click()
    # 选择excel
    wait_for_element(driver, *LOCATORS["documentsui_icon_thumb_1"]).click()
    wait_for_element(driver, *LOCATORS["excel_row_1"]).click()
    wait_for_element(driver, *LOCATORS["excel_row_2"]).click()
    # 点击生成
    wait_for_element(driver, *LOCATORS["create_btn"]).click()
    # 确认生成
    wait_for_element(driver, *LOCATORS["sim_affirm"]).click()


def test_add_symbol(driver):
    """添加符号功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 添加符号
    wait_for_element(driver, *LOCATORS["kata_symbol"]).click()
    # 任选一个符号进行添加
    wait_for_element(driver, *LOCATORS["symbol_exclamation"]).click()
    # 收起功能区域
    wait_for_element(driver, *LOCATORS["label_produce_close"]).click()


def test_ai_photo_print(driver):
    """AI拍照打印功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 点击AI拍照打印
    wait_for_element(driver, *LOCATORS["kata_ai_photo"]).click()
    # 从相册选择
    wait_for_element(driver, *LOCATORS["choose_album"]).click()
    # 选择相册的第一张相片
    wait_for_element(driver, *LOCATORS["photo_btn_check_1"]).click()
    # 点击已完成
    wait_for_element(driver, *LOCATORS["photo_complete"]).click()
    # 点击确定
    wait_for_element(driver, *LOCATORS["appcompat_linear_layout"]).click()

    '''
def test_template(driver):
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    #点击模板
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="模板"]').click()
    #使用第一个系统模板
    wait_for_element(driver,By.XPATH,'(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_name"])[1]').click()
    '''


def test_add_shape(driver):
    """添加形状功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 添加形状功能
    wait_for_element(driver, *LOCATORS["kata_shape"]).click()
    # 收起形状功能弹窗
    wait_for_element(driver, *LOCATORS["close"]).click()


def test_add_sketch(driver):
    """添加涂鸦功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择涂鸦功能
    wait_for_element(driver, *LOCATORS["kata_sketch"]).click()
    driver.swipe(100, 1300, 700, 1300)
    driver.swipe(200, 1100, 200, 1500)
    driver.swipe(100, 1400, 700, 1400)
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm"]).click()
    # 收起功能区弹窗
    wait_for_element(driver, *LOCATORS["close2"]).click()


def test_date(driver):
    """时间功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择时间功能
    wait_for_element(driver, *LOCATORS["kata_time"]).click()
    # 添加实时时间
    wait_for_element(driver, *LOCATORS["date_realtime"]).click()
    wait_for_element(driver, *LOCATORS["date_read_tip"]).click()
    wait_for_element(driver, *LOCATORS["date_add_association"]).click()
    # 关闭时间弹窗
    wait_for_element(driver, *LOCATORS["back"]).click()


def test_add_table(driver):
    """添加表格功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择表格功能
    wait_for_element(driver, *LOCATORS["kata_table"]).click()
    # 双击表格的编辑区
    size = driver.get_window_size()
    screen_width = size["width"]
    screen_height = size["height"]
    perform_double_tap(driver, x=450, y=800)
    wait_for_element(driver, *LOCATORS["table_edit"]).send_keys('表格文本1')
    # 点击确定按钮
    wait_for_element(driver, *LOCATORS["table_affirm"]).click()


def test_add_photo(driver):
    """添加图片功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 新增标签
    wait_for_element(driver, *LOCATORS["new_label"]).click()
    # 收起预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择图片功能
    wait_for_element(driver, *LOCATORS["kata_photo"]).click()
    # 从相册选择
    wait_for_element(driver, *LOCATORS["photo_album"]).click()
    # 选择第一张图片
    wait_for_element(driver, *LOCATORS["photo_check_1"]).click()
    # 点击已完成
    wait_for_element(driver, *LOCATORS["photo_complete"]).click()
    # 点击确定
    wait_for_element(driver, *LOCATORS["appcompat_linear_layout"]).click()


def test_save_template(driver):
    """保存模板功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击保存
    wait_for_element(driver, *LOCATORS["save_text"]).click()
    # 清空文本框
    wait_for_element(driver, *LOCATORS["template_name_input"]).clear()
    # 输入模板名字
    wait_for_element(driver, *LOCATORS["template_name_input"]).send_keys('自动化测试模板1')
    # 点击保存
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    # 点击去查看
    wait_for_element(driver, *LOCATORS["saved_toast"]).click()
    # 选择模板
    wait_for_element(driver, *LOCATORS["template_spec_1"]).click()


def test_print(driver):
    """打印功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 打印编辑并保存的模板
    wait_for_element(driver, *LOCATORS["print_text"]).click()
    # 设置excel打印范围
    # wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etExcelLarge').clear()
    # wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etExcelLarge').send_keys('3')
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    wait_disappear(driver, *LOCATORS["print_cancel"])


def test_change_machine(driver):
    """切换设备测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击返回
    wait_for_element(driver, *LOCATORS["home_back"]).click()
    # 不保存
    wait_for_element(driver, *LOCATORS["not_save"]).click()
    # 切换机器
    wait_for_element(driver, *LOCATORS["connect_state"]).click()
    wait_for_element(driver, *LOCATORS["confirm_text"]).click()
    wait_for_element(driver, *LOCATORS["connect_state"]).click()
    # 连接新机器型号
    wait_for_element(
        driver,
        By.XPATH,
        f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number2}"]'
    ).click()


def test_new_template(driver):
    """新建模板测试

    :param driver: WebDriver实例
    :return: None
    """
    wait_for_element(driver, *LOCATORS["goto_edit"]).click()
    # 点击耗材
    wait_for_element(driver, *LOCATORS["material_info_icon"]).click()
    # 自定义耗材
    wait_for_element(driver, *LOCATORS["go_custom_label"]).click()
    wait_for_element(driver, *LOCATORS["input_width"]).send_keys('50')
    wait_for_element(driver, *LOCATORS["input_height"]).send_keys('30')
    wait_for_element(driver, *LOCATORS["input_gap"]).send_keys('3')
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm_tv"]).click()


def test_add_SEQ(driver):
    """添加序号功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 打开功能区
    wait_for_element(driver, *LOCATORS["more_fun"]).click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择序号功能
    wait_for_element(driver, *LOCATORS["kata_seq"]).click()
    # 输入起始值
    wait_for_element(driver, *LOCATORS["seq_start"]).send_keys('00')
    # 输入结束值
    wait_for_element(driver, *LOCATORS["seq_end"]).send_keys('03')
    # 点击确定
    wait_for_element(driver, *LOCATORS["affirm"]).click()


def test_add_frame(driver):
    """添加边框功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击边框
    wait_for_element(driver, *LOCATORS["kata_frame"]).click()
    # 选择一个边框
    wait_for_element(driver, *LOCATORS["border_item_3"]).click()
    # 收起弹窗
    wait_for_element(driver, *LOCATORS["wire_frame_close"]).click()


def test_print_settings(driver):
    """打印设置测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击打印
    wait_for_element(driver, *LOCATORS["print_text"]).click()
    # 打印份数
    wait_for_element(driver, *LOCATORS["copies_input"]).clear()
    wait_for_element(driver, *LOCATORS["copies_input"]).send_keys('2')
    # 打印浓度
    wait_for_element(driver, *LOCATORS["density"]).clear()
    wait_for_element(driver, *LOCATORS["density"]).send_keys('3')
    # 打印范围修改为全部页
    wait_for_element(driver, *LOCATORS["range_add"]).click()
    # 打印
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    wait_disappear(driver, *LOCATORS["print_cancel"])


def test_multiple_print(driver):
    """商超耗材多份打印测试

    :param driver: WebDriver实例
    :return: None
    """
    # 点击我的
    wait_for_element(driver, *LOCATORS["my_tab"]).click()
    # 进入新版
    wait_for_element(driver, *LOCATORS["enter_new_version"]).click()
    # 点击去连接
    wait_for_element(driver, *LOCATORS["connect_state"]).click()
    # 连接机器
    wait_for_element(
        driver,
        By.XPATH,
        f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number1}"]').click()
    # 点击去编辑
    wait_for_element(driver, *LOCATORS["goto_edit"]).click()
    # 新建标签
    wait_for_element(driver, *LOCATORS["kata_new_label"]).click()
    # 关闭预览
    wait_for_element(driver, *LOCATORS["hide_preview"]).click()
    # 清空输入框内容
    wait_for_element(driver, *LOCATORS["et_edit_199"]).clear()
    # 输入新内容
    wait_for_element(driver, *LOCATORS["et_edit_4"]).send_keys('999')
    # 打印
    wait_for_element(driver, *LOCATORS["print_text"]).click()
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    time.sleep(3)


def test_excel_import(driver):
    """Excel导入功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 返回首页
    wait_for_element(driver, *LOCATORS["home_back"]).click()
    # 点击不保存
    wait_for_element(driver, *LOCATORS["not_save"]).click()
    # 点击去编辑
    wait_for_element(driver, *LOCATORS["goto_edit"]).click()
    # 点击Excel导入
    wait_for_element(driver, *LOCATORS["kata_excel_import"]).click()
    # 点击本地导入
    wait_for_element(driver, *LOCATORS["local_import"]).click()
    # 选择Excel表格
    wait_for_element(driver, *LOCATORS["file_title"]).click()
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm_tv"]).click()
    # 从商品列表选择三个商品
    wait_for_element(driver, *LOCATORS["select_iv_1"]).click()
    wait_for_element(driver, *LOCATORS["select_iv_2"]).click()
    wait_for_element(driver, *LOCATORS["select_iv_3"]).click()
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm_tv"]).click()
    # 清空输入框内容
    wait_for_element(driver, *LOCATORS["et_edit_Q密怀念"]).clear()
    # 输入新内容
    wait_for_element(driver, *LOCATORS["et_edit_1"]).send_keys('硕方大厦')
    # 点击下一页
    wait_for_element(driver, *LOCATORS["next_page"]).click()
    # 修改内容
    wait_for_element(driver, *LOCATORS["et_edit_mcd"]).send_keys('123')
    # 打印
    wait_for_element(driver, *LOCATORS["print_text"]).click()
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    wait_disappear(driver, *LOCATORS["print_cancel"])


def test_scan_barcode(driver):
    """扫描商品条码功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 返回首页
    wait_for_element(driver, *LOCATORS["home_back"]).click()
    # 点击不保存
    wait_for_element(driver, *LOCATORS["not_save"]).click()
    # 点击去编辑
    wait_for_element(driver, *LOCATORS["goto_edit"]).click()
    # 点击扫描商品条码
    wait_for_element(driver, *LOCATORS["kata_scan_barcode"]).click()
    # 等待手动扫描条码
    time.sleep(5)
    # 清空输入框内容
    wait_for_element(driver, *LOCATORS["et_edit_30"]).clear()
    # 输入新内容
    wait_for_element(driver, *LOCATORS["et_edit_4"]).send_keys('50')
    # 打印
    wait_for_element(driver, *LOCATORS["print_text"]).click()
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    wait_disappear(driver, *LOCATORS["print_cancel"])


def test_create_data(driver):
    """新建商超数据功能测试

    :param driver: WebDriver实例
    :return: None
    """
    # 返回首页
    wait_for_element(driver, *LOCATORS["home_back"]).click()
    # 点击不保存
    wait_for_element(driver, *LOCATORS["not_save"]).click()
    # 点击去编辑
    wait_for_element(driver, *LOCATORS["goto_edit"]).click()
    # 点击我的商品
    wait_for_element(driver, *LOCATORS["kata_my_goods"]).click()
    # 点击新建
    wait_for_element(driver, *LOCATORS["add_commodity"]).click()
    # 输入品名
    wait_for_element(driver, *LOCATORS["name_et"]).send_keys('测试商品')
    # 输入条码
    wait_for_element(driver, *LOCATORS["barcode_et"]).send_keys('6939947707670')
    # 输入零售价
    wait_for_element(driver, *LOCATORS["price_et"]).send_keys('777')
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm_text"]).click()
    # 选择刚才新建的商品打印
    wait_for_element(driver, *LOCATORS["select_iv_1"]).click()
    # 点击确定
    wait_for_element(driver, *LOCATORS["confirm_tv"]).click()
    # 打印
    wait_for_element(driver, *LOCATORS["print_text"]).click()
    wait_for_element(driver, *LOCATORS["tv_confirm"]).click()
    wait_disappear(driver, *LOCATORS["print_cancel"])
