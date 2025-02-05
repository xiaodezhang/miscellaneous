import subprocess
project_name = 'Note'
with open("version.txt") as file:
    version = file.read()
    subprocess.run([
        "nuitka.cmd"
        , "src/main.py"
        , "--standalone"
        , "--plugin-enable=pyside6"
        , "--windows-console-mode=disable"
        , "--include-package=qt_material"
        , "--windows-icon-from-ico=./image/note_stack.png"
        , "--include-data-dir=./image=image"
        , "--include-data-dir=./style=style"
        , "--include-data-dir=./external=external"
        , "--include-data-file=./version.txt=version.txt"
        , f"--output-filename={project_name}"
        , "--output-dir=./dist"
        , f"--windows-file-version={version}"
        , f"--windows-product-name={project_name}"
        , "--windows-company-name=duduhome"
    ])
