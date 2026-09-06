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

# 点击文本
driver.find_element(*LOCATORS["feature_文本"]).click()
time.sleep(1)

# 输入123
driver.find_element(*LOCATORS["input_edit"]).send_keys('123')
time.sleep(1)

# 点击完成
driver.find_element(*LOCATORS["confirm"]).click()
time.sleep(1)

# 点击下一页
driver.find_element(*LOCATORS["enter_right"]).click()

# 点击下一页
driver.find_element(*LOCATORS["enter_right"]).click()

# 点击下一页
driver.find_element(*LOCATORS["enter_right"]).click()

# 点击下一页
driver.find_element(*LOCATORS["enter_right"]).click()

# 点击下一页
driver.find_element(*LOCATORS["enter_right"]).click()

# 点击反色
driver.find_element(*LOCATORS["feature_反色"]).click()
time.sleep(1)


# 退出App
driver.quit()
