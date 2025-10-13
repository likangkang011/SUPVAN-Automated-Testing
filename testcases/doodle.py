from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
import time

from selenium.webdriver.common.devtools.v137.fed_cm import click_dialog_button

# 创建 Options 对象并设置 capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "14"
options.device_name = "481QFGEA229CG"
options.app_package = "com.fhit.app_iprinter"
options.app_activity = (".ui.home.activity.HomeActivity")
options.no_reset = True

# 使用 options 参数而非 desired_capabilities
driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)
driver.find_element(By.XPATH, '//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivCreateNew"]').click()
time.sleep(1)
#切换下一页功能(5次）
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
#点击涂鸦功能
driver.find_element(By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="涂鸦"]').click()
#定位坐标在涂鸦区域进行涂鸦
driver.swipe(100, 1300, 700, 1300)
driver.swipe(200, 1100, 200, 1500)
driver.swipe(100, 1400, 700, 1400)
time.sleep(3)
#点击确定，关闭涂鸦页面
driver.find_element(By.ID,"com.fhit.app_iprinter:id/ivConfirm").click()
time.sleep(3)
driver.quit()