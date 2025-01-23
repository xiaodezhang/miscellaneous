from loguru import logger
from pathlib import Path
import subprocess
from PySide6.QtCore import QObject
import winreg

HONGKONG_IP= '154.197.26.66'
USA_IP = '156.247.14.88'

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

class ProxyStatus(QObject):
    def __init__(self, enabled: list[bool], connected: bool, ip: str):
        super().__init__()
        self._enabled = enabled 
        self._ip = ip
        self._process = self._connect_proxy() if connected else None

    @property
    def opened(self):
        return self._enabled[0] and self._process is not None

    @property
    def connected(self):
        return self._process is not None

    def open(self):
        if not self._enabled[0]:
            toggle_proxy(True)

        if self._process is None:
            self._process = self._connect_proxy()

        self._enabled[0] = True

    def disconnect_proxy(self):
        if self._process is not None:
            if self._process.poll() is None:  # 检查进程是否还在运行
                self._process.terminate()  # 优雅终止
                try:
                    self._process.wait(timeout=5)  # 等待子进程退出
                except subprocess.TimeoutExpired:
                    self._process.kill()  # 强制终止
                    logger.info(f"Process {self._process.pid} forcefully killed.")
            else:
                logger.info(f"Process {self._process.pid} already terminated.")

            self._process = None

    def _connect_proxy(self):
        gost = Path.cwd() / 'external' / 'gost-windows-amd64.exe'
        return subprocess.Popen(
            [str(gost), '-L=:8219', f'-F=http+tls://{self._ip}:443']
           , creationflags=subprocess.CREATE_NO_WINDOW)

class Proxy(QObject):
    def __init__(self):
        super().__init__()

        set_proxy_settings('127.0.0.1', 8219)
        toggle_proxy(True)
        self._enabled = [True]

        self._hongkong_proxy = ProxyStatus(self._enabled, False, HONGKONG_IP)
        self._usa_proxy = ProxyStatus(self._enabled, True, USA_IP)

    def toggle_hongkong(self):
        if self._hongkong_proxy.opened:
            self._toggle_proxy(False)

        else:
            if self._usa_proxy.connected:
                self._usa_proxy.disconnect_proxy()

            self._hongkong_proxy.open()

    def toggle_usa(self):
        if self._usa_proxy.opened:
            self._toggle_proxy(False)

        else:
            if self._hongkong_proxy.connected:
                self._hongkong_proxy.disconnect_proxy()

            self._usa_proxy.open()

    def _toggle_proxy(self, flag):
        toggle_proxy(flag)
        self._enabled[0] = flag

    def close(self):
        self._hongkong_proxy.disconnect_proxy()
        self._usa_proxy.disconnect_proxy()

    @property
    def hongkong_opened(self):
        return self._hongkong_proxy.opened

    @property
    def usa_opened(self):
        return self._usa_proxy.opened

