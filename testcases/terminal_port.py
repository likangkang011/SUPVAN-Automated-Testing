import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from locators import LOCATORS

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
driver.find_element(*LOCATORS["create_new"]).click()
time.sleep(1)
# 切换下一页功能(6次）
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
# 点击端子端口功能
driver.find_element(*LOCATORS["feature_端子端口"]).click()
# 改变端子方向为竖向
# driver.find_element(By.XPATH,'//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/llDirectionV"]/android.widget.ImageView').click()
# 清除默认端子个数
driver.find_element(*LOCATORS["terminal_frame"]).clear()
# 设置端子格数
driver.find_element(*LOCATORS["terminal_frame"]).send_keys("4")
# 清除端子宽度A
driver.find_element(*LOCATORS["terminal_clear_first"]).click()
# 设置端子宽度A    ************************
driver.find_element(*LOCATORS["et_height"]).send_keys("10")
# 勾选上绘制边框
driver.find_element(*LOCATORS["terminal_border"]).click()
# 进入输入内容界面
driver.find_element(*LOCATORS["terminal_tab_content"]).click()
# 输入端子内容
driver.find_element(*LOCATORS["terminal_content_1"]).send_keys("测试1")
# 输入端子内容2
driver.find_element(*LOCATORS["terminal_content_2"]).send_keys("测试2")
# 关闭端子端口页面
driver.find_element(*LOCATORS["terminal_confirm"]).click()
time.sleep(1)
driver.quit()
