from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import driver
from datetime import datetime
import time
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder

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


def test_select_devices(driver):
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvDeviceName').click()
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvDevice" and @text="T50 Plus"]').click()
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvDevice" and @text="T50 Plus"]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/btnConfirmSelectDevice').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/backIV').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/btnReturnOldVersion').click()
print('已选择T50 Plus机型')

def test_add_all_function(driver):
    # 点击新建标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCreateNew').click()

    # 点击向右切换两次
    for _ in range(2):
        wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    # 点击更多
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="更多"]'
    ).click()

    # 添加编辑功能到功能栏
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="标识"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="边框"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="符号"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="logo"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="序号"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="线"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="涂鸦"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="反色"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="端子/端口"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="日期"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="表格"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="识别"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_back_ll"]/android.widget.ImageView'
    )
print('已添加所有功能到功能栏')

def test_loginin(driver):
    # 返回首页
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_back_ll"]/android.widget.ImageView'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[3]'
    )

    # 去登录
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[3]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/rlPersonalInformationEnter').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/activity_login_phone_et').send_keys('17777786604')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/activity_login_verify_code_et').send_keys('8888')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/activity_login_agree_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/activity_login_confirm_btn').click()
    # 返回首页
    wait_for_element(driver, By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="首页"]').click()

print('登录成功')

def test_connect_devices(driver):
    # 点击去连接

    wait_for_element(driver, By.XPATH, '(/'
                                       ''
                                       ''
                                       ''
                                       ''
                                       ''
                                       '/android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[1]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvGoConnect').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="T0024B2310270013"]'
    ).click()

def test_DIY(driver):
    # 点击新建标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCreateNew').click()

    wait_for_element(
        driver,
        By.ID,
        'com.fhit.app_iprinter:id/ivFirstConnectionClose'
    ).click()

def test_text1(driver):
    # 测试文本功能--双击编辑，添加文本，对齐功能


    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('测试123')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="复制"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="旋转"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="对齐"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivHorizontalLeft').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivVerticalTop').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()

def test_text2(driver):
    # 测试文本功能--最大/最小字号
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('测试123')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()

    for _ in range(20):
        wait_for_element(
            driver,
            By.XPATH,
            '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="缩小"]'
        ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('测试123')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()

    for _ in range(20):
        wait_for_element(
            driver,
            By.XPATH,
            '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="放大"]'
        ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="对齐"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivHorizontalCenter').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivVerticalCenter').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()

def test_font(driver):
    # 测试文本功能--字体功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('测试123')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvFont').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTextFont" and @text="下载更多"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_item_font_adapter_download"])[1]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_font_back').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()

def test_inverse(driver):
    # 测试文本功能--反色功能
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('测试123')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()

    for _ in range(5):
        wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="反色"]'
    ).click()

def test_repeat(driver):
    # 测试文本功能--重复份数
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivRepeat').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_repetition_et').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_repetition_et').send_keys('3')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_repetition_iv_affirm').click()

def test_barcode(driver):
    # 测试一维码功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    for _ in range(5):
        wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_left_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="一维码"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('6901236040287')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()

def test_qrcode(driver):
    # 测试二维码功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="二维码"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('硕方打印')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()

def test_photo(driver):
    # 测试图片功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="图片"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_picture_photo_album_tv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvCheck"])[1]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ps_tv_complete').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/menu_crop').click()
'''
def test_excel(driver):
    # 测试Excel功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="Excel"]'
    ).click()

    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="本地导入"]').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="android:id/title" and @text="1 商品.xls"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//androidx.recyclerview.widget.RecyclerView[@resource-id="com.fhit.app_iprinter:id/rvData"]/android.widget.LinearLayout[1]/android.widget.LinearLayout/android.widget.ImageView'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//androidx.recyclerview.widget.RecyclerView[@resource-id="com.fhit.app_iprinter:id/rvData"]/android.widget.LinearLayout[2]/android.widget.LinearLayout/android.widget.ImageView'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvCreate').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()
'''
def test_shape(driver):
    # 测试形状功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="形状"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivShape"])[1]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCancel').click()

