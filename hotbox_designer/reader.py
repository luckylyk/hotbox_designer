import sys
import math
from PySide2 import QtWidgets, QtCore, QtGui
from hotbox_designer.interactive import Shape, get_shape_rect_from_options
from hotbox_designer.geometry import proportional_rect
from hotbox_designer.convert import VALIGNS, HALIGNS
from hotbox_designer.utils import get_cursor
from hotbox_designer.painting import (
    draw_shape, draw_aiming, draw_aiming_background)


class HotboxReader(QtWidgets.QWidget):
    def __init__(self, hotbox_data, parent=None):
        super(HotboxReader, self).__init__(parent)
        flags = (
            QtCore.Qt.Tool |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint)

        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        settings = hotbox_data['general']
        self.triggering = settings['triggering']
        self.aiming = settings['aiming']
        self.center = QtCore.QPoint(settings['centerx'], settings['centery'])
        self.setFixedSize(settings['width'], settings['height'])
        self.shapes = [Shape(data) for data in hotbox_data['shapes']]
        self.interactive_shapes = [
            s for s in self.shapes if s.is_interactive()]

        self.left_clicked = False
        self.right_clicked = False

    def mouseMoveEvent(self, _):
        shapes = self.interactive_shapes
        if self.aiming is True:
            set_closer_shapes_hovered(shapes, get_cursor(self))
        else:
            set_shapes_hovered(shapes, get_cursor(self), self.clicked)
        self.repaint()

    def leaveEvent(self, _):
        shapes = self.interactive_shapes
        if self.aiming is True:
            set_closer_shapes_hovered(shapes, get_cursor(self))
        else:
            set_shapes_hovered(shapes, get_cursor(self), self.clicked)
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

    def mouseReleaseEvent(self, event):
        close = execute_hovered_shape(
            self.shapes, self.left_clicked, self.right_clicked)

        if event.button() == QtCore.Qt.RightButton:
            self.right_clicked = False
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_clicked = False

        for shape in self.shapes:
            if shape.is_interactive():
                shape.clicked = bool(shape.hovered and self.clicked)

        if close is True:
            self.hide()
        self.repaint()

    def paintEvent(self, _):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.aiming:
            # this is a workaround because a fully transparent widget doesn't
            # execute the mouseMove event when the cursor is hover a
            # transparent of the widget. This draw the reader rect has black
            # rect with a 1/255 transparency value
            draw_aiming_background(painter, self.rect())
        for shape in self.shapes:
            shape.draw(painter)
        if self.aiming:
            draw_aiming(painter, self.center, get_cursor(self))
        painter.end()

    def show(self):
        super(HotboxReader, self).show()
        self.move(QtGui.QCursor.pos() - self.center)

    def hide(self):
        if self.triggering == 'click or close':
            execute_hovered_shape(self.shapes, left=True)
        super(HotboxReader, self).hide()


def set_shapes_hovered(shapes, cursor, clicked):
    for shape in shapes:
        if shape.is_interactive():
            shape.set_hovered(cursor)
            if shape.hovered and clicked:
                shape.clicked = True
            else:
                shape.clicked = False


def set_closer_shapes_hovered(shapes, cursor):
    shapedistances = {
        distance(shape.rect.center(), cursor): shape
        for shape in shapes}
    for shape in shapes:
        shape.hovered = False
    shapedistances[min(shapedistances.keys())].hovered = True


def distance(a, b):
    x = (b.x() - a.x())**2
    y = (b.y() - a.y())**2
    return math.sqrt(abs(x + y))


def execute_hovered_shape(shapes, left=False, right=False):
    for shape in shapes:
        if shape.is_interactive() and shape.hovered:
            shape.execute(left=left, right=right)
            return shape.autoclose(left=left, right=right)
    return False
