from selenium.webdriver.common.by import By
from page_objects.base_page import BasePage


class home_Page(BasePage):
    # 元素定位
    switch_device = (
        By.ID,
        "com.fhit.app_iprinter:id/tvDeviceName")  # "左上角切换设备按钮"
    support = (By.ID, "com.fhit.app_iprinter:id/tvCustomerService")  # 客服按钮

    def click_switch_device(self):
        self.click(self.switch_device)

    def click_support_device(self):
        self.click(self.support)
