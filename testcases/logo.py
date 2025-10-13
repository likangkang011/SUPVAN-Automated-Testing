from idlelib.search import find_again

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
import time

# 创建 Options 对象并设置 capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "14"
options.device_name = "481QFGEA229CG"
options.app_package = "com.fhit.app_iprinter"
options.app_activity = (".ui.home.activity.HomeActivity")
options.no_reset = True

driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)
#进入编辑页
driver.find_element(By.XPATH, '//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivCreateNew"]').click()
time.sleep(1)
#切换下一页功能(4次）
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
#点击logo选项
driver.find_element(By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="logo"]').click()
time.sleep(5)
#选择第一个logo图标
driver.find_element(By.ID,"com.fhit.app_iprinter:id/ivLogo").click()
time.sleep(1)
driver.quit()

