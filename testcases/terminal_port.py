from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver import Keys
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
#切换下一页功能(6次）
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
driver.find_element(By.XPATH,'//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"]').click()
#点击端子端口功能
driver.find_element(By.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="端子/端口"]').click()
#改变端子方向为竖向
#driver.find_element(By.XPATH,'//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/llDirectionV"]/android.widget.ImageView').click()
#清除默认端子个数
driver.find_element(By.ID,"com.fhit.app_iprinter:id/etFrame").clear()
#设置端子格数
driver.find_element(By.ID,"com.fhit.app_iprinter:id/etFrame").send_keys("4")
#清除端子宽度A
driver.find_element(By.ID,"com.fhit.app_iprinter:id/ivClearFirst").click()
#设置端子宽度A    ************************
driver.find_element(By.ID,"com.fhit.app_iprinter:id/etHeight").send_keys("10")
#勾选上绘制边框
driver.find_element(By.ID,"com.fhit.app_iprinter:id/sBorder").click()
#进入输入内容界面
driver.find_element(By.XPATH,'//android.widget.TextView[@text="内容"]').click()
#输入端子内容
driver.find_element(By.XPATH,'(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/adapter_terminal_block_content"])[1]').send_keys("测试1")
#输入端子内容2
driver.find_element(By.XPATH,'(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/adapter_terminal_block_content"])[2]').send_keys("测试2")
#关闭端子端口页面
driver.find_element(By.ID,"com.fhit.app_iprinter:id/dialog_terminal_block_confirm").click()
time.sleep(1)
driver.quit()
