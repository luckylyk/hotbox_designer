from hotbox_designer.vendor.Qt import QtWidgets, QtCore, QtGui
from hotbox_designer.interactive import Shape
from hotbox_designer.qtutils import get_cursor
from hotbox_designer.painting import draw_aiming, draw_aiming_background
from hotbox_designer.geometry import distance, segment_cross_rect


class HotboxWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(HotboxWidget, self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.shapes = []
        self.interactive_shapes = []
        self.left_clicked = False
        self.right_clicked = False

    def set_hotbox_data(self, hotbox_data):
        self.shapes = [Shape(shape) for shape in hotbox_data['shapes']]
        self.interactive_shapes = [
            s for s in self.shapes if s.is_interactive()]
        self.repaint()

    def clear(self):
        self.shapes = []
        self.interactive_shapes = []
        self.repaint()

    @property
    def clicked(self):
        return self.right_clicked or self.left_clicked

    def mouseMoveEvent(self, _):
        shapes = self.interactive_shapes
        set_shapes_hovered(shapes, get_cursor(self), self.clicked)
        self.repaint()

    def leaveEvent(self, _):
        shapes = self.interactive_shapes
        set_shapes_hovered(shapes, get_cursor(self), self.clicked)
        self.repaint()

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
        execute_hovered_shape(
            self.shapes, self.left_clicked, self.right_clicked)

        if event.button() == QtCore.Qt.RightButton:
            self.right_clicked = False
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_clicked = False

        for shape in self.shapes:
            if shape.is_interactive():
                shape.clicked = bool(shape.hovered and self.clicked)
        self.repaint()

    def paintEvent(self, _):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        for shape in self.shapes:
            shape.draw(painter)
        painter.end()


class HotboxReader(QtWidgets.QWidget):
    hideSubmenusRequested = QtCore.Signal()

    def __init__(self, hotbox_data, parent=None):
        super(HotboxReader, self).__init__(parent)
        f = (QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(f)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        settings = hotbox_data['general']
        self.triggering = settings['triggering']
        self.aiming = settings['aiming']
        self.is_submenu = settings['submenu']
        self.center = QtCore.QPoint(settings['centerx'], settings['centery'])
        self.setFixedSize(settings['width'], settings['height'])
        self.shapes = [Shape(data) for data in hotbox_data['shapes']]
        self.close_on_leave = settings['leaveclose']
        self.interactive_shapes = [
            s for s in self.shapes if s.is_interactive()]

        self.left_clicked = False
        self.right_clicked = False

    def mouseMoveEvent(self, _):
        self.set_hovered_shapes()

    def leaveEvent(self, _):
        shapes = self.interactive_shapes
        if self.aiming is True:
            set_crossed_shapes_hovered(
                self.center, get_cursor(self), shapes, get_cursor(self))
        else:
            set_shapes_hovered(shapes, get_cursor(self), self.clicked)
        if self.close_on_leave is True:
            self.hide()
        self.repaint()

    @property
    def clicked(self):
        return self.right_clicked or self.left_clicked

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()

        parent = self.parent()
        if parent is not None:
            return parent.keyPressEvent(event)

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
        self.move(QtGui.QCursor.pos() - self.center)
        super(HotboxReader, self).show()
        self.set_hovered_shapes()
        self.setFocus()

    def hide(self):
        if not self.isVisible():
            return

        if self.triggering == 'click or close':
            execute_hovered_shape(self.shapes, left=True)
        if self.is_submenu is False:
            self.hideSubmenusRequested.emit()

        # the shape states for the next hotbox appearance
        for shape in self.interactive_shapes:
            shape.hovered = False
            shape.clicked = False
        # clean the aiming shape before close
        self.clear_aiming()
        super(HotboxReader, self).hide()

    def set_hovered_shapes(self):
        shapes = self.interactive_shapes
        if self.aiming is True:
            set_crossed_shapes_hovered(
                self.center, get_cursor(self), shapes, get_cursor(self))
        else:
            set_shapes_hovered(shapes, get_cursor(self), self.clicked)
        self.repaint()

    def clear_aiming(self):
        '''
        this method is a workaround because Qt seem optimize to keep a paint
        when a widget is hidden. The aiming shape have to been cleaned before
        the widget is hidden. In case of it's cleaned after, the shape can pop
        on the next hotbox opening.
        '''
        if self.aiming is False:
            return
        self.aiming = False
        self.repaint()
        self.aiming = True

def set_shapes_hovered(shapes, cursor, clicked):
    """
    this function all the given shapes.
    It set hovered the shape if his rect contains the cursor.
    """
    for shape in shapes:
        if shape.is_interactive():
            shape.set_hovered(cursor)
            shape.clicked = shape.hovered and clicked


def set_crossed_shapes_hovered(point1, point2, shapes, cursor):
    """
    this is the function to set the hovered shape using the aiming system.
    It filter all shapes crossed by the given line and set the closest to the.
    cursor hovered.
    """
    # reset hovered shape
    for shape in shapes:
        shape.hovered = False
    # check first if a shape rect contain the cursor
    for shape in shapes:
        if shape.rect.contains(cursor):
            shape.hovered = True
            return
    # filter all shapes crossed by a virtual line who joins the
    # hotspot and the cursor
    cshapes = [s for s in shapes if segment_cross_rect(point1, point2, s.rect)]
    if not cshapes:
        return
    # process distance between all shape crossed and
    # set the closest to the cursor hovered
    shapedistances = {
        distance(shape.rect.center(), cursor): shape
        for shape in cshapes}
    shapedistances[min(shapedistances.keys())].hovered = True


def execute_hovered_shape(shapes, left=False, right=False):
    for shape in shapes:
        if shape.is_interactive() and shape.hovered:
            shape.execute(left=left, right=right)
            return shape.autoclose(left=left, right=right)
    return False
