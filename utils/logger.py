# -*- coding: utf-8 -*-
"""
统一日志模块
============
在 conftest.py 顶部调用 setup_logger() 即可让整个项目用同一套日志。

特点：
  - 控制台实时输出（配合 pytest.ini 的 log_cli，或直接 print 风格查看）
  - 同时落盘到 logs/run.log（追加模式），事后可回溯
  - 自动给 selenium / appium 的噪音日志降级

用法：
    from utils.logger import setup_logger, get_logger
    setup_logger()
    logger = get_logger("element")
    logger.info("...")
"""
import logging
import os
import sys

# 项目根目录: utils/ 的上一级
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOG_DIR = os.path.join(_PROJECT_ROOT, "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "run.log")

_LOGGER_NAME = "supvan"
_configured = False


def _prepare_console_stream():
    """修复 Windows 控制台中文乱码（幂等，失败静默）。

    背景：直接 `sys.stdout.reconfigure(encoding="utf-8")` 会在 Windows 上把中文
    搞成 `鏃ュ織宸插垵濮嬪寲` 这种乱码 —— Python 改完编码后会绕过
    WriteConsoleW 直接写字节，而控制台仍按 GBK(936) 解析，两边编码对不上。

    策略：区分「真实控制台」和「被重定向 / 被 IDE 捕获」两种情况，分别处理。
    """
    stream = sys.stdout
    if stream is None:
        return

    try:
        is_tty = bool(stream.isatty())
    except Exception:
        is_tty = False

    # ① 非真实控制台（重定向到文件、管道、IDE 输出窗口）：
    #    保持它自身的编码不动，交给下游按同一套编码解析，避免再次错配；
    #    只把错误处理改成 replace，防止 emoji / 生僻字触发 UnicodeEncodeError。
    if not is_tty:
        try:
            # 注意：reconfigure 的参数是关键字专用的，不能按位置传
            stream.reconfigure(errors="replace")
        except Exception:
            pass
        return

    # ② 真实控制台：先把 Windows 代码页切到 UTF-8，再让 stdout 按 UTF-8 输出，
    #    这样「写出的字节」和「控制台的解析方式」才是一致的。
    if sys.platform == "win32":
        try:
            import ctypes

            k32 = ctypes.windll.kernel32
            k32.SetConsoleOutputCP(65001)   # 控制台输出代码页 -> UTF-8
            k32.SetConsoleCP(65001)         # 控制台输入代码页 -> UTF-8
        except Exception:
            pass

    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _under_pytest():
    """当前是否由 pytest 驱动（pytest 自带实时日志 handler，见 pytest.ini 的 log_cli）。"""
    return "pytest" in sys.modules or "_pytest" in sys.modules


def setup_logger(level=logging.INFO):
    """初始化全局日志（幂等，重复调用不会重复挂 handler）。"""
    global _configured

    logger = logging.getLogger(_LOGGER_NAME)
    if _configured:
        return logger

    os.makedirs(_LOG_DIR, exist_ok=True)

    # Windows 控制台中文乱码修复（真实控制台同步代码页，重定向场景保持原编码）
    _prepare_console_stream()

    logger.setLevel(level)

    # 关键：必须允许冒泡到 root。
    # pytest 的 log_cli 实时日志 handler 是挂在 root logger 上的，propagate=False
    # 会让 pytest.ini 里的 log_cli / log_cli_level 对项目日志完全失效。
    # （冒泡过程中只按「各级 handler 的 level」过滤，与 root logger 的 level 无关。）
    logger.propagate = True

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ① 控制台
    #    - 非 pytest（直接 python 跑脚本）：自己挂 handler 打印；
    #    - pytest 下：交给它的 log_cli，避免同一行日志被打印两次。
    if not _under_pytest():
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        console.setFormatter(fmt)
        logger.addHandler(console)

    # ② 文件（每次运行追加，保留历史）—— 无论谁驱动都要落盘
    file_handler = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    # ③ 降噪：第三方库只记 WARNING 以上
    for noisy in ("selenium", "urllib3", "appium"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True
    logger.info("日志已初始化 → %s", _LOG_FILE)
    return logger


def get_logger(name=None):
    """获取子 logger，例如 get_logger("element") -> supvan.element"""
    return logging.getLogger(f"{_LOGGER_NAME}.{name}" if name else _LOGGER_NAME)
