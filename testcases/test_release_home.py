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
#------------------底部页面左滑-----------------------------
#------------要修改下，看看怎么调用合适------------------------
def swipe_left(driver):
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]

    start_x = width * 0.8
    start_y = height * 0.75
    end_x = width * 0.3
    end_y = height * 0.75
    driver.swipe(start_x, start_y, end_x, end_y)

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


def wait_disappear(driver, by, locator, timeout=30):
    """等待元素消失（不可见/不存在）"""
    return WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((by, locator))
    )
    #成功登录
def test_login_succeed(driver):
    # 点击我的
    wait_for_element(driver, By.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[3]').click()
    #进入家用风主页
    wait_for_element(driver,By.XPATH, '//android.widget.TextView[@text="进入新版"]').click()
    #点击去登陆
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/btnLogin').click()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/activity_login_phone_et').send_keys('19711916427')
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/activity_login_verify_code_et').send_keys('8888')
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/activity_login_agree_iv').click()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/activity_login_confirm_btn').click()
    #连接机器
def test_connect_devices(driver):
    #点击去连接
    wait_for_element(driver,By.ID, 'com.fhit.app_iprinter:id/tvConnectState').click()
    #匹配连接机器型号，点击连接按钮
    wait_for_element(
        driver,
        By.XPATH,
        f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number1}"]'
    ).click()
def test_add_text(driver):
    #点击去编辑
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvGotoEdit').click()
    #关闭提示信息
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivFirstConnection').click()
    #使用文本功能（双击可直接打开，不用再次点击文本）
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="文本"]').click()
    #输入内容
    wait_for_element(driver,By.CLASS_NAME,'android.widget.EditText').send_keys('添加文本')
    #复制
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="复制"]').click()
    #旋转
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="旋转"]').click()
    #左对齐,上对齐
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tv_align_setting').click()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivHorizontalLeft').click()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivVerticalTop').click()
    #wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tv_complete').click()
def test_add_barcode(driver):
    #关闭功能区
    wait_for_element(driver,By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/iv_close"]').click()
    #新增标签
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/iv_new_label').click()
    #收起预览
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    #打开功能区
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/iv_more_fun').click()
    #点击条形码
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="条形码"]').click()
    #输入条形码内容
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etInput').send_keys('1234567891234')
    #点击确定
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivAffirm').click()




def test_add_qrcode(driver):
    #新增标签
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/iv_new_label').click()
    #收起预览
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    #打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    #导入二维码
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="二维码"]').click()
    #输入二维码内容
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etInput').send_keys('测试二维码')
    #点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()
'''
def test_add_excel(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    # 导入二维码
    wait_for_element(driver, By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="Excel导入"]').click()
    #选择本地导入
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@text="本地导入"]').click()
    #选择excel
    wait_for_element(driver,By.XPATH,'(//android.widget.ImageView[@resource-id="com.android.documentsui:id/icon_thumb"])[1]').click()
    wait_for_element(driver,By.XPATH,'//androidx.recyclerview.widget.RecyclerView[@resource-id="com.fhit.app_iprinter:id/rvData"]/android.widget.LinearLayout[1]/android.widget.LinearLayout/android.widget.ImageView').click()
    wait_for_element(driver,By.XPATH,'//androidx.recyclerview.widget.RecyclerView[@resource-id="com.fhit.app_iprinter:id/rvData"]/android.widget.LinearLayout[2]/android.widget.LinearLayout/android.widget.ImageView').click()
    #点击生成
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvCreate').click()
    #确认生成
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivSimAffirm').click()
'''
def test_add_symbol(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    #添加符号
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="符号"]').click()
    #任选一个符号进行添加
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/my_item_symbol_tv" and @text="!"]').click()
    #收起功能区域
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivKataMyDialogLabelProduce').click()
def test_AI_photo_print(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    #点击AI拍照打印
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="AI拍照打印"]').click()
    #从相册选择
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/dialog_choose_two_item_second_item_btn').click()
    #选择相册的第一张相片
    wait_for_element(driver,By.XPATH,'(//android.view.View[@resource-id="com.fhit.app_iprinter:id/btnCheck"])[1]').click()
    #点击已完成
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ps_tv_complete').click()
    #点击确定
    wait_for_element(driver,By.XPATH,'//androidx.appcompat.widget.LinearLayoutCompat').click()
    '''
def test_template(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    #点击模板
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="模板"]').click()
    #使用第一个系统模板
    wait_for_element(driver,By.XPATH,'(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_name"])[1]').click()
    '''
