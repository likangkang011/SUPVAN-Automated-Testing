from page_objects.home_page import home_Page
from page_objects.base_page import BasePage
import time



class TestSwitchDevice:

    def test_click_switch_device(self, driver):
        """验证点击切换设备按钮功能"""
        home = home_Page(driver)
        home.support()