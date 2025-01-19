from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLayout, QSizePolicy, QToolButton, QWidget

def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def override(method):
    return method

def remove_all_widgets_from_layout(layout: QLayout):
    # 遍历布局中的所有项
    while layout.count():
        item = layout.takeAt(0)  # 取出布局中的第一个项
        if item.widget():  # 如果项是小部件
            widget = item.widget()
            widget.setParent(None)  # 从父部件中移除小部件
            widget.deleteLater()   # 标记小部件以便稍后删除
        elif item.layout():  # 如果项是布局
            # 递归调用来移除子布局中的小部件
            remove_all_widgets_from_layout(item.layout())
        # 注意：如果 item 既不是 widget 也不是 layout，那么可能是一个空的间隔或其他类型的项

def take_all_widgets_from_layout(layout: QLayout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():  # 如果项是小部件
            yield item.widget()
        if item.layout():
            take_all_widgets_from_layout(item.layout())

def place_holder():
    widget = QWidget()
    widget.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return widget

#辅助打印函数
def to_hex(b: bytes):
    return [hex(x) for x in b]

def remove_class(ins, class_name):
    current_classes = getattr(ins, 'property')('class')
    if current_classes:
        class_list = current_classes.split()
        if class_name in class_list:
            class_list.remove(class_name)
            updated_classes = ' '.join(class_list)
            getattr(ins, 'setProperty')('class', updated_classes)
            getattr(getattr(ins, 'style')(), 'unpolish')(ins)
            getattr(getattr(ins, 'style')(), 'polish')(ins)

def append_class(ins, class_name):
    current_classes = getattr(ins, 'property')('class')
    if current_classes:
        class_list = current_classes.split()
        if class_name not in class_list:
            class_list.append(class_name)
        updated_classes = ' '.join(class_list)
    else:
        updated_classes = class_name
    getattr(ins, 'setProperty')('class', updated_classes)
    getattr(getattr(ins, 'style')(), 'unpolish')(ins)
    getattr(getattr(ins, 'style')(), 'polish')(ins)

def replace_class(ins, old, new):
    remove_class(ins, old)
    append_class(ins, new)

def create_custom_grayscale_icon(icon_path):
    pixmap = QPixmap(icon_path)
    img = pixmap.toImage()

    # 遍历每个像素，手动调整灰度
    for y in range(img.height()):
        for x in range(img.width()):
            color = img.pixelColor(x, y)
            # 使用自定义灰度处理，特别处理亮度高的颜色（如白色）
            gray = 0.3 * color.red() + 0.59 * color.green() + 0.11 * color.blue()

            # 如果灰度太亮（接近白色），强制变为深灰色
            if gray > 220:  # 白色阈值，具体值可调整
                gray = 150  # 设置成较深的灰色

            # 将每个像素变为灰度值
            img.setPixelColor(x, y, Qt.GlobalColor.gray)

    # 返回修改后的 QIcon
    return QIcon(QPixmap.fromImage(img))
