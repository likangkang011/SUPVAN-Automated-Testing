import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from locators import LOCATORS

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
driver.find_element(*LOCATORS["create_new"]).click()
time.sleep(1)

# 点击下一页
driver.find_element(*LOCATORS["enter_right"]).click()
time.sleep(1)


# 点击Excel
driver.find_element(*LOCATORS["feature_Excel"]).click()
time.sleep(1)

# 打开Excel列表里的第一个文件
driver.find_element(*LOCATORS["excel_filename"]).click()
time.sleep(3)

# 勾选需要导入的列
driver.find_element(*LOCATORS["excel_row_1"]).click()
time.sleep(1)

# 点击生成
driver.find_element(*LOCATORS["create_btn"]).click()
time.sleep(1)

# 点击确定
driver.find_element(*LOCATORS["affirm"]).click()
time.sleep(5)


print("已完成")

# 退出App
driver.quit()
