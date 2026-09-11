# -*- coding: utf-8 -*-
"""
元素定位统一管理文件
====================
本项目所有测试用例的元素定位（By 类型 + selector）集中在此处维护，
测试用例中通过语义化 key 引用，例如：

    wait_for_element(driver, *LOCATORS["add_label"]).click()

修改元素定位时，只需改这里，无需改动测试用例。
"""
from appium.webdriver.common.appiumby import AppiumBy


LOCATORS = {
    # ================= 通用 =================
    "create_new": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCreateNew"),            # 新建标签
    "add_label": (AppiumBy.ID, "com.fhit.app_iprinter:id/htiSettingLabelAdd"),     # 新增标签（标签+号）
    "input_edit": (AppiumBy.ID, "com.fhit.app_iprinter:id/etInput"),               # 内容输入框
    "confirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivConfirm"),                # 确定（文本编辑）
    "affirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivAffirm"),                  # 确定（条码/耗材等）
    "tv_confirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConfirm"),             # 确定（保存模板/打印）
    "cancel": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivCancel"),                  # 取消
    "view": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_paint_view"),  # 编辑区画布
    "enter_right": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_enter_right_iv"),  # 功能栏右翻
    "enter_left": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_enter_left_iv"),    # 功能栏左翻
    "go_connect": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvGoConnect"),           # 去连接
    "main_back_btn": (AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="com.fhit.app_iprinter:id/my_activity_main_lp_back_ll"]/android.widget.ImageView'),  # 主页返回
    "back_btn": (AppiumBy.XPATH, '//android.view.ViewGroup[@resource-id="com.fhit.app_iprinter:id/clPageTitle"]/android.widget.ImageView'),  # 页头返回

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
    "kata_text": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="文本"]'),      # 文本
    "kata_excel": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="Excel"]'),   # Excel
    "kata_more": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvKataMyObjectSetting" and @text="更多"]'),     # 更多

    "feature_反色": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="反色"]'),
    "feature_一维码": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="一维码"]'),
    "feature_二维码": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="二维码"]'),
    "feature_图片": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="图片"]'),
    "feature_Excel": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="Excel"]'),
    "feature_形状": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="形状"]'),
    "feature_线缆标签": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="线缆标签"]'),
    "feature_标识": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="标识"]'),
    "feature_边框": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="边框"]'),
    "feature_符号": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="符号"]'),
    "feature_logo": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="logo"]'),
    "feature_线": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="线"]'),
    "feature_涂鸦": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="涂鸦"]'),
    "feature_端子端口": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="端子/端口"]'),
    "feature_日期": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="日期"]'),
    "feature_表格": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="表格"]'),
    "feature_序号": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="序号"]'),

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

    # ================= 文本样式 =================
    "typeface": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvTypeface"),                  # 样式
    "layout_mode_switch": (AppiumBy.ID, "com.fhit.app_iprinter:id/sLayoutMode"),       # 自动换行开关
    "word_width_add": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivWordWidthAdd"),        # 字宽放大
    "text_direction_c": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivTextDirectionC"),    # 弧形文字方向
    "effect_italic": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEffectI"),              # 字效-倾斜
    "effect_underline": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivEffectU"),           # 字效-下划线
    "font_size_auto": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivFontSizeAuto"),        # 自动字号
    "font_space": (AppiumBy.ID, "com.fhit.app_iprinter:id/etFontSpace"),               # 字间距输入框
    "line_space": (AppiumBy.ID, "com.fhit.app_iprinter:id/etLineSpace"),               # 行间距输入框
    "font_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvFont"),                      # 字体
    "font_back": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_font_back"),      # 字体页返回
    "download_more_font": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvTextFont" and @text="下载更多"]'),  # 下载更多字体
    "font_download_item_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_item_font_adapter_download"])[1]'),  # 字体下载项1
    "font_download_item_2": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/my_item_font_adapter_download"])[2]'),  # 字体下载项2

    # ================= 重复份数 =================
    "repeat_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivRepeat"),                  # 重复份数入口
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
    "photo_check_1": (AppiumBy.XPATH, '(//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvCheck"])[1]'),  # 选中第1张
    "photo_complete": (AppiumBy.ID, "com.fhit.app_iprinter:id/ps_tv_complete"),        # 完成
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
    "interior_handle": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_interior_handle_iv"),  # 内页把手

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
    "paint_view": (AppiumBy.ID, "com.fhit.app_iprinter:id/my_activity_main_lp_paint_view"),  # 画布/编辑区

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
    "feature_文本": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/item_adapter_lp_custom_horizontal_scroll_view_tv" and @text="文本"]'),  # 文本（横向滚动）

    # ================= 家用风新版UI：首页/编辑 =================
    "enter_new_version": (AppiumBy.XPATH, '//android.widget.TextView[@text="进入新版"]'),  # 进入新版
    "my_tab": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/tvText" and @text="我的"]'),  # 我的tab（新版）
    "login_btn": (AppiumBy.ID, "com.fhit.app_iprinter:id/btnLogin"),                     # 去登录
    "connect_state": (AppiumBy.ID, "com.fhit.app_iprinter:id/tvConnectState"),           # 连接状态/切换机器
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

    # ================= 家用风新版UI：功能区入口（tvKataMyObjectSetting） =================
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

    # ================= 家用风新版UI：Excel/导入 =================
    "sim_affirm": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivSimAffirm"),                 # 确认生成Excel
    "documentsui_icon_thumb_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.android.documentsui:id/icon_thumb"])[1]'),  # 文件选择器第1项
    "select_iv_1": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[1]'),  # 商品选择1
    "select_iv_2": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[2]'),  # 商品选择2
    "select_iv_3": (AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.fhit.app_iprinter:id/selectIV"])[3]'),  # 商品选择3
    "next_page": (AppiumBy.ID, "com.fhit.app_iprinter:id/ivNextPage"),                   # 下一页

    # ================= 家用风新版UI：符号/边框/形状/涂鸦 =================
    "symbol_exclamation": (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.fhit.app_iprinter:id/my_item_symbol_tv" and @text="!"]'),  # 符号!
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
    "et_edit_199": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="1.99"])'),  # 金额输入框(1.99)
    "et_edit_30": (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="30"]'),      # 金额输入框(30)
    "et_edit_4": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit"])[4]'),  # 第4个输入框
    "et_edit_1": (AppiumBy.XPATH, '(//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit"])[1]'),  # 第1个输入框
    "et_edit_Q密怀念": (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="Q密怀念"]'),  # 商品名输入框
    "et_edit_mcd": (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.fhit.app_iprinter:id/etEdit" and @text="麦兜星迷你乐趣蛋"]'),  # 商品名输入框2
    "add_commodity": (AppiumBy.ID, "com.fhit.app_iprinter:id/addCommodityIV"),           # 新建商品
    "name_et": (AppiumBy.ID, "com.fhit.app_iprinter:id/nameET"),                         # 品名
    "barcode_et": (AppiumBy.ID, "com.fhit.app_iprinter:id/barcodeET"),                   # 条码
    "price_et": (AppiumBy.ID, "com.fhit.app_iprinter:id/priceET"),                       # 零售价
}
