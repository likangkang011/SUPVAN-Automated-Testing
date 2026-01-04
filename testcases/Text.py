from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


def test_text_input(driver):  # 引用fixture中的driver
    # 点击新建标签（显式等待元素可点击）
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(
            (By.XPATH, '//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivCreateNew"]'))
    ).click()

    # 点击文本（显式等待元素可点击）
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH,
                                    '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]'))
    ).click()

    # 输入内容（显式等待元素可见并可交互）
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located(
            (By.ID, 'com.fhit.app_iprinter:id/etInput'))
    ).send_keys('123')

    # 点击完成（显式等待元素可点击）
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(
            (By.ID, 'com.fhit.app_iprinter:id/ivConfirm'))
    ).click()
