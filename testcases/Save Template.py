import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from locators import LOCATORS

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime

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

# 点击保存
driver.find_element(*LOCATORS["save_btn"]).click()
time.sleep(1)

# 输入模板名称
driver.find_element(*LOCATORS["template_name_input"]).send_keys(
        "测试" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
time.sleep(1)

# 点击保存
driver.find_element(*LOCATORS["tv_confirm"]).click()
time.sleep(5)

print("已完成")

# 退出App
driver.quit()
