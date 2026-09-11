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
options.platform_version = "11"
options.device_name = "fdd0c23f"
options.app_package = "com.fhit.app_iprinter"
options.app_activity = (".ui.home.activity.HomeActivity")
options.no_reset = True

# 使用 options 参数而非 desired_capabilities
driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)
# 进入主页，点击我的
driver.find_element(*LOCATORS["home_mine"]).click()
# 点击头像
driver.find_element(*LOCATORS["personal_info_enter"]).click()
time.sleep(1)
# 输入手机号
driver.find_element(*LOCATORS["login_phone"]).send_keys("19711916427")
# 输入万能验证码8888
driver.find_element(*LOCATORS["login_code"]).send_keys("8888")
# 勾选同意隐私政策
driver.find_element(*LOCATORS["login_agree"]).click()
# 点击登录
driver.find_element(*LOCATORS["login_confirm_btn"]).click()
time.sleep(3)

# driver.find_element(*LOCATORS["confirm"]).click()
# time.sleep(5)
print("已完成")

# 退出App
driver.quit()
