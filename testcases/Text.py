from selenium.webdriver.common.by import By
import time

def test_text_input(driver):  # 引用fixture中的driver
    # 点击新建标签
    driver.find_element(By.XPATH, '//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivCreateNew"]').click()
    time.sleep(1)
    # 点击文本
    driver.find_element(By.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]').click()
    time.sleep(1)
    # 输入内容
    driver.find_element(By.ID, 'com.fhit.app_iprinter:id/etInput').send_keys('pytest1')
    time.sleep(1)
    # 点击完成
    driver.find_element(By.ID, 'com.fhit.app_iprinter:id/ivConfirm').click()