def test_cable_label(driver):
    # 测试线缆标签功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="线缆标签"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etManualFirstFoldedContent').send_keys('测试123')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()

def test_symbol_frame(driver):
    # 测试标识，边框，符号功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="标识"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/my_item_symbol_tv" and @text="0"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="边框"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivBorder"])[2]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCancel').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="符号"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/my_item_symbol_tv" and @text="#"]'
    ).click()

def test_logo(driver):
    # 测试LOGO功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="logo"]'
    ).click()

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivLogo"])[4]'
    ).click()

def test_line(driver):
    # 测试线功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    for _ in range(3):
        wait_for_element(
            driver,
            By.XPATH,
            '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="线"]'
        ).click()

def test_sketch(driver):
    # 测试涂鸦功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="涂鸦"]'
    ).click()

    # 定位坐标在涂鸦区域进行涂鸦
    driver.swipe(100, 1300, 700, 1300)
    driver.swipe(200, 1100, 200, 1500)
    driver.swipe(100, 1400, 700, 1400)
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()

def test_terminal_port(driver):
    # 测试端子/端口功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="端子/端口"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/sBorder').click()
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="内容"]').click()

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/adapter_terminal_block_content"])[1]'
    ).send_keys('测试1')

    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/adapter_terminal_block_content"])[2]'
    ).send_keys('测试2')

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/dialog_terminal_block_confirm').click()

def test_date(driver):
    # 测试日期功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="日期"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/sRealTime').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvReadTip').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/sAddAssociation').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()

def test_table(driver):
    # 测试表格功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_add_segment_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="表格"]'
    ).click()

    size = driver.get_window_size()
    screen_width = size["width"]
    screen_height = size["height"]
    perform_double_tap(driver, x=screen_width*0.33, y=screen_height*0.29)
    wait_visible(
        driver,
        By.ID,
        "com.fhit.app_iprinter:id/window_table_edit"
    ).send_keys("表格1")

    wait_clickable(
        driver,
        By.ID,
        "com.fhit.app_iprinter:id/dialog_table_iv_affirm"
    ).click()

def test_prewiew(driver):
    # 测试预览功能
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_preview_tv').click()

    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]

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

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_interior_handle_iv').click()

def test_savetemplate1(driver):
    # 保存模板
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_save_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etTemplateName').send_keys('文本，一维码模板')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()


def test_savetemplate2(driver):
    # 添加序号模板
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_back_ll"]/android.widget.ImageView'
    ).click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvNotSave').click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCreateNew').click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCanvasRotation').click()
    for _ in range(4):
        wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="序号"]'
    ).click()

    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_prefix').send_keys('前缀')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_suffix').send_keys('后缀')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_start').send_keys('1')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_end').send_keys('5')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()

    # 保存模板
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_save_iv').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etTemplateName').send_keys('序号模板')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()

    #返回
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_back_ll"]/android.widget.ImageView'
).click()

def test_print_personal_template1(driver):
    # 点击我的保存
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvMySave').click()

    # 点击第一个已保存的模板
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_name" and @text="序号模板"]'
    ).click()




    # 点击打印
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[3]'
    ).click()

    # 点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()

    # 等待打印完成
    time.sleep(10)

    # 点击模板
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[4]'
    ).click()

def test_print_personal_template2(driver):
    # 切换成第二个模板
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_name" and @text="文本，一维码模板"]'
    ).click()

    # 点击打印
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[3]'
    ).click()

    time.sleep(2)

    wait_for_element(
        driver,
        By.ID,
        'com.fhit.app_iprinter:id/ivRangeAdd'
    ).click()

    # 设置excel打印范围
    # 安卓端暂时有bug,等待实现
    # 点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()

    # 等待打印完成
    time.sleep(15)

