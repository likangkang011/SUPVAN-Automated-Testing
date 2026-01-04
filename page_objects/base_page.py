from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find(self, locator, timeout=None):
        """等待元素可见并返回元素"""
        wait = self.wait if timeout is None else WebDriverWait(
            self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        """点击元素"""
        el = self.find(locator)
        el.click()

    def send_keys(self, locator, text, clear_first=True):
        """输入文本"""
        el = self.find(locator)
        if clear_first:
            el.clear()
        el.send_keys(text)

    def get_text(self, locator):
        """获取元素文本"""
        return self.find(locator).text

    def is_displayed(self, locator, timeout=3):
        """判断元素是否可见"""
        try:
            self.find(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def screenshot(self, filename):
        """保存截图"""
        self.driver.save_screenshot(filename)
