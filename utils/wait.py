from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_element(driver, locator, timeout=10):
    """等待元素可见并返回元素"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )