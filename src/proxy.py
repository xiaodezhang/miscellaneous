from loguru import logger
from pathlib import Path
import subprocess
from PySide6.QtCore import QObject
import winreg

HONGKONG_IP= '154.197.26.66'
HONGKONG_LOCAL_PORT = 8219
USA_IP = '156.247.14.88'
USA_LOCAL_PORT = 8229

def get_proxy_settings():
    try:
        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path)
        
        # 获取代理服务器设置
        proxy_enabled, _ = winreg.QueryValueEx(registry_key, "ProxyEnable")
        proxy_server, _ = winreg.QueryValueEx(registry_key, "ProxyServer")
        
        if proxy_enabled:
            return proxy_server
        else:
            return "No proxy enabled"
    
    except Exception as e:
        return f"Error: {e}"

def set_proxy_settings(proxy_address, proxy_port):
    try:
        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        
        # 启用代理设置
        winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        
        # 设置代理服务器地址
        proxy_server = f"{proxy_address}:{proxy_port}"
        winreg.SetValueEx(registry_key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
        
    except Exception as e:
        logger.warning(f"Error setting proxy: {e}")
    finally:
        winreg.CloseKey(registry_key) #type: ignore

def toggle_proxy(flag: bool):
    try:
        # 打开注册表中的 Internet Settings 路径
        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        
        winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if flag else 0)
        
    except Exception as e:
        logger.warning(f"Error toggling proxy: {e}")
    finally:
        winreg.CloseKey(registry_key) #type: ignore

class Proxy(QObject):
    def __init__(self):
        super().__init__()

        self._hongkong_process = self._connect_proxy(HONGKONG_IP, HONGKONG_LOCAL_PORT)
        self._usa_process = self._connect_proxy(USA_IP, USA_LOCAL_PORT)

        set_proxy_settings('127.0.0.1', USA_LOCAL_PORT)
        toggle_proxy(True)

    def _connect_proxy(self, ip, local_port):
        gost = Path.cwd() / 'external' / 'gost-windows-amd64.exe'
        return subprocess.Popen(
            [str(gost), f'-L=:{local_port}', f'-F=http+tls://{ip}:443']
           , creationflags=subprocess.CREATE_NO_WINDOW)

    def toggle_hongkong(self, flag):
        if flag:
            set_proxy_settings('127.0.0.1', HONGKONG_LOCAL_PORT)
        toggle_proxy(flag)

    def toggle_usa(self, flag):
        if flag:
            set_proxy_settings('127.0.0.1', USA_LOCAL_PORT)
        toggle_proxy(flag)

    def close(self):
        self.disconnect_proxy(self._hongkong_process)
        self.disconnect_proxy(self._usa_process)
        toggle_proxy(False)

    def disconnect_proxy(self, process):
        if process is not None:
            if process.poll() is None:  # 检查进程是否还在运行
                process.terminate()  # 优雅终止
                try:
                    process.wait(timeout=5)  # 等待子进程退出
                except subprocess.TimeoutExpired:
                    process.kill()  # 强制终止
                    logger.info(f"Process {process.pid} forcefully killed.")
            else:
                logger.info(f"Process {process.pid} already terminated.")
