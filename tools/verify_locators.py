# -*- coding: utf-8 -*-
"""抽样校验：把 locators.py 里指定的 key 在真机上找一遍，确认定位有效。

用法：python tools/verify_locators.py key1 key2 ...
不传参数时校验默认样本（首页/编辑页若干新增条目）。
"""
import sys
import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

sys.path.insert(0, ".")
from locators import LOCATORS

PREFIX = "com.fhit.app_iprinter:id/"
DEFAULT = ["v_device", "cl_connect_device", "tv_customer_service", "ll_serve",
           "htwi_home_page", "htwi_home_create", "iv_create_new"]


def main():
    keys = sys.argv[1:] or DEFAULT
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.device_name = "4b66ddf"
    opts.udid = "4b66ddf"
    opts.app_package = "com.fhit.app_iprinter"
    opts.app_activity = ".ui.home.activity.HomeActivity"
    opts.no_reset = True
    opts.skip_device_initialization = True
    opts.new_command_timeout = 300
    opts.set_capability("enableNotificationListener", False)
    opts.set_capability("uiautomator2ServerLaunchTimeout", 180000)

    d = webdriver.Remote("http://127.0.0.1:4723", options=opts)
    ok = fail = 0
    try:
        d.activate_app("com.fhit.app_iprinter")
        time.sleep(3)
        for k in keys:
            if k not in LOCATORS:
                print(f"✗ {k}: locators.py 里没有这个 key")
                fail += 1
                continue
            by, loc = LOCATORS[k]
            if not isinstance(loc, str):
                print(f"- {k}: 伪定位（{by}），跳过实机校验")
                continue
            t0 = time.time()
            try:
                els = [e for e in d.find_elements(by, loc) if e.is_displayed()]
            except Exception as e:
                print(f"✗ {k}: 查找异常 {type(e).__name__}")
                fail += 1
                continue
            cost = (time.time() - t0) * 1000
            if els:
                r = els[0].rect
                print(f"✓ {k}: 命中 {len(els)} 个（{cost:.0f}ms） rect=({r['x']},{r['y']},{r['width']}x{r['height']}）")
                ok += 1
            else:
                print(f"✗ {k}: 未命中（{cost:.0f}ms）")
                fail += 1
    finally:
        d.quit()
    print(f"\n结果：命中 {ok}，失败 {fail}")


if __name__ == "__main__":
    main()