def test_add_shape(driver):
    #新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    #收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    #打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    #屏幕左滑实现翻页
    swipe_left(driver)
    #添加形状功能
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="形状"]').click()
    #收起形状功能弹窗
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivClose').click()
def test_add_doodle(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    #选择涂鸦功能
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="涂鸦"]').click()
    driver.swipe(100, 1300, 700, 1300)
    driver.swipe(200, 1100, 200, 1500)
    driver.swipe(100, 1400, 700, 1400)
    #点击确定
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivConfirm').click()
    #收起功能区弹窗
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/iv_close').click()
def test_add_date(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择时间功能
    wait_for_element(driver, By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="时间"]').click()
    #关闭时间弹窗
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivBack').click()

def test_add_table(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择表格功能
    wait_for_element(driver, By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="表格"]').click()
    #双击表格的编辑区
    size = driver.get_window_size()
    screen_width = size["width"]
    screen_height = size["height"]
    perform_double_tap(driver, x=450, y=800)
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/window_table_edit').send_keys('表格文本1')
    #点击确定按钮
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/dialog_table_iv_affirm').click()



def test_add_photo(driver):
    # 新增标签
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_new_label').click()
    # 收起预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择图片功能
    wait_for_element(driver, By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="图片"]').click()
    #从相册选择
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/my_dialog_picture_photo_album_tv').click()
    #选择第一张图片
    wait_for_element(driver,By.XPATH,'(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvCheck"])[1]').click()
    #点击已完成
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ps_tv_complete').click()
    #点击确定
    wait_for_element(driver,By.XPATH,'//androidx.appcompat.widget.LinearLayoutCompat').click()
def test_save_template(driver):
    #点击保存
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@text="保存"]').click()
    #清空文本框
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etTemplateName').clear()
    #输入模板名字
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etTemplateName').send_keys('自动化测试模板1')
    #点击保存
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvConfirm').click()
    #点击去查看
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@text="已保存，"]').click()
    #选择模板
    wait_for_element(driver,By.XPATH,'(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_specification"])[1]').click()
def test_print(driver):
    #打印编辑并保存的模板
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@text="打印"]').click()
    #设置excel打印范围
    #wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etExcelLarge').clear()
    #wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etExcelLarge').send_keys('3')
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvConfirm').click()
    wait_disappear(driver,By.ID,'com.fhit.app_iprinter:id/btCancel',)
def test_change_machine(driver):
    #点击返回
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/iv_back').click()
    #不保存
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvNotSave').click()
    #切换机器
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvConnectState').click()
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@text="确定"]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConnectState').click()
    #连接新机器型号
    wait_for_element(
        driver,
        By.XPATH,
        f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="T0174A2409000003"]'
    ).click()
def test_new_template(driver):
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvGotoEdit').click()
    #点击耗材
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tv_material_info_icon').click()
    #自定义耗材
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@text="去自定义标签"]').click()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/inputWidthET').send_keys('50')
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/inputHeightET').send_keys('30')
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/inputGapET').send_keys('3')
    #点击确定
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/confirmTV').click()

def test_add_SEQ(driver):
    # 打开功能区
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_more_fun').click()
    # 屏幕左滑实现翻页
    swipe_left(driver)
    # 选择序号功能
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="序号"]').click()
    #输入起始值
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_start').send_keys('00')
    #输入结束值
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_end').send_keys('03')
    #点击确定
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivAffirm').click()
def test_add_frame(driver):
    #点击边框
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="边框"]').click()
    #选择一个边框
    wait_for_element(driver,By.XPATH,'(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivBorder"])[3]').click()
    #收起弹窗
    wait_for_element(driver, By.ID,'com.fhit.app_iprinter:id/ivKataMyDialogWireFrame').click()
