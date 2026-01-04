from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
import time


# 创建 Options 对象并设置 capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "15"
options.device_name = "4b66ddf"
options.app_package = "com.fhit.app_iprinter"
options.app_activity = (".ui.home.activity.HomeActivity")
options.no_reset = True

# 使用 options 参数而非 desired_capabilities
driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)

# 点击新建标签按钮
driver.find_element(
    By.XPATH,
    '//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivCreateNew"]').click()
time.sleep(1)

# 点击下一页
driver.find_element(
    By.ID,
    "com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv").click()
time.sleep(1)

# 点击下一页
driver.find_element(
    By.ID,
    "com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv").click()
time.sleep(1)

# 点击线缆标签
driver.find_element(
    By.XPATH,
    '(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text=\'线缆标签\'])[1]').click()
time.sleep(1)

# 输入内容
driver.find_element(
    By.ID,
    'com.fhit.app_iprinter:id/etManualFirstFoldedContent').send_keys('测试')
time.sleep(3)

# 点击确定
driver.find_element(By.ID, 'com.fhit.app_iprinter:id/ivAffirm').click()
time.sleep(3)

print("已完成")

# 退出App
driver.quit()
