from loguru import logger
import subprocess
import os
import re
import hashlib
import msgpack
from pathlib import Path
from uuid import uuid4
from PySide6.QtCore import QObject, QTimer, Signal, Slot

def get_file_hash(file_path):
    hash_sha256 = hashlib.sha256()

    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()

def get_file_title(file_path):
    title = ''

    with open(file_path, encoding='utf-8') as f:
        line = f.readline()
        mathches = re.findall(r"^#\s*(.+)", line)
        if mathches:
            title = mathches[0]

    return title

class Note(QObject):
    modified = Signal(str)
    name_changed = Signal(str)
    def __init__(self, name='Untitled', path=Path(), output=Path(), id=''):
        super().__init__()

        if not id:
            id = str(uuid4())

            path = Path.cwd() / '.notes' / (id + '.md')

            # create new file
            path.touch(exist_ok=True)

        self._file_hash = get_file_hash(path)

        self._name = name
        self._path = path
        self._id = id
        self._output = output

    @property
    def name(self):
        """The name property."""
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def path(self):
        """The path property."""
        return self._path
    @path.setter
    def path(self, value):
        self._path = value

    @property
    def output(self):
        """The output property."""
        return self._output
    @output.setter
    def output(self, value):
        self._output = value

    def serialize(self):
        return {
            'name': self._name,
            'file_path': str(self._path),
            'output': str(self._output),
            'id': self._id
        }

    def check_file_status(self):
        hash = get_file_hash(self._path)
        if hash != self._file_hash:
            self._file_hash = hash

            name = self._path.stem

            # create the output folder
            folder = Path.cwd() / '.htmls' / name
            if not os.path.exists(folder):
                os.makedirs(folder)

            # markdown to html
            self._output = folder / (self._id + '.html')
            subprocess.run(['pandoc', '-s', str(self._path), '-o', self._output])

            # web view set url with the local html
            # self.web_view.setUrl(output.as_uri())
            self.modified.emit(self._output.as_uri())

            name = get_file_title(self._path)
            if name != self._name:
                self._name = name
                self.name_changed.emit(name)

class Book(QObject):
    current_note_modified = Signal(str)
    current_note_name_change = Signal(str)

    new_note = Signal(Note)
    current_note_changed = Signal(Note)

    def __init__(self):
        super().__init__()

        self._notes: list[Note] = []
        self._current_note: Note | None = None

        self._timer = QTimer(self)

        self._timer.timeout.connect(self._on_check_file_status)

        self._timer.start(1000)

        self.load()

    def __iter__(self):
        return iter(self._notes)

    def _bool__(self):
        return self._notes

    @Slot()
    def _on_check_file_status(self):
        if self._current_note:
            self._current_note.check_file_status()

    @Slot()
    def _on_note_modify(self, path: str):
        if self.sender() is self._current_note:
            self.current_note_modified.emit(path)

    @Slot()
    def _on_note_name_change(self, name: str):
        if self.sender() is self._current_note:
            self.current_note_name_change.emit(name)

    def create_note(self):
        self._add_note(Note())

    def _add_note(self, note: Note):
        self._notes.append(note)

        self._current_note = note;

        note.modified.connect(self._on_note_modify)
        note.name_changed.connect(self._on_note_name_change)

        self.new_note.emit(note)


    def save(self):
        file_name = Path.cwd() / 'book'
        with open(file_name, 'wb') as file:
            file.write(msgpack.packb({
                'notes': [x.serialize() for x in self._notes]
            })) #type: ignore

    def load(self):
        file_name = Path.cwd() / 'book'

        if file_name.exists():
            with open(file_name, 'rb') as file:
                parsed = msgpack.unpackb(file.read())
                for x in parsed['notes']:
                    self._add_note(Note(x['name'], Path(x['file_path']), 
                                        Path(x['output']), x['id']))

        if self._notes:
            self._current_note = self._notes[0]

    @property
    def current_note(self):
        """The current_note property."""
        return self._current_note
    @current_note.setter
    def current_note(self, value):
        if self._current_note == value:
            return
        self._current_note = value
        self.current_note_changed.emit(value)
