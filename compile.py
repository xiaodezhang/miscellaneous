import subprocess
from src.appconfig import app_config
project_name = app_config.project
with open("version.txt") as file:
    version = file.read()
    subprocess.run([
        "nuitka.cmd"
        , "src/main.py"
        , "--standalone"
        , "--plugin-enable=pyside6"
        , "--windows-console-mode=disable"
        , "--include-package=qt_material"
        , "--windows-icon-from-ico=./image/dns.png"
        , "--include-data-dir=./image=image"
        , "--include-data-dir=./style=style"
        , "--include-data-dir=./net=net"
        , "--include-data-file=./version.txt=version.txt"
        , "--include-data-file=./appconfig.json=appconfig.json"
        , f"--output-filename={project_name}"
        , "--output-dir=./dist"
        , f"--windows-file-version={version}"
        , f"--windows-product-name={project_name}"
        , "--windows-company-name=CNSCAN"
    ])
