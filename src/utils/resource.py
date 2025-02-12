from pathlib import Path

def url(path):
    theme = 'light'
    return str(Path('image') / theme / path)
