from pathlib import Path
import socket
import subprocess
import signal
import os
from PySide6.QtCore import QObject

class Nvim(QObject):
    def __init__(self):
        super().__init__()
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._process = subprocess.Popen(['nvim-qt', '--', '--cmd', '"let g:switch_enabled=1"'])
        self._process = subprocess.Popen(['nvim-qt', '--', '--cmd', 'let g:switch_enabled=1'])
        # self._process.wait()
        self._client.connect(('127.0.0.1', 36795))

    def switch(self, path: Path):
        self._client.sendall(str(path).encode('utf-8'))

    def close(self):
        self._client.close()
        try:
            os.kill(self._process.pid, signal.SIGTERM)
        except: ...
