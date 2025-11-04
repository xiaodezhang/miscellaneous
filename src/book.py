import shutil
import subprocess
import os
import re
import hashlib
from loguru import logger
import msgpack
from pathlib import Path
from uuid import uuid4
from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from platformdirs import user_data_path

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
    modified = Signal(QUrl)
    name_changed = Signal(str)
    def __init__(self, name='Untitled', id=''):
        super().__init__()

        self._name = name
        self._id = id if id else str(uuid4())

        # create the note folder
        if not os.path.exists(self.note_folder):
            os.makedirs(self.note_folder)

        # create new note file
        self.path.touch(exist_ok=True)

        # create the output folder
        if not os.path.exists(self.html_folder):
            os.makedirs(self.html_folder)

        # create output file
        self.output_file.touch(exist_ok=True)

        self._file_hash = get_file_hash(self.path)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        """The name property."""
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def path(self) -> Path:
        """The path property."""
        return self.note_folder / (self._id + '.md')

    @property
    def output_file(self) -> Path:
        """The output property."""
        return self.html_folder / (self._id + '.html')

    @property
    def url(self):
        """The output property."""
        return QUrl.fromLocalFile(self.output_file.resolve())

    # @property
    # def url(self) -> str:
    #     """The output property."""
    #     return f'http://localhost:8000/{self._id}/{self._id}.html'

    def serialize(self):
        return {
            'name': self._name,
            'id': self._id
        }

    def add_resource(self, file_path: str):
        file_name = Path(file_path).name

        shutil.copy(file_path, self.note_folder / file_name)
        shutil.copy(file_path, self.html_folder / file_name)

    def check_file_status(self):
        hash = get_file_hash(self.path)
        if hash != self._file_hash:
            self.build(hash)

    def build(self, hash = None):
        if hash is not None:
            self._file_hash = hash

        else:
            self._file_hash = get_file_hash(self.path)

        pandoc = Path.cwd() / 'external' / 'pandoc.exe'
        html = Path.cwd() / 'style' / 'github.html'

        # markdown to html
        subprocess.run([
            pandoc, 
            '-s', 
            str(self.path), 
            '-o', 
            self.output_file, 
            f'--template={html}',
            '--from=gfm',
        ], creationflags=subprocess.CREATE_NO_WINDOW)

        self._check_and_copy_resources()

        self.modified.emit(self.url)

        name = get_file_title(self.path)
        if name != self._name:
            self._name = name
            self.name_changed.emit(name)

    def export_to_html(self, path):
        pandoc = Path.cwd() / 'external' / 'pandoc.exe'
        html = Path.cwd() / 'style' / 'github.html'
        # markdown to html
        subprocess.run([
            pandoc, 
            str(self.path), 
            '-o', 
            path,
            f'--template={html}',
            '--from=gfm',
            '--embed-resources',
            '--standalone', 
        ], cwd=self.note_folder, creationflags=subprocess.CREATE_NO_WINDOW)

    def export_to_word(self, path):
        pandoc = Path.cwd() / 'external' / 'pandoc.exe'
        docx = Path.cwd() / 'style' / 'reference.docx'
        # markdown to html
        subprocess.run([
            pandoc, 
            str(self.path), 
            '-o', 
            path,
            f'--reference-doc={docx}',
            '--from=gfm',
            '--standalone', 
        ], cwd=self.note_folder, creationflags=subprocess.CREATE_NO_WINDOW)

    def _check_and_copy_resources(self):
        note_resources = [x.name for x in self.note_folder.iterdir()]
        html_resources = [x.name for x in self.html_folder.iterdir()]
        to_move_resources = [x for x in note_resources if x not in html_resources]
        for x in to_move_resources:
            shutil.copy(self.note_folder / x, self.html_folder / x)

    @property
    def html_folder(self):
        return user_data_path() / 'miscellaneous' / '.htmls' / self._id

    @property
    def note_folder(self):
        return user_data_path() / 'miscellaneous' / '.notes' / self._id

    def clear(self):
        shutil.rmtree(self.html_folder)
        shutil.rmtree(self.note_folder)


class Book(QObject):
    current_note_modified = Signal(QUrl)
    current_note_name_change = Signal(str)

    new_note = Signal(Note)
    current_note_changed = Signal(Note)

    note_removed = Signal(Note)

    def __init__(self):
        super().__init__()

        self._notes: list[Note] = []
        self._current_note: Note | None = None

        self._timer = QTimer(self)

        if not os.path.exists(self.user_path):
            os.makedirs(self.user_path)

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
    def _on_note_modify(self, url: str):
        if self._current_note:
            if url == self._current_note.url:
                self.current_note_modified.emit(url)

    @Slot() #type: ignore
    def _on_note_name_change(self, name: str) -> None:
        if self._current_note:
            if name == self._current_note.name:
                self.current_note_name_change.emit(name)

    def create_note(self):
        self._add_note(Note())

    def remove_note(self, note: Note):
        note.modified.disconnect(self._on_note_modify)
        note.name_changed.disconnect(self._on_note_name_change)

        self._notes.remove(note)

        note.clear()

        self.note_removed.emit(note)

        if note is self._current_note:
            self.current_note = self._notes[-1] if self._notes else None

    def _add_note(self, note: Note):
        self._notes.append(note)

        self._current_note = note;

        note.modified.connect(self._on_note_modify)
        note.name_changed.connect(self._on_note_name_change)

        self.new_note.emit(note)

        return note

    def add_resource(self, file_path: str):
        if self._current_note:
            self._current_note.add_resource(file_path)

    @property
    def user_path(self):
        return user_data_path() / 'miscellaneous'

    def save(self):
        file_name = self.user_path / 'book'
        with open(file_name, 'wb') as file:
            file.write(msgpack.packb({
                'notes': [x.serialize() for x in self._notes]
            })) # type: ignore

    def load(self):
        folder = self.user_path / '.notes'
        if not folder.exists():
            folder.mkdir()
            return

        for note_path in folder.iterdir():
            note = self._add_note(Note(id=note_path.stem))
            note.build()

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