def test_print_system_template(driver):
    # 打印系统模板
    # 点击模板
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[4]'
    ).click()

    # 点击系统模板
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvSystemTemplate').click()

    # 任选一个系统模板
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/mIvTemplateFileItem"])[1]'
    ).click()

    # 点击打印
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[3]'
    ).click()

    # 点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()

def test_print_setting(driver):
    # 点击返回
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_back_ll"]/android.widget.ImageView'
    ).click()

    # 点击不保存
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvNotSave').click()

    size = driver.get_window_size()
    screen_width = size["width"]
    screen_height = size["height"]

    # 需验证能否滑倒底部
    driver.swipe(screen_width * 0.2, screen_height * 0.5, screen_width * 0.2, screen_height * 0.9)

    #断开机器
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvGoConnect"]').click()
    #点击去连接
    wait_for_element(driver, By.XPATH, '(/'
                                       ''
                                       ''
                                       ''
                                       ''
                                       ''
                                       '/android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[1]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvGoConnect').click()
    #连接另一台机器
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="T0213B2512190002"]'
    ).click()

    # 点击新建标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCreateNew').click()

    # 点击耗材
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="耗材"]'
    ).click()

    size = driver.get_window_size()
    screen_width = size["width"]
    screen_height = size["height"]

    # 需验证能否滑倒底部
    driver.swipe(screen_width * 0.2, screen_height * 0.9, screen_width * 0.2, screen_height * 0.5)

    # 选中自定义耗材
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/mTvGroupName" and @text="自定义耗材"]'
    ).click()

    # 点击新增自定义耗材
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/rlCustomConsumablesAdd').click()

    # 设置耗材的宽高
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etConsumableName').send_keys(
        "自定义耗材" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etWidth').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etHeight').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etWidth').send_keys('50')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etHeight').send_keys('30')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivDeletePicture').click()

    # 点击保存
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvSave').click()
    time.sleep(3)
    print('已保存自定义耗材')
    wait_for_element(driver,By.XPATH,'(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/mIvTemplateFileItem"])[1]').click()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivAffirm').click()

    for _ in range(3):
        wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv').click()

    # 点击添加一个边框
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="边框"]'
    ).click()

    # 添加一个边框
    wait_for_element(
        driver,
        By.XPATH,
        '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivBorder"])[2]'
    ).click()

    # 关闭边框弹窗
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivCancel').click()

    # 添加文本
    # 双击编辑区进行编辑
    for _ in range(2):
        wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/my_activity_main_lp_paint_view').click()

    # 输入文本
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('测试123')

    # 点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()

    # 点击打印
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="打印"]'
    ).click()

    # 设置打印份数
    # 清空输入框
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etCopies').clear()

    # 设置打印份数为2
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etCopies').send_keys('2')

    # 水平，垂直偏移为-16
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etHShift').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etHShift').send_keys('-16')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etVShift').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etVShift').send_keys('-16')

    # 点击确定，开始进行打印
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()

    # 点击打印
    wait_for_element(
        driver,
        By.XPATH,
        '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="打印"]'
    ).click()

    # 设置打印份数
    # 清空输入框
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etCopies').clear()

    # 设置打印份数为3
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etCopies').send_keys('3')

    # 打印当前页
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivRangeAdd').click()

    # 设置打印浓度为9
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etDensity').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etDensity').send_keys('9')

    # 水平，垂直偏移为16
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etHShift').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etHShift').send_keys('16')
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etVShift').clear()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/etVShift').send_keys('16')

    size = driver.get_window_size()
    screen_width = size["width"]
    screen_height = size["height"]

    # 打印设置页面上滑
    driver.swipe(screen_width * 0.5, screen_height * 0.5, screen_width * 0.5, screen_height * 0.4)

    # 切换翻转方式为水平翻转
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivFlipAdd').click()

    # 点击确定开始打印
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()

    time.sleep(15)

