from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

class MouseChartView(QChartView):
    def __init__(self, chart, parent=None):
        super().__init__(chart, parent)
        self.setDragMode(QChartView.DragMode.NoDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.last_mouse_pos = None
        self._rect = self.chart().plotArea()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.chart().zoomReset()
        elif event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QChartView.DragMode.ScrollHandDrag)
            self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragMode() == QChartView.DragMode.ScrollHandDrag and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.chart().scroll(-delta.x(), delta.y())
            self.last_mouse_pos = event.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QChartView.DragMode.NoDrag)
            self.last_mouse_pos = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.chart().zoom(factor)

    def reset(self):
        self.chart().zoomReset()
        self.chart().setPlotArea(self._rect)

    def init_reset(self):
        self._rect = self.chart().plotArea()
