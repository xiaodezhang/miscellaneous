import subprocess
project_name = 'Miscellaneous'
with open("version.txt") as file:
    version = file.read()
    subprocess.run([
        "nuitka.cmd"
        , "src/main.py"
        , "--standalone"
        , "--plugin-enable=pyside6"
        , "--windows-console-mode=disable"
        , "--include-package=qt_material"
        , "--windows-icon-from-ico=./image/stacks.png"
        , "--include-data-dir=./image=image"
        , "--include-data-dir=./style=style"
        , "--include-data-file=./version.txt=version.txt"
        , "--include-data-file=./external/gost-windows-amd64.exe=external/gost-windows-amd64.exe"
        , "--include-data-file=./external/pandoc.exe=external/pandoc.exe"
        , f"--output-filename={project_name}"
        , "--output-dir=./dist"
        , f"--windows-file-version={version}"
        , f"--windows-product-name={project_name}"
        , "--windows-company-name=duduhome"
    ])
