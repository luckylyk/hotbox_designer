
from PySide2 import QtCore, QtGui, QtWidgets

from hotbox_designer.interactive import Manipulator, SelectionSquare
from hotbox_designer.geometry import Transform, snap, get_combined_rects
from hotbox_designer.painting import draw_editor, draw_editor_center
from hotbox_designer.qtutils import get_cursor


class ShapeEditArea(QtWidgets.QWidget):
    selectedShapesChanged = QtCore.Signal()
    increaseUndoStackRequested = QtCore.Signal()
    centerMoved = QtCore.Signal(int, int)

    def __init__(self, options, parent=None):
        super(ShapeEditArea, self).__init__(parent)
        self.setFixedSize(750, 550)
        self.setMouseTracking(True)
        self.options = options

        self.selection = Selection()
        self.selection_square = SelectionSquare()
        self.manipulator = Manipulator()
        self.transform = Transform()

        self.shapes = []
        self.clicked_shape = None
        self.clicked = False
        self.handeling = False
        self.manipulator_moved = False
        self.edit_center_mode = False
        self.increase_undo_on_release = False

        self.ctrl_pressed = False
        self.shit_pressed = False

    def mouseMoveEvent(self, _):
        cursor = get_cursor(self)
        if self.edit_center_mode is True:
            if self.clicked is False:
                return
            if self.transform.snap:
                x, y = snap(cursor.x(), cursor.y(), self.transform.snap)
            else:
                x, y = cursor.x(), cursor.y()
            self.centerMoved.emit(x, y)
            self.increase_undo_on_release = True
            self.repaint()
            return

        for shape in self.shapes:
            shape.set_hovered(cursor)

        if self.selection_square.handeling:
            self.selection_square.handle(cursor)

        if self.handeling is False:
            return self.repaint()

        self.manipulator_moved = True
        rect = self.manipulator.rect
        if self.transform.direction:
            self.transform.resize([s.rect for s in self.selection], cursor)
            self.manipulator.update_geometries()
        elif rect is not None and rect.contains(cursor):
            self.transform.move([s.rect for s in self.selection], cursor)
            self.manipulator.update_geometries()
        for shape in self.shapes:
            shape.synchronize_rect()
            shape.synchronize_image()
        self.increase_undo_on_release = True
        self.selectedShapesChanged.emit()
        self.repaint()

    def mousePressEvent(self, _):
        self.setFocus(QtCore.Qt.MouseFocusReason)
        cursor = get_cursor(self)
        direction = self.manipulator.get_direction(cursor)
        self.clicked = True
        self.transform.direction = direction

        self.manipulator_moved = False
        rect = self.manipulator.rect
        if rect is not None:
            self.transform.set_rect(rect)
            self.transform.reference_rect = QtCore.QRectF(rect)

        self.clicked_shape = None
        for shape in reversed(self.shapes):
            if shape.rect.contains(cursor):
                self.clicked_shape = shape
                break

        if rect and rect.contains(cursor):
            self.transform.set_reference_point(cursor)
        handeling = bool(direction or rect.contains(cursor) if rect else False)

        self.handeling = handeling
        if not self.handeling:
            self.selection_square.clicked(cursor)

        self.repaint()

    def mouseReleaseEvent(self, _):
        if self.edit_center_mode is True:
            self.clicked = False
            return

        shape = self.clicked_shape
        selection_update_conditions = (
            self.handeling is False
            or shape not in self.selection
            and self.manipulator_moved is False)
        if selection_update_conditions:
            self.selection.set([shape] if shape else None)
            self.update_selection()

        if self.selection_square.handeling:
            shapes = [
                s for s in self.shapes
                if s.rect.intersects(self.selection_square.rect)]
            if shapes:
                self.selection.set(shapes)
                rects = [shape.rect for shape in self.selection]
                self.manipulator.set_rect(get_combined_rects(rects))
                self.selectedShapesChanged.emit()
        self.selection_square.release()

        if self.increase_undo_on_release:
            self.increaseUndoStackRequested.emit()
            self.increase_undo_on_release = False

        self.clicked = False
        self.handeling = False
        self.repaint()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self.transform.square = True
            self.shit_pressed = True

        if event.key() == QtCore.Qt.Key_Control:
            self.ctrl_pressed = True

        self.selection.mode = get_selection_mode(
            shift=self.shit_pressed,
            ctrl=self.ctrl_pressed)

        self.repaint()

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self.transform.square = False
            self.shit_pressed = False

        if event.key() == QtCore.Qt.Key_Control:
            self.ctrl_pressed = False

        self.selection.mode = get_selection_mode(
            shift=self.shit_pressed,
            ctrl=self.ctrl_pressed)

        self.repaint()

    def update_selection(self):
        rects = [shape.rect for shape in self.selection]
        self.manipulator.set_rect(get_combined_rects(rects))
        self.selectedShapesChanged.emit()

    def paintEvent(self, _):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.paint(painter)
        painter.end()

    def paint(self, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        draw_editor(painter, self.rect(), snap=self.transform.snap)
        for shape in self.shapes:
            shape.draw(painter)
        self.manipulator.draw(painter, get_cursor(self))
        self.selection_square.draw(painter)
        if self.edit_center_mode is True:
            point = self.options['centerx'], self.options['centery']
            draw_editor_center(painter, self.rect(), point)


class Selection():
    def __init__(self):
        self.shapes = []
        self.mode = 'replace'

    def set(self, shapes):
        if self.mode == 'add':
            if shapes is None:
                return
            return self.add(shapes)
        elif self.mode == 'replace':
            if shapes is None:
                return self.clear()
            return self.replace(shapes)
        elif self.mode == 'invert':
            if shapes is None:
                return
            return self.invert(shapes)
        elif self.mode == 'remove':
            if shapes is None:
                return
            for shape in shapes:
                if shape in self.shapes:
                    self.remove(shape)

    def replace(self, shapes):
        self.shapes = shapes

    def add(self, shapes):
        self.shapes.extend(shapes)

    def remove(self, shape):
        self.shapes.remove(shape)

    def invert(self, shapes):
        for shape in shapes:
            if shape not in self.shapes:
                self.add([shape])
            else:
                self.remove(shape)

    def clear(self):
        self.shapes = []

    def __iter__(self):
        return self.shapes.__iter__()


def get_selection_mode(ctrl, shift):
    if not ctrl and not shift:
        return 'replace'
    elif ctrl and shift:
        return 'invert'
    elif shift and not ctrl:
        return 'add'
    elif ctrl and not shift:
        return 'remove'
