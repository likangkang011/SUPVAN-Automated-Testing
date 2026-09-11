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

from selenium.webdriver.common.devtools.v137.fed_cm import click_dialog_button


class Test_date(unittest.TestCase):
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
    time.sleep(3)
# 切换下一页功能(7次）
    driver.find_element(*LOCATORS["enter_right"]).click()
    driver.find_element(*LOCATORS["enter_right"]).click()
    driver.find_element(*LOCATORS["enter_right"]).click()
    driver.find_element(*LOCATORS["enter_right"]).click()
    driver.find_element(*LOCATORS["enter_right"]).click()
    driver.find_element(*LOCATORS["enter_right"]).click()
    driver.find_element(*LOCATORS["enter_right"]).click()
# 点击日期功能
    driver.find_element(*LOCATORS["feature_日期"]).click()
# 打开实时时间
    driver.find_element(*LOCATORS["date_realtime"]).click()
    time.sleep(3)
# 首次点击打开实时时间需要点击'我知道了‘
# driver.find_element(*LOCATORS["date_read_tip"]).click()
# 打开星期
    driver.find_element(*LOCATORS["date_week"]).click()
# 打开添加关联时间
    driver.find_element(*LOCATORS["date_add_association"]).click()
# 点击确定
    driver.find_element(*LOCATORS["affirm"]).click()
    time.sleep(3)
# 关闭软件
    driver.quit()