def test_print_settings(driver):
    # 点击打印
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="打印"]').click()
    #打印份数
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etCopies').clear()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etCopies').send_keys('2')
    #打印浓度
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etDensity').clear()
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/etDensity').send_keys('3')
    #打印范围修改为全部页
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/ivRangeAdd').click()
    #打印
    wait_for_element(driver,By.ID,'com.fhit.app_iprinter:id/tvConfirm').click()
    wait_disappear(driver,By.ID,'com.fhit.app_iprinter:id/btCancel',)

def test_multiple_print(driver):
    # 点击我的
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="我的"]').click()
    # 进入新版
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="进入新版"]').click()
    # 点击去连接
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConnectState').click()
    # 连接机器
    wait_for_element(driver,By.XPATH,f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number1}"]').click()
    # 点击去编辑
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvGotoEdit').click()
    # 新建标签
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="新增标签"]').click()
    # 关闭预览
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_home_style_hide_preview').click()
    # 清空输入框内容
    wait_for_element(driver, By.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="1.99"])').clear()
    # 输入新内容
    wait_for_element(driver, By.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit"])[4]').send_keys('999')
    # 打印
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="打印"]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()
    time.sleep(3)

def test_excel_import(driver):
    # 返回首页
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_back').click()
    # 点击不保存
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvNotSave').click()
    # 点击去编辑
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvGotoEdit').click()
    # 点击Excel导入
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="Excel导入"]').click()
    # 点击本地导入
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="本地导入"]').click()
    # 选择Excel表格
    wait_for_element(driver,By.XPATH,'//android.widget.TextView[@resource-id="android:id/title" and @text="商品测试数据.xlsx"]').click()
    # 点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/confirmTV').click()
    # 从商品列表选择三个商品
    wait_for_element(driver,By.XPATH,'(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[1]').click()
    wait_for_element(driver,By.XPATH,'(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[2]').click()
    wait_for_element(driver,By.XPATH,'(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[3]').click()
    # 点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/confirmTV').click()
    # 清空输入框内容
    wait_for_element(driver, By.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="Q密怀念"]').clear()
    # 输入新内容
    wait_for_element(driver, By.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit"])[1]').send_keys('硕方大厦')
    # 点击下一页
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/ivNextPage').click()
    # 修改内容
    wait_for_element(driver, By.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="麦兜星迷你乐趣蛋"]').send_keys('123')
    # 打印
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="打印"]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()
    wait_disappear(driver,By.ID,'com.fhit.app_iprinter:id/btCancel')

def test_scan_barcode(driver):
    # 返回首页
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_back').click()
    # 点击不保存
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvNotSave').click()
    # 点击去编辑
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvGotoEdit').click()
    # 点击扫描商品条码
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="扫描商品条码"]').click()
    # 等待手动扫描条码
    time.sleep(5)
    # 清空输入框内容
    wait_for_element(driver, By.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="30"]').clear()
    # 输入新内容
    wait_for_element(driver, By.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit"])[4]').send_keys('50')
    # 打印
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="打印"]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()
    wait_disappear(driver,By.ID,'com.fhit.app_iprinter:id/btCancel')

def test_create_data(driver):
    # 返回首页
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/iv_back').click()
    # 点击不保存
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvNotSave').click()
    # 点击去编辑
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvGotoEdit').click()
    # 点击我的商品
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="我的商品"]').click()
    # 点击新建
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/addCommodityIV').click()
    # 输入品名
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/nameET').send_keys('测试商品')
    # 输入条码
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/barcodeET').send_keys('6939947707670')
    # 输入零售价
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/priceET').send_keys('777')
    # 点击确定
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="确定"]').click()
    # 选择刚才新建的商品打印
    wait_for_element(driver, By.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[1]').click()
    # 点击确定
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/confirmTV').click()
    # 打印
    wait_for_element(driver, By.XPATH, '//android.widget.TextView[@text="打印"]').click()
    wait_for_element(driver, By.ID, 'com.fhit.app_iprinter:id/tvConfirm').click()
    wait_disappear(driver,By.ID,'com.fhit.app_iprinter:id/btCancel')



