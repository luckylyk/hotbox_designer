from PySide2 import QtWidgets, QtCore, QtGui
from hotbox_designer.interactive import Shape, get_shape_rect_from_options
from hotbox_designer.painting import draw_shape
from hotbox_designer.geometry import proportional_rect
from hotbox_designer.convert import VALIGNS, HALIGNS
from hotbox_designer.utils import get_cursor


class HotboxReader(QtWidgets.QWidget):
    def __init__(self, hotbox_data, parent=None):
        super(HotboxReader, self).__init__(parent)
        flags = (
            QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint)

        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        settings = hotbox_data['general']
        self.triggering = settings['triggering'] 
        self.center = QtCore.QPoint(settings['centerx'], settings['centery'])
        self.setFixedSize(settings['width'], settings['height'])
        self.shapes = [Shape(data) for data in hotbox_data['shapes']]

        self.left_clicked = False
        self.right_clicked = False

    def mouseMoveEvent(self, event):
        for shape in self.shapes:
            if shape.is_interactive():
                shape.set_hovered(get_cursor(self))
                if shape.hovered and self.clicked:
                    shape.clicked = True
                else:
                    shape.clicked = False
        self.repaint()

    @property
    def clicked(self):
        return self.right_clicked or self.left_clicked

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.right_clicked = True
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_clicked = True
        for shape in self.shapes:
            if shape.is_interactive():
                if shape.hovered and self.clicked:
                    shape.clicked = True
                else:
                    shape.clicked = False
        self.repaint()

    def execute_hovered_shape(self):
        for shape in self.shapes:
            if shape.is_interactive() and shape.hovered:
                shape.execute(left=self.left_clicked, right=self.right_clicked)
                close = shape.autoclose(
                    left=self.left_clicked, right=self.right_clicked)
                break

    def mouseReleaseEvent(self, event):
        close = True
        self.execute_hovered_shape()
        if event.button() == QtCore.Qt.RightButton:
            self.right_clicked = False
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_clicked = False
        for shape in self.shapes:
            if shape.is_interactive():
                if shape.hovered and self.clicked:
                    shape.clicked = True
                else:
                    shape.clicked = False
        if close is True:
            self.hide()
        self.repaint()

    def paintEvent(self, _):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        for shape in self.shapes:
            shape.draw(painter)
        painter.end()

    def show(self):
        super(HotboxReader, self).show()
        self.move(QtGui.QCursor.pos() - self.center)

    def hide(self):
        if self.triggering == 'passive':
            self.execute_hovered_shape()
        super(HotboxReader, self).__init__()
