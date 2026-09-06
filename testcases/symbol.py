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
driver.find_element(*LOCATORS["create_new"]).click()
time.sleep(1)
# 切换下一页功能(3次）
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
driver.find_element(*LOCATORS["enter_right"]).click()
# 点击符号
driver.find_element(*LOCATORS["feature_符号"]).click()
time.sleep(1)
# 添加第一个符号
driver.find_element(*LOCATORS["symbol_first"]).click()
time.sleep(1)
driver.quit()
