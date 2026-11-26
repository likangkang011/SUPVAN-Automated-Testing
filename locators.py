# -*- coding: utf-8 -*-
# 打印机编号：全项目唯一数据源。
# 下面的 LOCATORS["device_num1/2/3"] 用 f-string 把它们拼进 XPath；
# run_gui.py 的「测试参数」窗口改的也是这几行。用例文件不要再定义 device_number* 副本。
device_number1 = "T0186A2602270010"  # 第一台打印机编号（官方耗材）
device_number2 = "T0172A2025071472"  # 第二台打印机编号(自定义耗材)
device_number3 = "T0148B2607100001"  # 第三台打印机编号（商超耗材）
"""
元素定位统一管理文件
====================
本项目所有测试用例的元素定位（By 类型 + selector）集中在此处维护，
测试用例中通过语义化 key 引用，例如：

    wait_for_element(driver, *LOCATORS["add_label"]).click()

修改元素定位时，只需改这里，无需改动测试用例。
"""
from appium.webdriver.common.appiumby import AppiumBy


# 伪定位方式：值为「屏幕比例坐标」 (x_ratio, y_ratio)，取值范围 0~1，
# 运行时按 driver.get_window_size() 的实际分辨率换算成像素 —— 换机型/模拟器不用改。
# 用于「元素定位彻底失效、只能盲点」的场景，配 utils.element_helper.tap_ratio 使用。
COORDINATE = "coordinate"

# 伪定位方式：值为「候选定位组」，按顺序逐个尝试，第一个命中的生效。
# 用于「同一个控件在不同 ROM / App 版本里定位完全不同」的场景（典型：系统相册）。
# 写法必须是 tuple 套 tuple（不能写 list，否则下面反向索引会因不可哈希报错）：
#     "key": (MULTI, ((AppiumBy.XPATH, "..."), (AppiumBy.ID, "...")))
# 配 utils.element_helper.find_any / click_any 使用。
MULTI = "multi"


