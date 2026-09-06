import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from locators import LOCATORS

import unittest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time


class Test_223(unittest.TestCase):
    # 创建 Options 对象并设置 capabilities
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "15"
    options.device_name = "4b66ddf"
    options.app_package = "com.fhit.app_iprinter"
    options.app_activity = (".ui.home.activity.HomeActivity")
    options.no_reset = True

    driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)
    # 进入标签页
    driver.find_element(*LOCATORS["create_new"]).click()
    time.sleep(3)

    # 获取并且打印当前页面
    current_context = driver.current_context
    print(current_context)
    # 点击一维码
    driver.find_element(*LOCATORS["feature_一维码"]).click()
    time.sleep(1)
    # 定位输入框并输入
    driver.find_element(*LOCATORS["input_edit"]).send_keys("6923569204532")
    # 关闭一维码编辑页
    driver.find_element(*LOCATORS["affirm"]).click()
    time.sleep(2)

    driver.quit()
