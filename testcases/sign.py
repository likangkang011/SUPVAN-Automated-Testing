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
driver.find_element(By.XPATH, '//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivCreateNew"]').click()
time.sleep(1)
#切换下一页功能(3次）
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
#点击标识
driver.find_element(By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="标识"]').click()
time.sleep(1)
#点击第一个标识符号
driver.find_element(By.ID,"com.fhit.app_iprinter:id/my_item_symbol_tv").click()
time.sleep(1)
driver.quit()