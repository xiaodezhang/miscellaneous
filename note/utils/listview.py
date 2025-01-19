from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel
    , QScrollArea
    , QVBoxLayout
    , QWidget
)
from loguru import logger
from utils import override, replace_class
from utils.hoverablewidget import HoverableWidget

class Item(HoverableWidget):
    actived = Signal(int)
    def __init__(self):
        super().__init__()
        self._id = 0
        self._active = False 

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value: int):
        self._id = value

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.set_active()
        return super().mousePressEvent(event)

    def is_active(self):
        return self._active

    def set_active(self):
        self.actived.emit(self._id)

    def _set_active(self):
        replace_class(self, 'bg-dark', 'bg-light')
        self.style().unpolish(self)
        self.style().polish(self)
        self._active = True 

    def set_inactive(self):
        replace_class(self, 'bg-light', 'bg-dark')
        self.style().unpolish(self)
        self.style().polish(self)
        self._active = False 

class TextItem(Item):
    def __init__(self, text: str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.addStretch()
        layout.addWidget(QLabel(text), Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

class Scene(QWidget):
    item_changed = Signal(Item)
    def __init__(self, orientation, reversed):
        super().__init__()
        self._reversed = reversed

        self._layout = (
            QVBoxLayout() if orientation == Qt.Orientation.Vertical 
            else QHBoxLayout()
        )
        self._layout.addStretch()
        self.setLayout(self._layout);

        self._items: list[Item] = []
        self._current_item: Item|None = None

    def __iter__(self):
        return iter(self._items)

    def __bool__(self):
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, id: int):
        if id > len(self._items)-1:
            return None
        return self._items[id]

    @property
    def current_item(self):
        """The current_item property."""
        return self._current_item
    @current_item.setter
    def current_item(self, value: Item|None):
        if self.current_item == value:
            return
        if self.current_item:
            self.current_item.set_inactive()
        self._current_item = value
        if value:
            value._set_active()
        self.item_changed.emit(value)

    def set_orientation(self, orientation: Qt.Orientation):
        while self._layout.count():
            self._layout.takeAt(0)
        QWidget().setLayout(self._layout)

        self._layout = (
            QVBoxLayout() if orientation == Qt.Orientation.Vertical 
            else QHBoxLayout()
        )
        for item in self._items:
            if self._reversed:
                self._layout.insertWidget(0, item)
            else:
                self._layout.addWidget(item)
        self._layout.addStretch()
        self.setLayout(self._layout);

    def delete_item(self, item: Item):
        self._items.remove(item)
        for i, it in enumerate(self._items):
            it.id = i
        if self.current_item == item:
            if self._items:
                self.current_item = self._items[0]
            else:
                self.current_item = None
        self._layout.removeWidget(item)
        item.deleteLater()

    def delete_next(self, item: Item):
        if item.id+1 > len(self._items)-1:
            return
        items = self._items[item.id+1:]
        for it in items:
            self.delete_item(it)

    def delete_previous(self, item: Item):
        items = self._items[:item.id]
        for it in items:
            self.delete_item(it)

    def add_item(self, new_item: Item):
        if self._reversed:
            for item in self._items:
                item._id += 1
            self._layout.insertWidget(0, new_item)
            self._items.insert(0, new_item)

        else:
            new_item._id = len(self._items)
            self._layout.insertWidget(new_item._id, new_item)
            self._items.append(new_item)

        new_item.actived.connect(lambda x: self.set_active(x))

        return new_item

    def set_active(self, id: int):
        self.current_item = self[id]

    def set_inactive(self):
        self.current_item = None

class ListView(QScrollArea):
    item_changed = Signal(Item)
    def __init__(
        self
        , orientation: Qt.Orientation=Qt.Orientation.Vertical
        , reversed=True
    ):
        super().__init__()
        self._orientation = orientation
        self._reversed = reversed 
        self.setWidgetResizable(True)
        self._add_scene()

    @override
    def wheelEvent(self, arg__1) -> None:
        if self._orientation is Qt.Orientation.Horizontal:
            value = int(5*arg__1.angleDelta().y())
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value()-value)
        else:
            super().wheelEvent(arg__1)

    def __len__(self):
        return len(self._scene)

    def __iter__(self):
        return iter(self._scene)

    def __bool__(self):
        return bool(self._scene)

    def __getitem__(self, id: int):
        return self._scene[id]

    @property
    def current_item(self):
        return self._scene.current_item

    def set_orientation(self, orientation: Qt.Orientation):
        self._orientation = orientation
        self._scene.set_orientation(orientation);

    def _add_scene(self):
        self._scene = Scene(self._orientation, self._reversed)
        self.setWidget(self._scene)
        def on_item_change(item):
            self.item_changed.emit(item)
        self._scene.item_changed.connect(on_item_change)

    def set_table_style(self):
        self._scene._layout.setSpacing(0)
        self._scene._layout.setContentsMargins(0, 0, 0, 0)

    def set_active(self, id: int):
        self._scene.set_active(id)

    def set_inactive(self):
        self._scene.set_inactive()

    def add_item(self, item: Item):
        return self._scene.add_item(item)

    def delete_item(self, item: Item):
        self._scene.delete_item(item)

    def delete_previous(self, item: Item):
        self._scene.delete_previous(item)

    def delete_next(self, item: Item):
        self._scene.delete_next(item)

    def clear(self):
        if self.widget():
            self.takeWidget()
            self._scene.deleteLater()
            self._add_scene()
