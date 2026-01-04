import subprocess
import re
from typing import List, Dict


class DeviceDetector:
    @staticmethod
    def get_connected_devices() -> List[str]:
        """获取所有已连接设备的序列号（UDID）"""
        try:
            # 执行 adb devices 命令，获取连接的设备列表
            result = subprocess.check_output(
                ["adb", "devices"],
                stderr=subprocess.STDOUT,
                text=True
            )

            # 解析输出，提取设备序列号（排除标题行和离线设备）
            devices = []
            for line in result.splitlines():
                if "device" in line and not "List of devices" in line:
                    udid = line.split()[0].strip()
                    devices.append(udid)
            return devices
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ADB命令执行失败: {e.output}")
        except Exception as e:
            raise RuntimeError(f"获取设备列表失败: {str(e)}")

    @staticmethod
    def get_device_info(udid: str) -> Dict[str, str]:
        """获取指定设备的详细信息（系统版本、设备型号等）"""
        try:
            # 1. 获取系统版本（Android version）
            android_version = subprocess.check_output(
                ["adb", "-s", udid, "shell", "getprop", "ro.build.version.release"],
                stderr=subprocess.STDOUT,
                text=True
            ).strip()

            # 2. 获取设备型号（如 "MI 13"）
            device_model = subprocess.check_output(
                ["adb", "-s", udid, "shell", "getprop", "ro.product.model"],
                stderr=subprocess.STDOUT,
                text=True
            ).strip()

            # 3. 获取设备名称（可选，有些设备可能没有）
            device_name = subprocess.check_output(
                ["adb", "-s", udid, "shell", "getprop", "ro.product.name"],
                stderr=subprocess.STDOUT,
                text=True
            ).strip()

            # 4. 获取应用包名（如果需要固定测试某个APP）
            app_package = "com.fhit.app_iprinter"
            app_activity = ".ui.home.activity.HomeActivity"

            # 组装Appium所需的配置字典
            return {
                "udid": udid,  # 设备唯一标识（必须）
                "platformName": "Android",
                "platformVersion": android_version,
                "deviceName": device_model,  # 设备型号作为名称
                "appPackage": app_package,
                "appActivity": app_activity,
                "noReset": True,
                "automationName": "UiAutomator2"
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取设备 {udid} 信息失败: {e.output}")
        except Exception as e:
            raise RuntimeError(f"解析设备信息失败: {str(e)}")

    @staticmethod
    def select_device() -> Dict[str, str]:
        """交互式选择一个已连接的设备，并返回其配置信息"""
        devices = DeviceDetector.get_connected_devices()
        if not devices:
            raise RuntimeError("未检测到任何已连接的设备，请检查ADB连接")

        # 如果只有一个设备，直接返回其信息
        if len(devices) == 1:
            print(f"自动选择唯一设备: {devices[0]}")
            return DeviceDetector.get_device_info(devices[0])

        # 多个设备时，让用户选择
        print("已检测到多个设备，请选择：")
        for i, udid in enumerate(devices, 1):
            # 简单显示设备型号，方便用户识别
            try:
                model = subprocess.check_output(
                    ["adb", "-s", udid, "shell", "getprop", "ro.product.model"],
                    text=True
                ).strip()
                print(f"{i}. {udid} ({model})")
            except BaseException:
                print(f"{i}. {udid} (未知型号)")

        # 输入选择
        while True:
            try:
                choice = int(input(f"请输入序号 (1-{len(devices)}): ")) - 1
                if 0 <= choice < len(devices):
                    return DeviceDetector.get_device_info(devices[choice])
                else:
                    print(f"请输入1到{len(devices)}之间的序号")
            except ValueError:
                print("请输入有效的数字")


# 测试示例
if __name__ == "__main__":
    try:
        device_config = DeviceDetector.select_device()
        print("\n设备配置信息：")
        for key, value in device_config.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"错误: {str(e)}")
