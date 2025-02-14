from pathlib import Path
import socket
import subprocess
import signal
import os
from PySide6.QtCore import QObject
from loguru import logger

class Nvim(QObject):
    def __init__(self):
        super().__init__()

        self._valid = True
        try:
            subprocess.run(['nvim', '--version'], check=True)

            self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._process = subprocess.Popen(['nvim-qt', '--', '--cmd', 'let g:switch_enabled=1'])
            self._client.connect(('127.0.0.1', 36795))

        except Exception as e:
            logger.warning(f"nvim connected failed: {str(e)}")
            self._valid = False

    def switch(self, path: Path):
        if self._valid:
            self._client.sendall(str(path).encode('utf-8'))

    def close(self):
        if self._valid:
            try:
                self._client.close()
                os.kill(self._process.pid, signal.SIGTERM)
            except: ...
