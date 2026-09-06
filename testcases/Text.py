import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from locators import LOCATORS

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


def test_text_input(driver):  # 引用fixture中的driver
    # 点击新建标签（显式等待元素可点击）
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(LOCATORS["create_new"])
    ).click()

    # 点击文本（显式等待元素可点击）
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(LOCATORS["feature_文本"])
    ).click()

    # 输入内容（显式等待元素可见并可交互）
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located(LOCATORS["input_edit"])
    ).send_keys('123')

    # 点击完成（显式等待元素可点击）
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(LOCATORS["confirm"])
    ).click()