LOCATORS = {
    # ================= 通用 =================
    "create_new": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCreateNew"),            # 新建标签
    "add_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiSettingLabelAdd"),     # 新增标签（标签+号）
    "input_edit": (AppiumBy.ID, "com.fhit.app_iprinter:id/etInput"),               # 内容输入框
    "confirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivConfirm"),                # 确定（文本编辑）
    "affirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivAffirm"),                  # 确定（条码/耗材等）
    "tv_confirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConfirm"),             # 确定（保存模板/打印）
    "cancel": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCancel"),                  # 取消
    # 编辑区画布：原 id 定位已失效，改为坐标盲点（屏幕左右居中、垂直 2/3 处）
    "view": (COORDINATE, (0.5, 1 / 3)),  # 编辑区画布（坐标盲点，非元素定位）
    "enter_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"),  # 功能栏右翻
    "enter_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_enter_left_iv"),    # 功能栏左翻
    "go_connect": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvGoConnect"),           # 去连接
    "main_back_btn": (AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_back_ll"]/android.widget.ImageView'),  # 主页返回
    "back_btn": (AppiumBy.XPATH, '//android.view.ViewGroup[@resource-id="com.fhit.app_iprinter:id/clPageTitle"]/android.widget.ImageView'),  # 页头返回
    "Function Bar_5": (AppiumBy.XPATH,'(//android.view.ViewGroup[@resource-id="com.fhit.app_iprinter:id/llKataMyObjectSetting"])[5]'),    # 专业风功能栏第五个元素，用于实现左滑动能
    "Function Bar_1": (AppiumBy.XPATH,'(//android.view.ViewGroup[@resource-id="com.fhit.app_iprinter:id/llKataMyObjectSetting"])[1]'),    # 专业风功能栏第1个元素，用于实现右滑动能


    # ================= 登录 =================
    "personal_info_enter": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlPersonalInformationEnter"),  # 个人中心入口
    "login_phone": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_login_phone_et"),             # 手机号输入框
    "login_code": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_login_verify_code_et"),        # 验证码输入框
    "login_agree": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_login_agree_iv"),             # 同意协议勾选
    "login_confirm_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_login_confirm_btn"),    # 登录按钮
    "iv_icon_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[1]'),  # 首页图标1（去连接）
    "iv_icon_3": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[3]'),  # 首页图标3（我的）
    "iv_icon_4": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivIcon"])[4]'),  # 首页图标4（模板）
    "home_tab": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="首页"]'),  # 首页Tab
    "first_connection_close": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFirstConnectionClose"),   # 首次连接引导关闭

    # ================= 功能栏入口（金刚区/横向滚动） =================
    "text": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="文本"]'),      # 文本
    "excel": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="Excel"]'),   # Excel
    "more": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="更多"]'),     # 更多
    "feature_反色": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="反色"]'),
    "feature_一维码": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="一维码"]'),
    "feature_二维码": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="二维码"]'),
    "feature_图片": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="图片"]'),
    "feature_Excel": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="Excel"]'),
    "feature_形状": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="形状"]'),
    "feature_线缆标签": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="线缆标签"]'),
    "feature_标识": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="标识"]'),
    "feature_边框": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="边框"]'),
    "feature_符号": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="符号"]'),
    "feature_logo": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="logo"]'),
    "feature_线": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="线"]'),
    "feature_涂鸦": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="涂鸦"]'),
    "feature_端子端口": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="端子/端口"]'),
    "feature_日期": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="日期"]'),
    "feature_表格": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="表格"]'),
    "feature_序号": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="序号"]'),

    # ================= 添加功能弹窗（tvTabTitle 各Tab） =================
    "tab_标识": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="标识"]'),
    "tab_边框": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="边框"]'),
    "tab_符号": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="符号"]'),
    "tab_logo": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="logo"]'),
    "tab_序号": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="序号"]'),
    "tab_涂鸦": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="涂鸦"]'),
    "tab_反色": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="反色"]'),
    "tab_端子端口": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="端子/端口"]'),
    "tab_日期": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="日期"]'),
    "tab_表格": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="表格"]'),
    "tab_识别": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTabTitle" and @text="识别"]'),

    # ================= 文本编辑 =================
    "copy_btn": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="复制"]'),      # 复制
    "rotate_btn": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="旋转"]'),    # 旋转
    "align_btn": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="对齐"]'),      # 对齐
    "shrink_btn": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="缩小"]'),     # 缩小
    "enlarge_btn": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="放大"]'),    # 放大
    "align_h_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHorizontalLeft"),        # 水平左对齐
    "align_h_center": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHorizontalCenter"),    # 水平居中对齐
    "align_v_top": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivVerticalTop"),            # 垂直顶对齐
    "align_v_center": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivVerticalCenter"),      # 垂直居中对齐
    "setting_align": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiSettingAlign"),        # 对齐设置
    "keyboard_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvKeyboard"),              # 键盘（唤起软键盘输入）

    # ================= 文本样式 =================
    "typeface": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTypeface"),                  # 样式
    "layout_mode_switch": (AppiumBy.ID, "com.fhit.app_iprinter:id/sLayoutMode"),       # 自动换行开关
    "word_width_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivWordWidthAdd"),        # 字宽放大
    "text_direction_c": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivTextDirectionC"),    # 弧形文字方向
    "effect_italic": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEffectItalic"),              # 字效-倾斜
    "effect_underline": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEffectUnderline"),           # 字效-下划线
    "font_size_auto": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFontSizeAuto"),        # 自动字号
    "font_space": (AppiumBy.ID, "com.fhit.app_iprinter:id/etFontSpace"),               # 字间距输入框
    "line_space": (AppiumBy.ID, "com.fhit.app_iprinter:id/etLineSpace"),               # 行间距输入框
    "font_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFont"),                      # 字体
    "font_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_font_back"),      # 字体页返回
    "download_more_font": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTextFont" and @text="下载更多"]'),  # 下载更多字体
    "download_more_font2": (AppiumBy.XPATH,'(//android.view.ViewGroup[@resource-id="com.fhit.app_iprinter:id/rlFont"])[8]'),   # 点击字体列表里第八个，下载更多字体
    "font_download_item_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_item_font_adapter_download"])[1]'),  # 字体下载项1
    "font_download_item_2": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_item_font_adapter_download"])[2]'),  # 字体下载项2


    # ================= 重复份数 =================
    "repeat_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiSettingRepeat"),                  # 重复份数入口
    "repeat_input": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_repetition_et"),  # 份数输入框
    "repeat_affirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_repetition_iv_affirm"),  # 份数确定

    # ================= 一维码 =================
    "barcode_chars_switch": (AppiumBy.ID, "com.fhit.app_iprinter:id/sChars"),          # 字符开关
    "barcode_type_dropdown": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivDown"),         # 条码类型下拉
    "barcode_type_code11": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/label" and @text="CODE-11"]'),  # 类型CODE-11
    "char_size_input": (AppiumBy.ID, "com.fhit.app_iprinter:id/etCharacter"),          # 字符字号输入框
    "chars_bold": (AppiumBy.ID, "com.fhit.app_iprinter:id/sCharsBold"),                # 字符加粗
    "align_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivAlignRight"),             # 居右对齐
    "barcode_typeface": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTypeFace"),          # 条码字体（注意与样式tvTypeface不同）

    # ================= 图片 =================
    "photo_album": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_picture_photo_album_tv"),  # 相册
    # --- 以下两条是 app 自带图库的 id：app 改调系统相册后已不再出现，保留供旧版本回滚参考 ---
    "photo_check_1": (AppiumBy.XPATH, '(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvCheck"])[1]'),  # 选中第1张（旧版 app 图库，已失效）
    "photo_complete": (AppiumBy.ID, "com.fhit.app_iprinter:id/ps_tv_complete"),        # 完成（旧版 app 图库，已失效）
    # 系统相册：各 ROM 结构完全不同（实测 OPPO ColorOS / 小米 MIUI），这里放「跨厂商通用的语义定位」，
    # 厂商专属定位放 utils/photo_picker.py 的 PICKER_PROFILES（按图库包名优先匹配）。
    # 通用逻辑：缩略图的 content-desc 一定带日期，且「最新一张」排在最前。
    "photo_pick_first": (MULTI, (  # 系统相册第一张（最新一张），通用语义候选
        (AppiumBy.XPATH, '//*[contains(@content-desc,"第 1 项")]'),                       # OPPO ColorOS：",第 1 项,图片,,日期"
        (AppiumBy.XPATH, '(//*[starts-with(@content-desc,"照片") and string-length(@content-desc) > 3])[1]'),  # 小米/华为："照片，日期"（排除同名 tab）
        (AppiumBy.XPATH, '(//*[contains(@content-desc,"年") and contains(@content-desc,"月") and contains(@content-desc,"日")])[1]'),  # 通用：desc 带日期
        (AppiumBy.XPATH, '(//*[contains(@content-desc,"Photo")])[1]'),                    # 英文系统
    )),  # 系统相册第一张（最新一张）
    "photo_pick_confirm": (MULTI, (  # 相册「完成/确定」，只有多选模式才出现
        (AppiumBy.XPATH, '//*[@text="完成"]'),
        (AppiumBy.XPATH, '//*[@text="确定"]'),
        (AppiumBy.XPATH, '//*[@text="添加"]'),
        (AppiumBy.XPATH, '//*[@content-desc="完成"]'),
        (AppiumBy.XPATH, '//*[@content-desc="确定"]'),
    )),  # 相册「完成/确定」（单选点完自动返回，没有这个按钮）
    "menu_crop": (AppiumBy.ID, "com.fhit.app_iprinter:id/menu_crop"),                  # 裁剪

    # ================= Excel =================
    "create_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvCreate"),                  # 创建
    "local_import": (AppiumBy.XPATH, '//android.widget.TextView[@text="本地导入"]'),    # 本地导入
    "file_title": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="android:id/title" and @text="商品测试数据.xlsx"]'),  # 目标文件
    "excel_row_1": (AppiumBy.XPATH, '//androidx.recyclerview.widget.RecyclerView[@resource-id="com.fhit.app_iprinter:id/rvData"]/android.widget.LinearLayout[1]/android.widget.LinearLayout/android.widget.ImageView'),  # 数据行1
    "excel_row_2": (AppiumBy.XPATH, '//androidx.recyclerview.widget.RecyclerView[@resource-id="com.fhit.app_iprinter:id/rvData"]/android.widget.LinearLayout[2]/android.widget.LinearLayout/android.widget.ImageView'),  # 数据行2

    # ================= 形状 =================
    "shape_item_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivShape"])[1]'),  # 形状1

    # ================= 线缆标签 =================
    "cable_first_content": (AppiumBy.ID, "com.fhit.app_iprinter:id/etManualFirstFoldedContent"),       # 第一折内容
    "cable_second_content": (AppiumBy.ID, "com.fhit.app_iprinter:id/etManualSecondFoldedContent"),     # 第二折内容
    "cable_align_upper_lower_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAlignUpperLowerLeft"),   # 展示效果4
    "cable_both_different": (AppiumBy.ID, "com.fhit.app_iprinter:id/llBothDifferent"),                 # 两折不同
    "cable_second_fold": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSecondFold"),                       # 第二折
    "cable_typeface": (AppiumBy.ID, "com.fhit.app_iprinter:id/clTypeFace"),                            # 字体
    "cable_effect": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvEffect"),                                # 字效
    "cable_effect_bold": (AppiumBy.ID, "com.fhit.app_iprinter:id/llEffectB"),                          # 加粗
    "cable_effect_italic": (AppiumBy.ID, "com.fhit.app_iprinter:id/llEffectI"),                        # 斜体
    "font_kaiti": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTextFont" and @text="楷体"]'),  # 楷体
    "font_heiti": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTextFont" and @text="黑体"]'),  # 黑体
    "font_zhanku": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTextFont" and @text="站酷快乐体"]'),  # 站酷快乐体

    # ================= 标识/符号 =================
    "symbol_0": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/my_item_symbol_tv" and @text="0"]'),  # 标识0
    "symbol_hash": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/my_item_symbol_tv" and @text="#"]'),  # 符号#
    "border_item_2": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivBorder"])[2]'),  # 边框2
    "logo_item_4": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivLogo"])[4]'),  # logo4

    # ================= 涂鸦 =================
    "eraser": (AppiumBy.ID, "com.fhit.app_iprinter:id/llEraser"),                        # 橡皮
    "revocation": (AppiumBy.ID, "com.fhit.app_iprinter:id/llRevocation"),                # 撤销
    "recover": (AppiumBy.ID, "com.fhit.app_iprinter:id/llRecover"),                      # 恢复

    # ================= 端子/端口 =================
    "terminal_border": (AppiumBy.ID, "com.fhit.app_iprinter:id/sBorder"),                # 绘制边框
    "terminal_clear_second": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivClearSecond"),    # 清除端子宽度
    "et_width": (AppiumBy.ID, "com.fhit.app_iprinter:id/etWidth"),                       # 宽度输入框
    "terminal_frame": (AppiumBy.ID, "com.fhit.app_iprinter:id/etFrame"),                 # 端子格数
    "terminal_line_rectangle": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivLineRectangle"),  # 分割线样式
    "terminal_tab_content": (AppiumBy.XPATH, '//android.widget.TextView[@text="内容"]'),   # 内容Tab
    "terminal_tab_style": (AppiumBy.XPATH, '//android.widget.TextView[@text="样式"]'),     # 样式Tab
    "terminal_tab_font": (AppiumBy.XPATH, '//android.widget.TextView[@text="字体"]'),      # 字体Tab
    "terminal_content_1": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/adapter_terminal_block_content"])[1]'),  # 端子内容1
    "terminal_content_2": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/adapter_terminal_block_content"])[2]'),  # 端子内容2
    "terminal_font_space": (AppiumBy.ID, "com.fhit.app_iprinter:id/fragment_terminal_block_style_font_space"),       # 字间距
    "terminal_line_space": (AppiumBy.ID, "com.fhit.app_iprinter:id/fragment_terminal_block_style_line_space"),       # 行间距
    "terminal_effect_bold": (AppiumBy.ID, "com.fhit.app_iprinter:id/fragment_terminal_block_style_effect_bold"),     # 加粗
    "terminal_effect_italic": (AppiumBy.ID, "com.fhit.app_iprinter:id/fragment_terminal_block_style_effect_italic"), # 斜体
    "terminal_effect_underline": (AppiumBy.ID, "com.fhit.app_iprinter:id/fragment_terminal_block_style_effect_underline"),  # 下划线
    "terminal_confirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/dialog_terminal_block_confirm"),  # 端子确定

    # ================= 日期 =================
    "date_realtime": (AppiumBy.ID, "com.fhit.app_iprinter:id/sRealTime"),                # 实时时间
    "date_read_tip": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvReadTip"),                # 读数提示
    "date_week": (AppiumBy.ID, "com.fhit.app_iprinter:id/sWeek"),                        # 星期开关
    "date_prefix_dropdown": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivTimePrefixPullDown"),  # 前缀下拉框
    "date_first_prefix": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFirstPrefix"),        # 生产日期前缀
    "date_add_association": (AppiumBy.ID, "com.fhit.app_iprinter:id/sAddAssociation"),   # 添加关联

    # ================= 表格 =================
    "table_edit": (AppiumBy.ID, "com.fhit.app_iprinter:id/window_table_edit"),           # 表格编辑框
    "table_affirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/dialog_table_iv_affirm"),    # 表格确定

    # ================= 预览 =================
    "preview_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_preview_tv"),           # 预览
    "close_preview": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_interior_handle_iv"),  # 收起预览

    # ================= 保存模板 =================
    "save_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_save_iv"),    # 保存
    "template_name_input": (AppiumBy.ID, "com.fhit.app_iprinter:id/etTemplateName"),      # 模板名输入框
    "not_save": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvNotSave"),                      # 不保存
    "canvas_rotation": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCanvasRotation"),        # 标签旋转

    # ================= 序号 =================
    "sequence_style_dropdown": (AppiumBy.XPATH, '//androidx.viewpager.widget.ViewPager[@resource-id="com.fhit.app_iprinter:id/cvpFrame"]/android.widget.FrameLayout/android.widget.LinearLayout/android.view.ViewGroup/android.widget.ImageView[1]'),  # 样式下拉框
    "sequence_style_0999": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="0-999"]'),  # 样式0-999
    "seq_prefix": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_prefix"),  # 前缀
    "seq_suffix": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_suffix"),  # 后缀
    "seq_start": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_start"),    # 起始值
    "seq_end": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_et_end"),        # 结束值
    "seq_clear_interval": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivClearInterval"),               # 清空间隔
    "seq_interval": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_et_interval"),      # 间隔

    # ================= 打印 =================
    "my_save": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMySave"),                      # 我的保存
    "print_cancel": (AppiumBy.ID, "com.fhit.app_iprinter:id/btCancel"),                 # 打印取消（等待消失）
    "range_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivRangeAdd"),                  # 打印当前页/范围
    "system_template": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSystemTemplate"),      # 系统模板
    "template_tab": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="模板"]'),  # 模板Tab
    "template_file_item_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/mIvTemplateFileItem"])[1]'),  # 模板项1
    "template_序号": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_name" and @text="序号模板"]'),  # 已存模板-序号
    "template_文本一维码": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_name" and @text="文本，一维码模板"]'),  # 已存模板-文本一维码

    # ================= 自定义耗材 =================
    "consumable_tab": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="耗材"]'),  # 耗材Tab
    "consumable_custom_group": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/mTvGroupName" and @text="自定义耗材"]'),  # 自定义耗材分组
    "consumable_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlCustomConsumablesAdd"),  # 新增自定义耗材
    "consumable_name": (AppiumBy.ID, "com.fhit.app_iprinter:id/etConsumableName"),       # 耗材名称
    "et_height": (AppiumBy.ID, "com.fhit.app_iprinter:id/etHeight"),                     # 高度输入框
    "consumable_gap": (AppiumBy.ID, "com.fhit.app_iprinter:id/etDieCuttingInterval"),    # 间隙输入框
    "consumable_delete_picture": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivDeletePicture"),  # 删除图片
    "consumable_save": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSave"),                 # 保存
    # 画布/编辑区：同 view，id 定位已失效，改坐标盲点（双击进入编辑）
    "paint_view": (COORDINATE, (0.5, 1 / 3)),  # 画布/编辑区（坐标盲点，双击进入编辑）

    # ================= 打印设置 =================
    "print_tab": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="打印"]'),  # 打印Tab
    "copies_input": (AppiumBy.ID, "com.fhit.app_iprinter:id/etCopies"),                  # 打印份数
    "h_shift": (AppiumBy.ID, "com.fhit.app_iprinter:id/etHShift"),                       # 水平偏移
    "v_shift": (AppiumBy.ID, "com.fhit.app_iprinter:id/etVShift"),                       # 垂直偏移
    "density": (AppiumBy.ID, "com.fhit.app_iprinter:id/etDensity"),                      # 打印浓度
    "flip_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFlipAdd"),                     # 水平翻转

    # ================= 旧版UI补充 =================
    "home_mine": (AppiumBy.ID, "com.fhit.app_iprinter:id/htwiHomeMine"),                 # 我的tab
    "excel_filename": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvExcelName"),             # Excel文件名
    "logo_first": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivLogo"),                      # 第一个logo
    "symbol_first": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_item_symbol_tv"),         # 第一个符号
    "terminal_clear_first": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivClearFirst"),      # 清除端子宽度A
    "table_attribute": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="属性"]'),  # 表格属性
    "border_item_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivBorder"])[1]'),  # 边框1
    "feature_文本": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="文本"]'),  # 文本（横向滚动）

    # ================= 家用风新版UI：首页/编辑 =================
    "enter_new_version": (AppiumBy.XPATH, '//android.widget.TextView[@text="进入新版"]'),  # 进入新版
    "my_tab": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="我的"]'),  # 我的tab（新版）
    "login_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/btnLogin"),                     # 去登录
    "connect_state": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvDeviceName"),             # 连接状态/切换机器
    "connect_down": (AppiumBy.XPATH, '//android.widget.TextView[@text="确定"]'),       # 断开连接按钮
    "goto_edit": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvGotoEdit"),                   # 去编辑
    "first_connection": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFirstConnection"),     # 新建标签引导关闭
    "new_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_new_label"),                 # 新增标签（新版）
    "hide_preview": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_home_style_hide_preview"),  # 收起预览
    "more_fun": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_more_fun"),                   # 打开功能区
    "align_setting": (AppiumBy.ID, "com.fhit.app_iprinter:id/tv_align_setting"),         # 对齐设置
    "edit_text_class": (AppiumBy.CLASS_NAME, "android.widget.EditText"),                 # 输入框（class定位）
    "back": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivBack"),                            # 关闭时间弹窗
    "home_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_back"),                      # 返回
    "material_info_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/tv_material_info_icon"),  # 耗材信息图标
    "quick_login_btn":(AppiumBy.XPATH,'//android.widget.TextView[@text="其他手机号登录"]'),#快捷登录页面使用手机号登录

    # ================= 家用风新版UI：功能区入口（tvKataMyObjectSetting） =================

    "home_text": (AppiumBy.XPATH,'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="文本"]'),
    "kata_barcode": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="条形码"]'),
    "kata_qrcode": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="二维码"]'),
    "kata_excel_import": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="Excel导入"]'),
    "kata_symbol": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="符号"]'),
    "kata_ai_photo": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="AI拍照打印"]'),
    "kata_shape": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="形状"]'),
    "kata_sketch": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="涂鸦"]'),
    "kata_time": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="时间"]'),
    "kata_table": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="表格"]'),
    "kata_photo": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="图片"]'),
    "kata_seq": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="序号"]'),
    "kata_frame": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="边框"]'),
    "kata_new_label": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="新增标签"]'),
    "kata_scan_barcode": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="扫描商品条码"]'),
    "kata_my_goods": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="我的商品"]'),

    # ====================家用风新版UI：文本样式（样式/字体/对齐）===========================

    "text_style": (AppiumBy.ID,'com.fhit.app_iprinter:id/tv_style_setting'),                               #样式按钮
    "text_italic": (AppiumBy.ID,'com.fhit.app_iprinter:id/ivKataMyFragmentStyleItalic'),                   #斜体字效
    "text_strikethrough": (AppiumBy.ID,'com.fhit.app_iprinter:id/ivKataMyFragmentStyleStrikeThrough'),     #删除线字效
    "text_underline": (AppiumBy.ID,'com.fhit.app_iprinter:id/ivKataMyFragmentStyleUnderLine'),             #下划线字效
    "text_align_left":(AppiumBy.ID,'com.fhit.app_iprinter:id/rbKataMyFragmentAlignLeft'),                  #文本居左
    "text_align_center": (AppiumBy.ID, 'com.fhit.app_iprinter:id/rbKataMyFragmentAlignCenter'),            #文本居中
    "text_align_right": (AppiumBy.ID, 'com.fhit.app_iprinter:id/rbKataMyFragmentAlignRight'),              #文本居右
    "text_auto_return": (AppiumBy.ID, 'com.fhit.app_iprinter:id/swAutoReturn'),                            #自动换行
    "text_auto_size": (AppiumBy.ID, 'com.fhit.app_iprinter:id/cbFontSizeAuto'),                            #自动字号
    "text_font_space_min": (AppiumBy.ID, 'com.fhit.app_iprinter:id/ivFontSpaceMin'),                       #字间距（减）
    "text_font_space_max": (AppiumBy.ID, 'com.fhit.app_iprinter:id/ivFontSpaceMax'),                       #字间距（加）
    "text_line_space_min": (AppiumBy.ID, 'com.fhit.app_iprinter:id/ivLineSpaceMin'),                       #行间距（减）
    "text_line_space_max": (AppiumBy.ID, 'com.fhit.app_iprinter:id/ivLineSpaceMax'),                       #行间距（加）
    #文本元素方向滑动只记住x/y的变化即可

    # ================= 家用风新版UI：Excel/导入 =================
    "sim_affirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivSimAffirm"),                 # 确认生成Excel
    "documentsui_icon_thumb_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.android.documentsui:id/icon_thumb"])[1]'),  # 文件选择器第1项
    "select_iv_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[1]'),  # 商品选择1
    "select_iv_2": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[2]'),  # 商品选择2
    "select_iv_3": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[3]'),  # 商品选择3
    "next_page": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivNextPage"),                   # 下一页

    # ================= 家用风新版UI：符号/边框/形状/涂鸦 =================
    "symbol_exclamation": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivSvgSymbol"])[1]'),  # 符号!
    "label_produce_close": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivKataMyDialogLabelProduce"),  # 收起功能区域
    "border_item_3": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/ivBorder"])[3]'),  # 边框3
    "wire_frame_close": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivKataMyDialogWireFrame"),  # 收起边框弹窗
    "close": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivClose"),                          # 关闭（形状弹窗）
    "close2": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_close"),                        # 关闭（功能区弹窗）

    # ================= 家用风新版UI：图片/AI拍照 =================
    "choose_album": (AppiumBy.ID, "com.fhit.app_iprinter:id/dialog_choose_two_item_second_item_btn"),  # 从相册选择
    "photo_btn_check_1": (AppiumBy.XPATH, '(//android.view.View[@resource-id="com.fhit.app_iprinter:id/btnCheck"])[1]'),  # 选择第1张相片
    "appcompat_linear_layout": (AppiumBy.XPATH, '//androidx.appcompat.widget.LinearLayoutCompat'),  # 确定（图片/AI拍照）

    # ================= 家用风新版UI：保存模板 =================
    "save_text": (AppiumBy.XPATH, '//android.widget.TextView[@text="保存"]'),             # 保存
    "saved_toast": (AppiumBy.XPATH, '//android.widget.TextView[@text="已保存，"]'),       # 已保存提示
    "template_spec_1": (AppiumBy.XPATH, '(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tv_template_specification"])[1]'),  # 模板规格1

    # ================= 家用风新版UI：打印 =================
    "print_text": (AppiumBy.XPATH, '//android.widget.TextView[@text="打印"]'),            # 打印
    "confirm_text": (AppiumBy.XPATH, '//android.widget.TextView[@text="确定"]'),          # 确定

    # ================= 家用风新版UI：商超耗材 =================
    "go_custom_label": (AppiumBy.XPATH, '//android.widget.TextView[@text="去自定义标签"]'),  # 去自定义标签
    "input_width": (AppiumBy.ID, "com.fhit.app_iprinter:id/inputWidthET"),               # 自定义宽度
    "input_height": (AppiumBy.ID, "com.fhit.app_iprinter:id/inputHeightET"),             # 自定义高度
    "input_gap": (AppiumBy.ID, "com.fhit.app_iprinter:id/inputGapET"),                   # 自定义间隙
    "confirm_tv": (AppiumBy.ID, "com.fhit.app_iprinter:id/confirmTV"),                   # 确定

    # ================= 家用风新版UI：商品编辑/新建 =================
    "et_edit_23": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="23"])'),  # 金额输入框(23)
    "et_edit_30": (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="30"]'),      # 金额输入框(30)
    "et_edit_3": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit"])[3]'),  # 第3个输入框
    "et_edit_1": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit"])[1]'),  # 第1个输入框
    "et_edit_Q密怀念": (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="Q密怀念"]'),  # 商品名输入框
    "et_edit_mcd": (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="麦兜星迷你乐趣蛋"]'),  # 商品名输入框2
    "add_commodity": (AppiumBy.ID, "com.fhit.app_iprinter:id/addCommodityIV"),           # 新建商品
    "name_et": (AppiumBy.ID, "com.fhit.app_iprinter:id/nameET"),                         # 品名
    "barcode_et": (AppiumBy.ID, "com.fhit.app_iprinter:id/barcodeET"),                   # 条码
    "price_et": (AppiumBy.ID, "com.fhit.app_iprinter:id/priceET"),                       # 零售价
    "chose_file": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="android:id/title" and @text="商品测试数据.xlsx"]'),
    "device_num1": (AppiumBy.XPATH, f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number1}"]'),  # 第一台（官方耗材）
    "device_num2": (AppiumBy.XPATH, f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number2}"]'),  # 第二台（自定义耗材）
    "device_num3": (AppiumBy.XPATH, f'//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/adapter_find_device_mac" and @text="{device_number3}"]'),  # 第三台（商超耗材）


    # ============ 自动抓取（真实控件树 dump，可整段删除） ============
    # 由 tools/gen_locators.py 从 logs/ui_dump/*.xml 生成；
    # 条目名按「控件 id 转下划线」命名，页面归属见行尾注释。

    # ---------- 首页 ----------
    "cl_arrow": (AppiumBy.ID, "com.fhit.app_iprinter:id/clArrow"),  # 首页
    "cl_connect_device": (AppiumBy.ID, "com.fhit.app_iprinter:id/clConnectDevice"),  # 首页
    "iv_arrow": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivArrow"),  # 首页
    "iv_card_device": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCardDevice"),  # 首页
    "iv_customer_service": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCustomerService"),  # 首页
    "iv_device": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivDevice"),  # 首页
    "iv_home_course": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHomeCourse"),  # 首页
    "iv_template_style": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivTemplateStyle"),  # 首页
    "ll_my_save": (AppiumBy.ID, "com.fhit.app_iprinter:id/llMySave"),  # 首页
    "ll_recently_printed": (AppiumBy.ID, "com.fhit.app_iprinter:id/llRecentlyPrinted"),  # 首页
    "ll_usage_scenario": (AppiumBy.ID, "com.fhit.app_iprinter:id/llUsageScenario"),  # 首页
    "text_定制耗材": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"定制耗材\"]"),  # 首页 | 定制耗材
    "text_热敏类": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"热敏类\"]"),  # 首页_定制耗材 | 热敏类
    "text_热转印类": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"热转印类\"]"),  # 首页_定制耗材 | 热转印类
    "text_线缆编辑": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"线缆编辑\"]"),  # 首页 | 线缆编辑
    "text_联系我们": (AppiumBy.XPATH, "//android.widget.Button[@text=\" 联系我们\"]"),  # 首页_定制耗材 |  联系我们
    "text_选择定制的类型": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"选择定制的类型\"]"),  # 首页_定制耗材 | 选择定制的类型
    "tv_connect_device_name1": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConnectDeviceName1"),  # 首页 | 连接设备
    "tv_connect_status": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConnectStatus"),  # 首页
    "tv_customer_service": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvCustomerService"),  # 首页 | 客服
    "tv_home_course": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvHomeCourse"),  # 首页 | 教程
    "tv_usage_scenario": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvUsageScenario"),  # 首页 | 行业模板
    "v_device": (AppiumBy.ID, "com.fhit.app_iprinter:id/vDevice"),  # 首页
    "v_my_save_tab_bg": (AppiumBy.ID, "com.fhit.app_iprinter:id/vMySaveTabBg"),  # 首页
    "v_recently_printed_def_bg": (AppiumBy.ID, "com.fhit.app_iprinter:id/vRecentlyPrintedDefBg"),  # 首页
    "v_sel_usage_scenario": (AppiumBy.ID, "com.fhit.app_iprinter:id/vSelUsageScenario"),  # 首页
    "v_usage_scenario_def_bg": (AppiumBy.ID, "com.fhit.app_iprinter:id/vUsageScenarioDefBg"),  # 首页

    # ---------- 我的 ----------
    "activity_my_device_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_my_device_back"),  # 我的_我的设备
    "adapter_find_device_connect": (AppiumBy.ID, "com.fhit.app_iprinter:id/adapter_find_device_connect"),  # 我的_连接设备 | 连接
    "adapter_find_device_mac_p0014_a2026115804": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/adapter_find_device_mac\" and @text=\"P0014A2026115804\"]"),  # 我的_连接设备 | P0014A2026115804
    "adapter_find_device_mac_p0014_a2026115805": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/adapter_find_device_mac\" and @text=\"P0014A2026115805\"]"),  # 我的_连接设备 | P0014A2026115805
    "adapter_find_device_type_mp50_pro": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/adapter_find_device_type\" and @text=\"MP50 Pro\"]"),  # 我的_连接设备 | MP50 Pro
    "adapter_find_device_type_p76_l": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/adapter_find_device_type\" and @text=\"P76L\"]"),  # 我的_连接设备 | P76L
    "adapter_find_device_type_tp76i": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/adapter_find_device_type\" and @text=\"TP76i\"]"),  # 我的_连接设备 | TP76i
    "back_iv": (AppiumBy.ID, "com.fhit.app_iprinter:id/backIV"),  # 新版功能_我的商品
    "btn_copy_app_info": (AppiumBy.ID, "com.fhit.app_iprinter:id/btnCopyAppInfo"),  # 我的_应用信息 | 复制
    "btn_return_old_version": (AppiumBy.ID, "com.fhit.app_iprinter:id/btnReturnOldVersion"),  # 我的_进入新版/新版_首页 | 返回旧版
    "btn_scan_connect": (AppiumBy.ID, "com.fhit.app_iprinter:id/btnScanConnect"),  # 我的_连接设备 | 扫码连接设备
    "cl_bottom_tab": (AppiumBy.ID, "com.fhit.app_iprinter:id/clBottomTab"),  # 我的_进入新版/新版_首页
    "cl_go_to_edit": (AppiumBy.ID, "com.fhit.app_iprinter:id/clGoToEdit"),  # 我的_进入新版/新版_首页
    "empty_image": (AppiumBy.ID, "com.fhit.app_iprinter:id/emptyImage"),  # 我的_我的文件
    "htwi_home_create": (AppiumBy.ID, "com.fhit.app_iprinter:id/htwiHomeCreate"),  # 我的/首页
    "htwi_home_page": (AppiumBy.ID, "com.fhit.app_iprinter:id/htwiHomePage"),  # 我的/首页
    "import_word_tv": (AppiumBy.ID, "com.fhit.app_iprinter:id/importWordTV"),  # 我的_我的文件 | 上传文件
    "iv_connect_device": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivConnectDevice"),  # 我的
    "iv_connect_state": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivConnectState"),  # 我的_进入新版/新版_首页
    "iv_current_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCurrentLabel"),  # 我的_进入新版/新版_首页
    "iv_custom_action_bar_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCustomActionBarLeft"),  # 我的_我的文件/我的_连接设备
    "iv_custom_action_bar_right_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCustomActionBarRightTitle"),  # 我的_我的文件 | 上传要求
    "iv_custom_action_bar_right_two": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCustomActionBarRightTwo"),  # 我的_我的文件/我的_连接设备
    "iv_customized_consumables_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCustomizedConsumablesIcon"),  # 我的_进入新版/新版_首页
    "iv_device_img": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivDeviceImg"),  # 我的_连接设备
    "iv_empty": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEmpty"),  # 我的_我的设备
    "iv_home_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHomeIcon"),  # 我的_进入新版/新版_首页
    "iv_mine_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivMineIcon"),  # 我的_进入新版/新版_首页
    "iv_my_activity_app_info_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivMyActivityAppInfoBack"),  # 我的_应用信息
    "iv_permission_guide": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPermissionGuide"),  # 我的_连接设备
    "iv_personal_pictures": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPersonalPictures"),  # 我的
    "ll_connect_state": (AppiumBy.ID, "com.fhit.app_iprinter:id/llConnectState"),  # 我的_进入新版/新版_首页
    "ll_current_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/llCurrentLabel"),  # 我的_进入新版/新版_首页
    "ll_customized_consumables": (AppiumBy.ID, "com.fhit.app_iprinter:id/llCustomizedConsumables"),  # 我的_进入新版/新版_首页
    "ll_goto_new_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/llGotoNewLabel"),  # 我的_进入新版/新版_首页
    "ll_home_page": (AppiumBy.ID, "com.fhit.app_iprinter:id/llHomePage"),  # 我的_进入新版/新版_首页
    "ll_mine": (AppiumBy.ID, "com.fhit.app_iprinter:id/llMine"),  # 我的_进入新版/新版_首页
    "ll_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/llRight"),  # 我的_我的文件/我的_连接设备
    "ll_serve": (AppiumBy.ID, "com.fhit.app_iprinter:id/llServe"),  # 我的_进入新版/新版_首页
    "ll_tutorial": (AppiumBy.ID, "com.fhit.app_iprinter:id/llTutorial"),  # 我的_进入新版/新版_首页
    "rl_about_supvan": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlAboutSupvan"),  # 我的
    "rl_app_info": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlAppInfo"),  # 我的
    "rl_clear_data": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlClearData"),  # 我的
    "rl_connect_customer_service": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlConnectCustomerService"),  # 我的
    "rl_connect_device": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlConnectDevice"),  # 我的
    "rl_custom_action_bar_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlCustomActionBarLeft"),  # 我的_我的文件/我的_连接设备
    "rl_government_we_chat": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlGovernmentWeChat"),  # 我的
    "rl_language": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlLanguage"),  # 我的
    "rl_my_device": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlMyDevice"),  # 我的
    "rl_my_file": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlMyFile"),  # 我的
    "rl_my_saved": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlMySaved"),  # 我的_进入新版/新版_首页
    "rl_new_version": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlNewVersion"),  # 我的
    "rl_recently_printed": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlRecentlyPrinted"),  # 我的_进入新版/新版_首页
    "rl_software_share": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlSoftwareShare"),  # 我的
    "scan_icon_iv": (AppiumBy.ID, "com.fhit.app_iprinter:id/scanIconIV"),  # 新版功能_我的商品
    "search_et": (AppiumBy.ID, "com.fhit.app_iprinter:id/searchET"),  # 新版功能_我的商品 | 请输入条形码、名称
    "search_icon_iv": (AppiumBy.ID, "com.fhit.app_iprinter:id/searchIconIV"),  # 新版功能_我的商品
    "text_不使用此标签_去更换": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"不使用此标签，去更换\"]"),  # 我的_进入新版/新版_首页 | 不使用此标签，去更换
    "text_关于硕方": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"关于硕方\"]"),  # 我的 | 关于硕方
    "text_商品列表": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"商品列表\"]"),  # 新版功能_我的商品 | 商品列表
    "text_多语言": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"多语言\"]"),  # 我的 | 多语言
    "text_官方微信": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"官方微信\"]"),  # 我的 | 官方微信
    "text_应用信息": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"应用信息\"]"),  # 我的/我的_应用信息 | 应用信息
    "text_我的": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"我的\"]"),  # 我的 | 我的
    "text_我的文件": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"我的文件\"]"),  # 我的 | 我的文件
    "text_我的设备": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"我的设备\"]"),  # 我的/我的_我的设备 | 我的设备
    "text_教程": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"教程\"]"),  # 我的_进入新版/新版_首页 | 教程
    "text_暂无内容": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"暂无内容\"]"),  # 我的_进入新版/新版_首页 | 暂无内容
    "text_暂无数据": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"暂无数据\"]"),  # 我的_我的文件 | 暂无数据
    "text_服务": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"服务\"]"),  # 我的_进入新版/新版_首页 | 服务
    "text_清空缓存": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"清空缓存\"]"),  # 我的 | 清空缓存
    "text_联系客服": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"联系客服\"]"),  # 我的 | 联系客服
    "text_软件分享": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"软件分享\"]"),  # 我的 | 软件分享
    "tv_android_version_number": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAndroidVersionNumber"),  # 我的_应用信息
    "tv_app_name": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAppName"),  # 我的_进入新版/新版_首页 | 硕方打印
    "tv_build_number": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvBuildNumber"),  # 我的_应用信息
    "tv_connect_device_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConnectDeviceTitle"),  # 我的 | 连接设备
    "tv_connect_state": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConnectState"),  # 我的_进入新版/新版_首页 | 未连接
    "tv_consumable_id": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConsumableID"),  # 我的_应用信息 | T56016
    "tv_custom_action_bar_center_title_定制耗材": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvCustomActionBarCenterTitle\" and @text=\"定制耗材\"]"),  # 我的_我的文件/我的_连接设备 | 定制耗材
    "tv_custom_action_bar_center_title_我的文件": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvCustomActionBarCenterTitle\" and @text=\"我的文件\"]"),  # 我的_我的文件/我的_连接设备 | 我的文件
    "tv_custom_action_bar_center_title_查找设备": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvCustomActionBarCenterTitle\" and @text=\"查找设备\"]"),  # 我的_我的文件/我的_连接设备 | 查找设备
    "tv_customized_consumables_text": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvCustomizedConsumablesText"),  # 我的_进入新版/新版_首页 | 定制耗材
    "tv_empty": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvEmpty"),  # 我的_我的设备 | 您还没有连接设备
    "tv_home_text": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvHomeText"),  # 我的_进入新版/新版_首页 | 首页
    "tv_label_name": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvLabelName"),  # 我的_进入新版/新版_首页
    "tv_mine_text": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMineText"),  # 我的_进入新版/新版_首页 | 我的
    "tv_mobile_phone_type": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMobilePhoneType"),  # 我的_应用信息 | 23127PN0CC
    "tv_mobile_system_version_number": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMobileSystemVersionNumber"),  # 我的_应用信息 | MIUI:V816
    "tv_my_saved": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMySaved"),  # 我的_进入新版/新版_首页 | 我的模板
    "tv_open_bluetooth": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvOpenBluetooth"),  # 我的_连接设备 | 请打开手机蓝牙和定位权限
    "tv_personal_telephone": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvPersonalTelephone"),  # 我的 | 177****6604
    "tv_recently_printed": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRecentlyPrinted"),  # 我的_进入新版/新版_首页 | 最近打印
    "tv_software_version_number": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSoftwareVersionNumber"),  # 我的_应用信息
    "tv_use_label_info": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvUseLabelInfo"),  # 我的_进入新版/新版_首页 | 上次使用的标签
    "tv_user_login_phone_number": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvUserLoginPhoneNumber"),  # 我的_应用信息

    # ---------- 新建标签/耗材选择 ----------
    "cb_show_dialog": (AppiumBy.ID, "com.fhit.app_iprinter:id/cbShowDialog"),  # 新建标签_入口/新建标签_弹窗
    "cl_last_use_template": (AppiumBy.ID, "com.fhit.app_iprinter:id/clLastUseTemplate"),  # 新建标签_入口/新建标签_弹窗
    "cl_last_use_template_image": (AppiumBy.ID, "com.fhit.app_iprinter:id/clLastUseTemplateImage"),  # 新建标签_入口/新建标签_弹窗
    "iv_enter": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEnter"),  # 新建标签_入口/新建标签_弹窗
    "iv_template_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivTemplateIcon"),  # 新建标签_入口/新建标签_弹窗
    "iv_template_image": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivTemplateImage"),  # 新建标签_入口/新建标签_弹窗
    "ll_connect_device_and_create": (AppiumBy.ID, "com.fhit.app_iprinter:id/llConnectDeviceAndCreate"),  # 新建标签_入口/新建标签_弹窗
    "ll_use_label_and_create": (AppiumBy.ID, "com.fhit.app_iprinter:id/llUseLabelAndCreate"),  # 新建标签_入口/新建标签_弹窗
    "text_连接设备": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"连接设备\"]"),  # 新建标签_入口/新建标签_弹窗 | 连接设备
    "tv_last_use": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvLastUse"),  # 新建标签_入口/新建标签_弹窗 | 上次使用
    "tv_no_more_show": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvNoMoreShow"),  # 新建标签_入口/新建标签_弹窗 | 不再出现此弹窗
    "tv_replace": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvReplace"),  # 新建标签_入口/新建标签_弹窗 | 更换
    "tv_template_name": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTemplateName"),  # 新建标签_入口/新建标签_弹窗
    "tv_use_label_and_create": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvUseLabelAndCreate"),  # 新建标签_入口/新建标签_弹窗 | 以此标签纸新建

    # ---------- 编辑页与功能栏 ----------
    "activity_logo_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_logo_back"),  # 功能_logo
    "activity_scan_area": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_scan_area"),  # 功能_扫码打印/新版功能_扫描商品条码
    "activity_scan_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_scan_back"),  # 功能_扫码打印/新版功能_扫描商品条码
    "activity_scan_flashlight": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_scan_flashlight"),  # 功能_扫码打印/新版功能_扫描商品条码
    "activity_scan_hint": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_scan_hint"),  # 功能_扫码打印/新版功能_扫描商品条码
    "activity_scan_line": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_scan_line"),  # 功能_扫码打印/新版功能_扫描商品条码
    "activity_scan_photo": (AppiumBy.ID, "com.fhit.app_iprinter:id/activity_scan_photo"),  # 功能_扫码打印/新版功能_扫描商品条码
    "align_upper_lower_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/AlignUpperLowerRight"),  # 功能_线缆标签 | Ɐ
    "bt_preview_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/bt_preview_add"),  # 新版功能_新增标签 | 新增
    "bt_preview_copy": (AppiumBy.ID, "com.fhit.app_iprinter:id/bt_preview_copy"),  # 新版功能_新增标签 | 复制
    "bt_preview_delete": (AppiumBy.ID, "com.fhit.app_iprinter:id/bt_preview_delete"),  # 新版功能_新增标签 | 删除
    "btn_free_trial": (AppiumBy.ID, "com.fhit.app_iprinter:id/btnFreeTrial"),  # 功能_识别 | 立即试用
    "cl_base": (AppiumBy.ID, "com.fhit.app_iprinter:id/clBase"),  # 功能_边框
    "cl_control": (AppiumBy.ID, "com.fhit.app_iprinter:id/clControl"),  # 功能_反色/功能_表格
    "cl_edit": (AppiumBy.ID, "com.fhit.app_iprinter:id/clEdit"),  # 新版_编辑页/新版功能_新增标签
    "cl_effect": (AppiumBy.ID, "com.fhit.app_iprinter:id/clEffect"),  # 功能_线缆标签
    "cl_file_import": (AppiumBy.ID, "com.fhit.app_iprinter:id/clFileImport"),  # 功能_一维码/功能_二维码
    "cl_font": (AppiumBy.ID, "com.fhit.app_iprinter:id/clFont"),  # 功能_文本/文本_输入弹窗
    "cl_format": (AppiumBy.ID, "com.fhit.app_iprinter:id/clFormat"),  # 功能_序号/功能_日期
    "cl_impl": (AppiumBy.ID, "com.fhit.app_iprinter:id/clImpl"),  # 功能_文本/文本_输入弹窗
    "cl_interesting": (AppiumBy.ID, "com.fhit.app_iprinter:id/clInteresting"),  # 功能_边框
    "cl_keyboard": (AppiumBy.ID, "com.fhit.app_iprinter:id/clKeyboard"),  # 功能_文本/文本_输入弹窗
    "cl_preview": (AppiumBy.ID, "com.fhit.app_iprinter:id/cl_preview"),  # 新版功能_新增标签
    "cl_segment": (AppiumBy.ID, "com.fhit.app_iprinter:id/clSegment"),  # 新版功能_新增标签/预览
    "cl_setting": (AppiumBy.ID, "com.fhit.app_iprinter:id/clSetting"),  # 功能_一维码/功能_二维码
    "cl_style": (AppiumBy.ID, "com.fhit.app_iprinter:id/clStyle"),  # 功能_序号/功能_日期
    "cl_typeface": (AppiumBy.ID, "com.fhit.app_iprinter:id/clTypeface"),  # 功能_文本/文本_输入弹窗
    "cl_wire": (AppiumBy.ID, "com.fhit.app_iprinter:id/clWire"),  # 功能_边框
    "dialog_terminal_block_content": (AppiumBy.ID, "com.fhit.app_iprinter:id/dialog_terminal_block_content"),  # 功能_端子_端口
    "dialog_terminal_block_set_up": (AppiumBy.ID, "com.fhit.app_iprinter:id/dialog_terminal_block_set_up"),  # 功能_端子_端口
    "dialog_terminal_block_text_style": (AppiumBy.ID, "com.fhit.app_iprinter:id/dialog_terminal_block_text_style"),  # 功能_端子_端口
    "dialog_terminal_block_typeface": (AppiumBy.ID, "com.fhit.app_iprinter:id/dialog_terminal_block_typeface"),  # 功能_端子_端口
    "et_edit_10g_20袋_包": (AppiumBy.XPATH, "//android.widget.EditText[@resource-id=\"com.fhit.app_iprinter:id/etEdit\" and @text=\"10g*20袋/包\"]"),  # 新版_编辑页/新版功能_新增标签 | 10g*20袋/包
    "et_edit_999板蓝根颗粒": (AppiumBy.XPATH, "//android.widget.EditText[@resource-id=\"com.fhit.app_iprinter:id/etEdit\" and @text=\"999板蓝根颗粒\"]"),  # 新版_编辑页/新版功能_新增标签 | 999板蓝根颗粒
    "et_edit_山东": (AppiumBy.XPATH, "//android.widget.EditText[@resource-id=\"com.fhit.app_iprinter:id/etEdit\" and @text=\"山东\"]"),  # 新版_编辑页/新版功能_新增标签 | 山东
    "et_edit_清热解毒": (AppiumBy.XPATH, "//android.widget.EditText[@resource-id=\"com.fhit.app_iprinter:id/etEdit\" and @text=\"清热解毒\"]"),  # 新版_编辑页/新版功能_新增标签 | 清热解毒
    "et_edit_盒": (AppiumBy.XPATH, "//android.widget.EditText[@resource-id=\"com.fhit.app_iprinter:id/etEdit\" and @text=\"盒\"]"),  # 新版_编辑页/新版功能_新增标签 | 盒
    "et_frame_tip": (AppiumBy.ID, "com.fhit.app_iprinter:id/etFrame_tip"),  # 功能_端子_端口 | 范围:1-80
    "et_input_请输入13位数字": (AppiumBy.XPATH, "//android.widget.EditText[@resource-id=\"com.fhit.app_iprinter:id/etInput\" and @text=\"请输入13位数字\"]"),  # 功能_一维码/功能_二维码 | 请输入13位数字
    "et_input_请输入内容": (AppiumBy.XPATH, "//android.widget.EditText[@resource-id=\"com.fhit.app_iprinter:id/etInput\" and @text=\"请输入内容\"]"),  # 功能_一维码/功能_二维码 | 请输入内容
    "et_poundage_number": (AppiumBy.ID, "com.fhit.app_iprinter:id/etPoundageNumber"),  # 功能_形状
    "hti_copy": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiCopy"),  # 功能_表格/功能栏_第3页
    "hti_delete": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiDelete"),  # 功能_表格/功能栏_第3页
    "hti_multiple_choice": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiMultipleChoice"),  # 功能_表格/功能栏_第3页
    "hti_rotate": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiRotate"),  # 功能_表格/功能栏_第3页
    "hti_setting_redo": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiSettingRedo"),  # 功能_反色/功能_表格
    "hti_setting_rotate": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiSettingRotate"),  # 功能_反色/功能_表格
    "hti_setting_undo": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiSettingUndo"),  # 功能_反色/功能_表格
    "hti_zoom_out": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiZoomOut"),  # 功能_表格/功能栏_第3页
    "item_expandable_list_child_name_tv_友情链接": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_child_name_tv\" and @text=\"友情链接\"]"),  # 功能_logo | 友情链接
    "item_expandable_list_child_name_tv_客户logo": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_child_name_tv\" and @text=\"客户LOGO\"]"),  # 功能_logo | 客户LOGO
    "item_expandable_list_child_name_tv_警示标识": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_child_name_tv\" and @text=\"警示标识\"]"),  # 功能_logo | 警示标识
    "item_expandable_list_child_name_tv_通用标识": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_child_name_tv\" and @text=\"通用标识\"]"),  # 功能_logo | 通用标识
    "item_expandable_list_child_name_tv_通用箭头": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_child_name_tv\" and @text=\"通用箭头\"]"),  # 功能_logo | 通用箭头
    "item_expandable_list_group_indicator_iv": (AppiumBy.ID, "com.fhit.app_iprinter:id/item_expandable_list_group_indicator_iv"),  # 功能_logo
    "item_expandable_list_group_name_tv_商业零售": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"商业零售\"]"),  # 功能_logo | 商业零售
    "item_expandable_list_group_name_tv_有线": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"有线\"]"),  # 功能_logo | 有线
    "item_expandable_list_group_name_tv_物流": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"物流\"]"),  # 功能_logo | 物流
    "item_expandable_list_group_name_tv_电网": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"电网\"]"),  # 功能_logo | 电网
    "item_expandable_list_group_name_tv_石油": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"石油\"]"),  # 功能_logo | 石油
    "item_expandable_list_group_name_tv_运营商": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"运营商\"]"),  # 功能_logo | 运营商
    "item_expandable_list_group_name_tv_通用": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"通用\"]"),  # 功能_logo | 通用
    "item_expandable_list_group_name_tv_银行": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/item_expandable_list_group_name_tv\" and @text=\"银行\"]"),  # 功能_logo | 银行
    "iv_ai_over_lay": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivAIOverLay"),  # 功能栏_第2页/功能栏_第3页
    "iv_border": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivBorder"),  # 功能_边框
    "iv_character_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCharacterAdd"),  # 功能_一维码
    "iv_character_subtract": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCharacterSubtract"),  # 功能_一维码
    "iv_clear_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivClearLabel"),  # 功能_反色/功能_表格
    "iv_edit_feedback": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEditFeedback"),  # 功能_反色/功能_表格
    "iv_edit_left_select": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEditLeftSelect"),  # 功能_表格/功能栏_第3页
    "iv_edit_right_select": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEditRightSelect"),  # 功能_表格/功能栏_第3页
    "iv_editable_del": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEditableDel"),  # 功能_更多/功能_更多_Tablogo
    "iv_empty_course": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEmptyCourse"),  # 功能_Excel/功能_PDF
    "iv_frame_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFrameAdd"),  # 功能_端子_端口
    "iv_frame_reduce": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFrameReduce"),  # 功能_端子_端口
    "iv_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivIcon"),  # 功能_反色/功能_表格
    "iv_input_expand_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivInputExpandIcon"),  # 功能_文本/文本_输入弹窗
    "iv_kata_my_object_setting": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivKataMyObjectSetting"),  # 功能_反色/功能_表格
    "iv_line": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivLine"),  # 功能_端子_端口
    "iv_line_circle": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivLineCircle"),  # 功能_端子_端口
    "iv_line_width_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivLineWidthAdd"),  # 功能_形状
    "iv_line_width_sub": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivLineWidthSub"),  # 功能_形状
    "iv_preview": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPreview"),  # 功能_反色/功能_表格
    "iv_real_time_tip": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivRealTimeTip"),  # 功能_日期
    "iv_scan_discern": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_scan_discern"),  # 功能_识别
    "iv_segment": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivSegment"),  # 新版功能_新增标签/预览
    "iv_service": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_service"),  # 新版_编辑页/新版功能_新增标签
    "iv_shape": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivShape"),  # 功能_形状
    "iv_svg_symbol": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivSvgSymbol"),  # 功能_符号
    "iv_symbol_search": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivSymbolSearch"),  # 功能_符号
    "iv_tab_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivTabIcon"),  # 功能_更多/功能_更多_Tablogo
    "iv_text_discern": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_text_discern"),  # 功能_识别
    "iv_width_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivWidthAdd"),  # 功能_形状
    "iv_width_sub": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivWidthSub"),  # 功能_形状
    "label_ean_13": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/label\" and @text=\"EAN-13\"]"),  # 功能_一维码/功能_二维码 | EAN-13
    "label_qr_code": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/label\" and @text=\"QR-CODE\"]"),  # 功能_一维码/功能_二维码 | QR-CODE
    "left_mask": (AppiumBy.ID, "com.fhit.app_iprinter:id/left_mask"),  # 功能_扫码打印/新版功能_扫描商品条码
    "ll_activity_home_style_edit_template_edit_list": (AppiumBy.ID, "com.fhit.app_iprinter:id/llActivityHomeStyleEditTemplateEditList"),  # 新版_编辑页/新版功能_新增标签
    "ll_align_upper_lower_center": (AppiumBy.ID, "com.fhit.app_iprinter:id/llAlignUpperLowerCenter"),  # 功能_线缆标签
    "ll_align_upper_lower_center_rotate": (AppiumBy.ID, "com.fhit.app_iprinter:id/llAlignUpperLowerCenterRotate"),  # 功能_线缆标签
    "ll_align_upper_lower_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/llAlignUpperLowerLeft"),  # 功能_线缆标签
    "ll_align_upper_lower_left_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/llAlignUpperLowerLeftRight"),  # 功能_线缆标签
    "ll_both_same": (AppiumBy.ID, "com.fhit.app_iprinter:id/llBothSame"),  # 功能_线缆标签
    "ll_date_format": (AppiumBy.ID, "com.fhit.app_iprinter:id/llDateFormat"),  # 功能_日期
    "ll_direction_h": (AppiumBy.ID, "com.fhit.app_iprinter:id/llDirectionH"),  # 功能_端子_端口
    "ll_direction_v": (AppiumBy.ID, "com.fhit.app_iprinter:id/llDirectionV"),  # 功能_端子_端口
    "ll_excel_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/llExcelBack"),  # 功能_Excel/功能_PDF
    "ll_folder": (AppiumBy.ID, "com.fhit.app_iprinter:id/llFolder"),  # 功能_Excel/功能_PDF
    "ll_fun_bar": (AppiumBy.ID, "com.fhit.app_iprinter:id/ll_fun_bar"),  # 新版_编辑页/新版功能_新增标签
    "ll_import_tutorial": (AppiumBy.ID, "com.fhit.app_iprinter:id/llImportTutorial"),  # 功能_Excel/功能_PDF
    "ll_kata_my_object_setting": (AppiumBy.ID, "com.fhit.app_iprinter:id/llKataMyObjectSetting"),  # 功能_反色/功能_表格
    "ll_material_info_container": (AppiumBy.ID, "com.fhit.app_iprinter:id/ll_material_info_container"),  # 新版_编辑页/新版功能_新增标签
    "ll_paint": (AppiumBy.ID, "com.fhit.app_iprinter:id/llPaint"),  # 功能_涂鸦
    "ll_qq_import": (AppiumBy.ID, "com.fhit.app_iprinter:id/llQQImport"),  # 功能_Excel/功能_PDF
    "ll_scan": (AppiumBy.ID, "com.fhit.app_iprinter:id/llScan"),  # 功能_一维码
    "ll_time_format": (AppiumBy.ID, "com.fhit.app_iprinter:id/llTimeFormat"),  # 功能_日期
    "ll_time_offset_data": (AppiumBy.ID, "com.fhit.app_iprinter:id/llTimeOffsetData"),  # 功能_日期
    "ll_time_prefix": (AppiumBy.ID, "com.fhit.app_iprinter:id/llTimePrefix"),  # 功能_日期
    "ll_wechat_import": (AppiumBy.ID, "com.fhit.app_iprinter:id/llWechatImport"),  # 功能_Excel/功能_PDF
    "m_hti_zoom_in": (AppiumBy.ID, "com.fhit.app_iprinter:id/mHtiZoomIn"),  # 功能_表格/功能栏_第3页
    "m_v_intercept": (AppiumBy.ID, "com.fhit.app_iprinter:id/mVIntercept"),  # 新版功能_新增标签/预览
    "my_activity_logo_tv": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_logo_tv"),  # 功能_logo | 相册
    "my_activity_main_lp_handle_iv": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_handle_iv"),  # 功能_反色/功能_表格
    "my_activity_main_lp_left_v": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_left_v"),  # 新版功能_新增标签/预览
    "my_activity_main_lp_paint_view_bg_v": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_paint_view_bg_v"),  # 功能_反色/功能_表格
    "my_activity_main_lp_pv_contain_ll": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_pv_contain_ll"),  # 功能_反色/功能_表格
    "my_activity_main_lp_title_tv": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_title_tv"),  # 功能_反色/功能_表格
    "my_activity_main_lp_total_page_tv": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_total_page_tv"),  # 新版功能_新增标签 | 标签/共2段
    "my_dialog_discern_iv_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_discern_iv_back"),  # 功能_识别
    "my_dialog_picture_cancel_tv": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_picture_cancel_tv"),  # 功能_图片 | 取消
    "my_dialog_picture_take_photos_tv": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_picture_take_photos_tv"),  # 功能_图片 | 拍照
    "my_dialog_scan_discern_cl": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_scan_discern_cl"),  # 功能_识别
    "my_dialog_sequence_produce_tv_end": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_tv_end"),  # 功能_序号 | 结束
    "my_dialog_sequence_produce_tv_interval": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_tv_interval"),  # 功能_序号 | 间隔
    "my_dialog_sequence_produce_tv_prefix": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_tv_prefix"),  # 功能_序号 | 前缀
    "my_dialog_sequence_produce_tv_start": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_tv_start"),  # 功能_序号 | 起始
    "my_dialog_sequence_produce_tv_style": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_tv_style"),  # 功能_序号 | 样式
    "my_dialog_sequence_produce_tv_suffix": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_sequence_produce_tv_suffix"),  # 功能_序号 | 后缀
    "my_dialog_text_discern_cl": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_text_discern_cl"),  # 功能_识别
    "my_item_symbol_tv_a": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/my_item_symbol_tv\" and @text=\"A\"]"),  # 功能_标识 | A
    "my_item_symbol_tv_b": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/my_item_symbol_tv\" and @text=\"B\"]"),  # 功能_标识 | B
    "my_item_symbol_tv_c": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/my_item_symbol_tv\" and @text=\"C\"]"),  # 功能_标识 | C
    "my_item_symbol_tv_d": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/my_item_symbol_tv\" and @text=\"D\"]"),  # 功能_标识 | D
    "npb_manual_first_folded_font_size": (AppiumBy.ID, "com.fhit.app_iprinter:id/npbManualFirstFoldedFontSize"),  # 功能_线缆标签
    "right_mask": (AppiumBy.ID, "com.fhit.app_iprinter:id/right_mask"),  # 功能_扫码打印/新版功能_扫描商品条码
    "rl_circle_interval_long": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlCircleIntervalLong"),  # 功能_形状
    "rl_edit_feedback": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlEditFeedback"),  # 功能_反色/功能_表格
    "rl_line_interval_long": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlLineIntervalLong"),  # 功能_形状
    "rl_line_long": (AppiumBy.ID, "com.fhit.app_iprinter:id/rlLineLong"),  # 功能_形状
    "s_choose_type": (AppiumBy.ID, "com.fhit.app_iprinter:id/sChooseType"),  # 功能_一维码/功能_二维码
    "seek_bar": (AppiumBy.ID, "com.fhit.app_iprinter:id/seekBar"),  # 功能_涂鸦
    "sp_import_type": (AppiumBy.ID, "com.fhit.app_iprinter:id/spImportType"),  # 功能_线缆标签
    "template_classify_name_excel": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"Excel\"]"),  # 功能_标识/功能_符号 | Excel
    "template_classify_name_pdf": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"PDF\"]"),  # 功能_标识/功能_符号 | PDF
    "template_classify_name_ttf": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"TTF\"]"),  # 功能_标识/功能_符号 | TTF
    "template_classify_name_办公室": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"办公室\"]"),  # 功能_标识/功能_符号 | 办公室
    "template_classify_name_勾选框": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"勾选框\"]"),  # 功能_标识/功能_符号 | 勾选框
    "template_classify_name_单位符号": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"单位符号\"]"),  # 功能_标识/功能_符号 | 单位符号
    "template_classify_name_售卖": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"售卖\"]"),  # 功能_标识/功能_符号 | 售卖
    "template_classify_name_城市地标": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"城市地标\"]"),  # 功能_标识/功能_符号 | 城市地标
    "template_classify_name_安全标志": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"安全标志\"]"),  # 功能_标识/功能_符号 | 安全标志
    "template_classify_name_所有": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"所有\"]"),  # 功能_标识/功能_符号 | 所有
    "template_classify_name_文档": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"文档\"]"),  # 功能_标识/功能_符号 | 文档
    "template_classify_name_电力通信": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"电力通信\"]"),  # 功能_标识/功能_符号 | 电力通信
    "template_classify_name_节日祝福": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"节日祝福\"]"),  # 功能_标识/功能_符号 | 节日祝福
    "template_classify_name_警示": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"警示\"]"),  # 功能_标识/功能_符号 | 警示
    "template_classify_name_运输": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/templateClassifyName\" and @text=\"运输\"]"),  # 功能_标识/功能_符号 | 运输
    "text_1_9": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"(1-9)\"]"),  # 功能_序号 | (1-9)
    "text_logo": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"logo\"]"),  # 功能_logo | logo
    "text_qq上传": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"QQ上传\"]"),  # 功能_Excel/功能_PDF | QQ上传
    "text_两折不同": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"两折不同\"]"),  # 功能_线缆标签 | 两折不同
    "text_两折相同": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"两折相同\"]"),  # 功能_线缆标签 | 两折相同
    "text_保存成功": (AppiumBy.XPATH, "//android.widget.Toast[@text=\"保存成功\"]"),  # 功能栏_第3页 | 保存成功
    "text_分割线": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"分割线\"]"),  # 功能_端子_端口 | 分割线
    "text_导入教程": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"导入教程\"]"),  # 功能_Excel/功能_PDF | 导入教程
    "text_已新增一个标签": (AppiumBy.XPATH, "//android.widget.Toast[@text=\"已新增一个标签\"]"),  # 新版功能_新增标签 | 已新增一个标签
    "text_形状": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"形状\"]"),  # 功能_形状 | 形状
    "text_微信上传": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"微信上传\"]"),  # 功能_Excel/功能_PDF | 微信上传
    "text_扫一扫": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"扫一扫\"]"),  # 功能_识别/首页 | 扫一扫
    "text_文本": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"文本\"]"),  # 功能_识别 | 文本
    "text_横向": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"横向\"]"),  # 功能_端子_端口 | 横向
    "text_涂鸦": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"涂鸦\"]"),  # 功能_涂鸦 | 涂鸦
    "text_竖向": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"竖向\"]"),  # 功能_端子_端口 | 竖向
    "text_端子宽度a": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"端子宽度A\"]"),  # 功能_端子_端口 | 端子宽度A
    "text_端子宽度b": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"端子宽度B\"]"),  # 功能_端子_端口 | 端子宽度B
    "text_端子方向": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"端子方向\"]"),  # 功能_端子_端口 | 端子方向
    "text_端子格数": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"端子格数\"]"),  # 功能_端子_端口 | 端子格数
    "text_线型": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"线型\"]"),  # 功能_形状 | 线型
    "text_线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"线缆标签\"]"),  # 功能_线缆标签 | 线缆标签
    "text_绘制边框": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"绘制边框\"]"),  # 功能_端子_端口 | 绘制边框
    "text_编辑": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"编辑\"]"),  # 功能_更多/功能_更多_Tablogo | 编辑
    "text_设置": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"设置\"]"),  # 功能_端子_端口 | 设置
    "text_识别": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"识别\"]"),  # 功能_识别 | 识别
    "text_预览": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"预览\"]"),  # 新版_编辑页/新版功能_新增标签 | 预览
    "touch_outside": (AppiumBy.ID, "com.fhit.app_iprinter:id/touch_outside"),  # 功能_端子_端口
    "tv_add_association_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAddAssociationTitle"),  # 功能_日期 | 添加关联时间
    "tv_ai_photo_tip": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAIPhotoTip"),  # 功能_识别 | AI拍照识图上线了，立即体验吧！
    "tv_align_upper_lower_center_rotate_lower": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAlignUpperLowerCenterRotateLower"),  # 功能_线缆标签 | Ɐ
    "tv_align_upper_lower_center_rotate_upper": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAlignUpperLowerCenterRotateUpper"),  # 功能_线缆标签 | A
    "tv_align_upper_lower_left_lower": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAlignUpperLowerLeftLower"),  # 功能_线缆标签 | A
    "tv_align_upper_lower_left_upper": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAlignUpperLowerLeftUpper"),  # 功能_线缆标签 | A
    "tv_align_upper_lower_lower": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAlignUpperLowerLower"),  # 功能_线缆标签 | A
    "tv_align_upper_lower_upper": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAlignUpperLowerUpper"),  # 功能_线缆标签 | A
    "tv_application": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvApplication"),  # 功能_更多/功能_更多_Tablogo | 我的
    "tv_base": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvBase"),  # 功能_边框 | 基础边框
    "tv_brush": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvBrush"),  # 功能_涂鸦 | 画笔
    "tv_cancel_取消": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvCancel\" and @text=\"取消\"]"),  # 功能_更多/功能_更多_Tablogo | 取消
    "tv_cancel_另存为": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvCancel\" and @text=\"另存为\"]"),  # 功能_更多/功能_更多_Tablogo | 另存为
    "tv_chars_bold": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvCharsBold"),  # 功能_一维码 | 字符加粗
    "tv_chars_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvCharsTitle"),  # 功能_一维码 | 字符开关
    "tv_choose_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvChooseTitle"),  # 功能_一维码/功能_二维码 | 选择条码类型
    "tv_confirm_保存": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvConfirm\" and @text=\"保存\"]"),  # 功能_更多/功能_更多_Tablogo | 保存
    "tv_confirm_确定": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvConfirm\" and @text=\"确定\"]"),  # 功能_更多/功能_更多_Tablogo | 确定
    "tv_connect_status_2": (AppiumBy.ID, "com.fhit.app_iprinter:id/tv_connect_status"),  # 新版_编辑页/新版功能_新增标签 | 未连接
    "tv_date_format": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvDateFormat"),  # 功能_日期 | 2026年11月25日
    "tv_device_name_2": (AppiumBy.ID, "com.fhit.app_iprinter:id/tv_device_name"),  # 新版_编辑页/新版功能_新增标签 | T50/56 Pro
    "tv_edit": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvEdit"),  # 新版_编辑页/新版功能_新增标签
    "tv_file_import": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFileImport"),  # 功能_一维码/功能_二维码 | 文件导入
    "tv_font_size": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFontSize"),  # 功能_一维码 | 字符字号
    "tv_format": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFormat"),  # 功能_序号/功能_日期 | 格式
    "tv_height_tip": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvHeightTip"),  # 功能_端子_端口 | 范围:4-12
    "tv_impl": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvImpl"),  # 功能_文本/文本_输入弹窗 | 文件导入
    "tv_import_method": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvImportMethod"),  # 功能_线缆标签 | 导入方式
    "tv_import_tips": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvImportTips"),  # 功能_Excel/功能_PDF
    "tv_input": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvInput"),  # 功能_一维码/功能_二维码 | 输入内容
    "tv_input_expand_text": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvInputExpandText"),  # 功能_文本/文本_输入弹窗 | 展开
    "tv_interesting": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvInteresting"),  # 功能_边框 | 趣味边框
    "tv_kata_my_object_setting_pdf": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvKataMyObjectSetting\" and @text=\"PDF\"]"),  # 功能_反色/功能_表格 | PDF
    "tv_kata_my_object_setting_扫码打印": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvKataMyObjectSetting\" and @text=\"扫码打印\"]"),  # 功能_反色/功能_表格 | 扫码打印
    "tv_kata_my_object_setting_识别": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvKataMyObjectSetting\" and @text=\"识别\"]"),  # 功能_反色/功能_表格 | 识别
    "tv_line_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvLineTitle"),  # 功能_形状 | 线宽
    "tv_line_unit": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvLineUnit"),  # 功能_形状 | (单位: mm)
    "tv_manual_first_folded_content": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvManualFirstFoldedContent"),  # 功能_线缆标签 | 内容
    "tv_manual_first_folded_font_size": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvManualFirstFoldedFontSize"),  # 功能_线缆标签 | 字号
    "tv_material_info": (AppiumBy.ID, "com.fhit.app_iprinter:id/tv_material_info"),  # 新版_编辑页/新版功能_新增标签
    "tv_more_application": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMoreApplication"),  # 功能_更多/功能_更多_Tablogo | 更多
    "tv_none": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvNone"),  # 功能_边框 | 无
    "tv_number": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvNumber"),  # 新版功能_新增标签/预览
    "tv_presentation_effect": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvPresentationEffect"),  # 功能_线缆标签 | 展示效果
    "tv_print": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvPrint"),  # 功能_反色/功能_表格 | 打印
    "tv_real_time_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRealTimeTitle"),  # 功能_日期 | 实时时间
    "tv_select_material": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSelectMaterial"),  # 功能_反色/功能_表格 | 耗材
    "tv_select_template": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSelectTemplate"),  # 功能_反色/功能_表格 | 模板
    "tv_setting": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSetting"),  # 功能_一维码/功能_二维码 | 设置
    "tv_style_样式": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvStyle\" and @text=\"样式\"]"),  # 功能_序号/功能_日期 | 样式
    "tv_style_类型": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvStyle\" and @text=\"类型\"]"),  # 功能_序号/功能_日期 | 类型
    "tv_sweep": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSweep"),  # 功能_一维码/功能_二维码 | 扫一扫
    "tv_tab_title_excel": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"Excel\"]"),  # 功能_更多/功能_更多_Tablogo | Excel
    "tv_tab_title_pdf": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"PDF\"]"),  # 功能_更多/功能_更多_Tablogo | PDF
    "tv_tab_title_一维码": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"一维码\"]"),  # 功能_更多/功能_更多_Tablogo | 一维码
    "tv_tab_title_二维码": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"二维码\"]"),  # 功能_更多/功能_更多_Tablogo | 二维码
    "tv_tab_title_图片": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"图片\"]"),  # 功能_更多/功能_更多_Tablogo | 图片
    "tv_tab_title_形状": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"形状\"]"),  # 功能_更多/功能_更多_Tablogo | 形状
    "tv_tab_title_扫码打印": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"扫码打印\"]"),  # 功能_更多/功能_更多_Tablogo | 扫码打印
    "tv_tab_title_文本": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"文本\"]"),  # 功能_更多/功能_更多_Tablogo | 文本
    "tv_tab_title_线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTabTitle\" and @text=\"线缆标签\"]"),  # 功能_更多/功能_更多_Tablogo | 线缆标签
    "tv_template_save": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTemplateSave"),  # 功能_反色/功能_表格 | 保存
    "tv_text_删除": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvText\" and @text=\"删除\"]"),  # 功能_反色/功能_表格 | 删除
    "tv_text_恢复": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvText\" and @text=\"恢复\"]"),  # 功能_反色/功能_表格 | 恢复
    "tv_text_撤销": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvText\" and @text=\"撤销\"]"),  # 功能_反色/功能_表格 | 撤销
    "tv_text_新增": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvText\" and @text=\"新增\"]"),  # 功能_反色/功能_表格 | 新增
    "tv_text_新建标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvText\" and @text=\"新建标签\"]"),  # 功能_反色/功能_表格 | 新建标签
    "tv_text_进入多选": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvText\" and @text=\"进入多选\"]"),  # 功能_反色/功能_表格 | 进入多选
    "tv_text_重复": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvText\" and @text=\"重复\"]"),  # 功能_反色/功能_表格 | 重复
    "tv_time_format": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTimeFormat"),  # 功能_日期
    "tv_time_offset_add_or_subtract": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTimeOffsetAddOrSubtract"),  # 功能_日期 | +
    "tv_time_offset_clear": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTimeOffsetClear"),  # 功能_日期 | 清除
    "tv_time_offset_data": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTimeOffsetData"),  # 功能_日期 | 0天
    "tv_time_offset_switch_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTimeOffsetSwitchTitle"),  # 功能_日期 | 时间偏移
    "tv_time_prefix": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTimePrefix"),  # 功能_日期 | 无前缀
    "tv_title_一维码": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"一维码\"]"),  # 功能_Excel/功能_PDF | 一维码
    "tv_title_不浪费版线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"不浪费版线缆标签\"]"),  # 功能_Excel/功能_PDF | 不浪费版线缆标签
    "tv_title_二维码": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"二维码\"]"),  # 功能_Excel/功能_PDF | 二维码
    "tv_title_商业零售": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"商业零售\"]"),  # 功能_Excel/功能_PDF | 商业零售
    "tv_title_序号": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"序号\"]"),  # 功能_Excel/功能_PDF | 序号
    "tv_title_我的pdf文件": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"我的PDF文件\"]"),  # 功能_Excel/功能_PDF | 我的PDF文件
    "tv_title_我的文件": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"我的文件\"]"),  # 功能_Excel/功能_PDF | 我的文件
    "tv_title_打印设置": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"打印设置\"]"),  # 功能_Excel/功能_PDF | 打印设置
    "tv_title_新建标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"新建标签\"]"),  # 功能_Excel/功能_PDF | 新建标签
    "tv_title_日期": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"日期\"]"),  # 功能_Excel/功能_PDF | 日期
    "tv_title_服装标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"服装标签\"]"),  # 功能_Excel/功能_PDF | 服装标签
    "tv_title_模板名称": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"模板名称\"]"),  # 功能_Excel/功能_PDF | 模板名称
    "tv_title_珠宝标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvTitle\" and @text=\"珠宝标签\"]"),  # 功能_Excel/功能_PDF | 珠宝标签
    "tv_week_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvWeekTitle"),  # 功能_日期 | 星期
    "tv_width_tip": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvWidthTip"),  # 功能_端子_端口 | 范围:2-30
    "tv_width_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvWidthTitle"),  # 功能_形状 | 线长
    "tv_width_unit": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvWidthUnit"),  # 功能_形状 | (单位: mm)
    "v_back_click_area": (AppiumBy.ID, "com.fhit.app_iprinter:id/v_back_click_area"),  # 新版_编辑页/新版功能_新增标签
    "v_clear_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/vClearLabel"),  # 功能_反色/功能_表格
    "v_connect_area": (AppiumBy.ID, "com.fhit.app_iprinter:id/v_connect_area"),  # 新版_编辑页/新版功能_新增标签
    "v_dismiss": (AppiumBy.ID, "com.fhit.app_iprinter:id/vDismiss"),  # 功能_标识/功能_符号
    "v_input_expand": (AppiumBy.ID, "com.fhit.app_iprinter:id/vInputExpand"),  # 功能_文本/文本_输入弹窗
    "v_page_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/vPageBack"),  # 功能_反色/功能_表格
    "v_preview": (AppiumBy.ID, "com.fhit.app_iprinter:id/v_preview"),  # 新版_编辑页/新版功能_新增标签
    "v_print": (AppiumBy.ID, "com.fhit.app_iprinter:id/v_print"),  # 新版_编辑页/新版功能_新增标签
    "v_print_2": (AppiumBy.ID, "com.fhit.app_iprinter:id/vPrint"),  # 功能_反色/功能_表格
    "v_save": (AppiumBy.ID, "com.fhit.app_iprinter:id/v_save"),  # 新版_编辑页/新版功能_新增标签
    "v_select_material": (AppiumBy.ID, "com.fhit.app_iprinter:id/vSelectMaterial"),  # 功能_反色/功能_表格
    "v_select_template": (AppiumBy.ID, "com.fhit.app_iprinter:id/vSelectTemplate"),  # 功能_反色/功能_表格

    # ---------- 其他页面 ----------
    "bt_added": (AppiumBy.ID, "com.fhit.app_iprinter:id/btAdded"),  # 预览 | 新增
    "bt_copy": (AppiumBy.ID, "com.fhit.app_iprinter:id/btCopy"),  # 预览 | 复制
    "bt_delete": (AppiumBy.ID, "com.fhit.app_iprinter:id/btDelete"),  # 预览 | 删除
    "bt_start": (AppiumBy.ID, "com.fhit.app_iprinter:id/btStart"),  # 页面_耗材 | 启动
    "cl_control_obj_style": (AppiumBy.ID, "com.fhit.app_iprinter:id/clControlObjStyle"),  # 文本_对齐
    "cl_specification": (AppiumBy.ID, "com.fhit.app_iprinter:id/clSpecification"),  # 页面_模板/页面_模板_系统模板
    "cl_type": (AppiumBy.ID, "com.fhit.app_iprinter:id/clType"),  # 页面_模板/页面_模板_系统模板
    "cv_cancel": (AppiumBy.ID, "com.fhit.app_iprinter:id/cvCancel"),  # 当前屏/状态检查
    "et_paper_gap": (AppiumBy.ID, "com.fhit.app_iprinter:id/etPaperGap"),  # 页面_打印/页面_打印_打印设置
    "et_search": (AppiumBy.ID, "com.fhit.app_iprinter:id/etSearch"),  # 页面_耗材 | 请输入标签型号，快速进入编辑
    "et_search_text": (AppiumBy.ID, "com.fhit.app_iprinter:id/etSearchText"),  # 页面_模板/页面_模板_系统模板 | 输入模板名称/规格
    "iv_check": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCheck"),  # 页面_模板_行业模板
    "iv_clear": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivClear"),  # 当前屏/状态检查
    "iv_collate": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCollate"),  # 页面_打印/页面_打印_打印设置
    "iv_copies_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCopiesAdd"),  # 页面_打印/页面_打印_打印设置
    "iv_copies_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCopiesIcon"),  # 页面_打印/页面_打印_打印设置
    "iv_copies_reduce": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCopiesReduce"),  # 页面_打印/页面_打印_打印设置
    "iv_density": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivDensity"),  # 页面_打印/页面_打印_打印设置
    "iv_density_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivDensityAdd"),  # 页面_打印/页面_打印_打印设置
    "iv_density_sub": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivDensitySub"),  # 页面_打印/页面_打印_打印设置
    "iv_flip_minus": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFlipMinus"),  # 页面_打印/页面_打印_打印设置
    "iv_flip_way": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFlipWay"),  # 页面_打印/页面_打印_打印设置
    "iv_h_shift": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHShift"),  # 页面_打印/页面_打印_打印设置
    "iv_h_shift_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHShiftAdd"),  # 页面_打印/页面_打印_打印设置
    "iv_h_shift_sub": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHShiftSub"),  # 页面_打印/页面_打印_打印设置
    "iv_horizontal_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivHorizontalRight"),  # 文本_对齐
    "iv_paper_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPaperAdd"),  # 页面_耗材
    "iv_paper_gap": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPaperGap"),  # 页面_打印/页面_打印_打印设置
    "iv_paper_gap_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPaperGapAdd"),  # 页面_打印/页面_打印_打印设置
    "iv_paper_gap_subtract": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPaperGapSubtract"),  # 页面_打印/页面_打印_打印设置
    "iv_paper_type": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPaperType"),  # 页面_打印/页面_打印_打印设置
    "iv_paper_type_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPaperTypeAdd"),  # 页面_打印/页面_打印_打印设置
    "iv_paper_type_subtract": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPaperTypeSubtract"),  # 页面_打印/页面_打印_打印设置
    "iv_position_bottom": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPositionBottom"),  # 文本_对齐
    "iv_position_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPositionLeft"),  # 文本_对齐
    "iv_position_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPositionRight"),  # 文本_对齐
    "iv_position_top": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivPositionTop"),  # 文本_对齐
    "iv_range_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivRangeIcon"),  # 页面_打印/页面_打印_打印设置
    "iv_range_subtract": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivRangeSubtract"),  # 页面_打印/页面_打印_打印设置
    "iv_scan": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivScan"),  # 页面_耗材
    "iv_search": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivSearch"),  # 页面_耗材
    "iv_search_icon": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_search_icon"),  # 页面_模板/页面_模板_系统模板
    "iv_subtract": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivSubtract"),  # 页面_耗材
    "iv_template_image_2": (AppiumBy.ID, "com.fhit.app_iprinter:id/iv_template_image"),  # 页面_模板/页面_模板_系统模板
    "iv_v_shift": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivVShift"),  # 页面_打印/页面_打印_打印设置
    "iv_v_shift_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivVShiftAdd"),  # 页面_打印/页面_打印_打印设置
    "iv_v_shift_sub": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivVShiftSub"),  # 页面_打印/页面_打印_打印设置
    "iv_vertical_bottom": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivVerticalBottom"),  # 文本_对齐
    "ll_align_setting_bg": (AppiumBy.ID, "com.fhit.app_iprinter:id/llAlignSettingBg"),  # 文本_对齐
    "ll_root": (AppiumBy.ID, "com.fhit.app_iprinter:id/llRoot"),  # 当前屏/状态检查
    "ll_tab_personal": (AppiumBy.ID, "com.fhit.app_iprinter:id/llTabPersonal"),  # 页面_模板/页面_模板_系统模板
    "ll_tab_system": (AppiumBy.ID, "com.fhit.app_iprinter:id/llTabSystem"),  # 页面_模板/页面_模板_系统模板
    "m_tv_group_name_02_f线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"02F线缆标签\"]"),  # 页面_耗材 | 02F线缆标签
    "m_tv_group_name_03_f线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"03F线缆标签\"]"),  # 页面_耗材 | 03F线缆标签
    "m_tv_group_name_t型珠宝标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"T型珠宝标签\"]"),  # 页面_耗材 | T型珠宝标签
    "m_tv_group_name_t型线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"T型线缆标签\"]"),  # 页面_耗材 | T型线缆标签
    "m_tv_group_name_不浪费版线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"不浪费版线缆标签\"]"),  # 页面_耗材 | 不浪费版线缆标签
    "m_tv_group_name_医药价签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"医药价签\"]"),  # 页面_耗材 | 医药价签
    "m_tv_group_name_双排线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"双排线缆标签\"]"),  # 页面_耗材 | 双排线缆标签
    "m_tv_group_name_商超价签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"商超价签\"]"),  # 页面_耗材 | 商超价签
    "m_tv_group_name_平面标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"平面标签\"]"),  # 页面_耗材 | 平面标签
    "m_tv_group_name_当前耗材": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"当前耗材\"]"),  # 页面_耗材 | 当前耗材
    "m_tv_group_name_烟草价签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"烟草价签\"]"),  # 页面_耗材 | 烟草价签
    "m_tv_group_name_珠宝标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"珠宝标签\"]"),  # 页面_耗材 | 珠宝标签
    "m_tv_group_name_索引标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/mTvGroupName\" and @text=\"索引标签\"]"),  # 页面_耗材 | 索引标签
    "material_image": (AppiumBy.ID, "com.fhit.app_iprinter:id/materialImage"),  # 页面_耗材
    "my_activity_main_lp_drawer_cl": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_drawer_cl"),  # 预览
    "my_dialog_repetition_iv_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_repetition_iv_add"),  # 文本_重复份数
    "my_dialog_repetition_iv_cancel": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_repetition_iv_cancel"),  # 文本_重复份数
    "my_dialog_repetition_iv_subtract": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_dialog_repetition_iv_subtract"),  # 文本_重复份数
    "rb_align": (AppiumBy.ID, "com.fhit.app_iprinter:id/rbAlign"),  # 文本_对齐 | 对齐
    "rg_control_obj_style": (AppiumBy.ID, "com.fhit.app_iprinter:id/rgControlObjStyle"),  # 文本_对齐
    "s_collate": (AppiumBy.ID, "com.fhit.app_iprinter:id/sCollate"),  # 页面_打印/页面_打印_打印设置
    "text_取消": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"取消\"]"),  # 当前屏/状态检查 | 取消
    "text_当前标签重复次数": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"当前标签重复次数\"]"),  # 文本_重复份数 | 当前标签重复次数
    "text_打印垂直偏移": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"打印垂直偏移\"]"),  # 页面_打印/页面_打印_打印设置 | 打印垂直偏移
    "text_耗材": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"耗材\"]"),  # 页面_耗材 | 耗材
    "text_范围_1_100": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"范围：1–100\"]"),  # 文本_重复份数 | 范围：1–100
    "text_重复": (AppiumBy.XPATH, "//android.widget.TextView[@text=\"重复\"]"),  # 文本_重复份数 | 重复
    "tv_adaptive_consumables": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAdaptiveConsumables"),  # 页面_耗材 | 耗材校准
    "tv_all_num": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvAllNum"),  # 当前屏/状态检查
    "tv_copies_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvCopiesTitle"),  # 页面_打印/页面_打印_打印设置 | 打印份数
    "tv_density": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvDensity"),  # 页面_打印/页面_打印_打印设置 | 打印浓度
    "tv_divide": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvDivide"),  # 当前屏/状态检查
    "tv_flip": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFlip"),  # 页面_打印/页面_打印_打印设置 | 无
    "tv_flip_way_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFlipWayTitle"),  # 页面_打印/页面_打印_打印设置 | 翻转方式
    "tv_mat_class": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMatClass"),  # 页面_耗材 | 分类
    "tv_mat_class_value": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMatClassValue"),  # 页面_耗材 | 医药价签
    "tv_mat_type": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMatType"),  # 页面_耗材 | 型号
    "tv_mat_type_value": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMatTypeValue"),  # 页面_耗材
    "tv_material": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvMaterial"),  # 页面_耗材 | 间隙
    "tv_num": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvNum"),  # 当前屏/状态检查
    "tv_one_by_one_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvOneByOneTitle"),  # 页面_打印/页面_打印_打印设置 | 逐份打印
    "tv_paper_gap_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvPaperGapTitle"),  # 页面_打印/页面_打印_打印设置 | 间隙间隔
    "tv_paper_type_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvPaperTypeTitle"),  # 页面_打印/页面_打印_打印设置 | 耗材类型
    "tv_paper_type_耗材类型": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPaperType\" and @text=\"耗材类型\"]"),  # 页面_打印/页面_打印_打印设置 | 耗材类型
    "tv_paper_type_间隙": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPaperType\" and @text=\"间隙\"]"),  # 页面_打印/页面_打印_打印设置 | 间隙
    "tv_primary_name_不浪费版线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"不浪费版线缆标签\"]"),  # 页面_模板_行业模板 | 不浪费版线缆标签
    "tv_primary_name_全部": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"全部\"]"),  # 页面_模板_行业模板 | 全部
    "tv_primary_name_医药价签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"医药价签\"]"),  # 页面_模板_行业模板 | 医药价签
    "tv_primary_name_商业零售": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"商业零售\"]"),  # 页面_模板_行业模板 | 商业零售
    "tv_primary_name_商超价签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"商超价签\"]"),  # 页面_模板_行业模板 | 商超价签
    "tv_primary_name_服装标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"服装标签\"]"),  # 页面_模板_行业模板 | 服装标签
    "tv_primary_name_烟草价签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"烟草价签\"]"),  # 页面_模板_行业模板 | 烟草价签
    "tv_primary_name_物品标记": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"物品标记\"]"),  # 页面_模板_行业模板 | 物品标记
    "tv_primary_name_珠宝标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"珠宝标签\"]"),  # 页面_模板_行业模板 | 珠宝标签
    "tv_primary_name_线缆标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"线缆标签\"]"),  # 页面_模板_行业模板 | 线缆标签
    "tv_primary_name_食品标签": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tvPrimaryName\" and @text=\"食品标签\"]"),  # 页面_模板_行业模板 | 食品标签
    "tv_print_h_shift_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvPrintHShiftTitle"),  # 页面_打印/页面_打印_打印设置 | 打印水平偏移
    "tv_range": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRange"),  # 页面_打印/页面_打印_打印设置 | 全部页
    "tv_range_title": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRangeTitle"),  # 页面_打印/页面_打印_打印设置 | 打印范围
    "tv_rotate": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRotate"),  # 页面_耗材 | 旋转
    "tv_rotate_0": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRotate_0"),  # 页面_耗材 | 0°
    "tv_rotate_180": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRotate_180"),  # 页面_耗材 | 180°
    "tv_rotate_270": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRotate_270"),  # 页面_耗材 | 270°
    "tv_rotate_90": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvRotate_90"),  # 页面_耗材 | 90°
    "tv_search": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSearch"),  # 页面_耗材 | 搜索
    "tv_search_bt": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSearchBt"),  # 页面_模板/页面_模板_系统模板 | 搜索
    "tv_secondary_name": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSecondaryName"),  # 页面_模板_行业模板 | 全部行业模板
    "tv_specification": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvSpecification"),  # 页面_模板/页面_模板_系统模板 | 全部规格
    "tv_tab_personal": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTabPersonal"),  # 页面_模板/页面_模板_系统模板 | 我的模板
    "tv_tab_system": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTabSystem"),  # 页面_模板/页面_模板_系统模板 | 系统模板
    "tv_template_name_二手手机含内存": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_name\" and @text=\"二手手机含内存\"]"),  # 页面_模板/页面_模板_系统模板 | 二手手机含内存
    "tv_template_name_二手手机含表格": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_name\" and @text=\"二手手机含表格\"]"),  # 页面_模板/页面_模板_系统模板 | 二手手机含表格
    "tv_template_name_手机参数": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_name\" and @text=\"手机参数\"]"),  # 页面_模板/页面_模板_系统模板 | 手机参数
    "tv_template_name_手机参数含二维码": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_name\" and @text=\"手机参数含二维码\"]"),  # 页面_模板/页面_模板_系统模板 | 手机参数含二维码
    "tv_template_name_服装行业": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_name\" and @text=\"服装行业\"]"),  # 页面_模板/页面_模板_系统模板 | 服装行业
    "tv_template_specification_30mm_25mm_45mm": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_specification\" and @text=\"30mm*25mm+45mm\"]"),  # 页面_模板/页面_模板_系统模板 | 30mm*25mm+45mm
    "tv_template_specification_40mm_60mm": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_specification\" and @text=\"40mm*60mm\"]"),  # 页面_模板/页面_模板_系统模板 | 40mm*60mm
    "tv_template_specification_50mm_80mm": (AppiumBy.XPATH, "//android.widget.TextView[@resource-id=\"com.fhit.app_iprinter:id/tv_template_specification\" and @text=\"50mm*80mm\"]"),  # 页面_模板/页面_模板_系统模板 | 50mm*80mm
    "tv_total_page": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTotalPage"),  # 预览 | 标签/共1段
    "tv_type": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvType"),  # 页面_模板/页面_模板_系统模板 | 行业模板
    "view_bg": (AppiumBy.ID, "com.fhit.app_iprinter:id/view_bg"),  # 页面_模板_行业模板
}
