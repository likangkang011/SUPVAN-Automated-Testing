import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from locators import LOCATORS

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver import Keys
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
# 进入编辑页
driver.find_element(*LOCATORS["create_new"]).click()
# 切换下一页功能(7次）
time.sleep(1)
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
# 点击表格
driver.find_element(*LOCATORS["feature_表格"]).click()
# 打印当前页面尺寸
size = driver.get_window_size()
print(size)

screen_width = size["width"]
screen_height = size["height"]

# 通过拖拽的方式点到其中之一的表格进行输入            *******需要获得屏幕比例滑动（不同机型屏幕尺寸不同）
driver.swipe(
    screen_width * 0.33,
    screen_height * 0.29,
    screen_width * 0.34,
    screen_height * 0.29)
time.sleep(2)
driver.find_element(*LOCATORS["table_attribute"]).click()
time.sleep(2)
driver.find_element(*LOCATORS["table_edit"]).send_keys("表格1")
# 输入表格二的信息
driver.swipe(
    screen_width * 0.67,
    screen_height * 0.29,
    screen_width * 0.66,
    screen_height * 0.29)
driver.find_element(*LOCATORS["table_attribute"]).click()
time.sleep(2)
driver.find_element(*LOCATORS["table_edit"]).send_keys("表格2")
driver.find_element(*LOCATORS["table_affirm"]).click()
print("已完成")
time.sleep(2)
driver.terminate_app('com.fhit.app_iprinter')
driver.quit()
