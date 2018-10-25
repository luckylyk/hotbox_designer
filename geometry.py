from PySide2 import QtCore

POINT_RADIUS = 8
POINT_OFFSET = 4
DIRECTIONS = [
    'top_left',
    'bottom_left',
    'top_right',
    'bottom_right',
    'left',
    'right',
    'top',
    'bottom']


def get_topleft_rect(rect):
    if not rect:
        return None
    point = rect.topLeft()
    return QtCore.QRectF(
        point.x() - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        point.y() - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def get_bottomleft_rect(rect):
    if not rect:
        return None
    point = rect.bottomLeft()
    return QtCore.QRectF(
        point.x() - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        point.y() + (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def get_topright_rect(rect):
    if not rect:
        return None
    point = rect.topRight()
    return QtCore.QRectF(
        point.x() + (POINT_RADIUS / 2.0) - POINT_OFFSET,
        point.y() - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def get_bottomright_rect(rect):
    if not rect:
        return None
    point = rect.bottomRight()
    return QtCore.QRectF(
        point.x() + (POINT_RADIUS / 2.0) - POINT_OFFSET,
        point.y() + (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def get_left_side_rect(rect):
    if not rect:
        return None
    top = rect.top() + (rect.height() / 2.0)
    return QtCore.QRectF(
        rect.left() - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        top - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def get_right_side_rect(rect):
    if not rect:
        return None
    top = rect.top() + (rect.height() / 2.0)
    return QtCore.QRectF(
        rect.right() + (POINT_RADIUS / 2.0) - POINT_OFFSET,
        top - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def get_top_side_rect(rect):
    if not rect:
        return None
    return QtCore.QRectF(
        rect.left() + (rect.width() / 2.0),
        rect.top() - (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def get_bottom_side_rect(rect):
    if not rect:
        return None
    return QtCore.QRectF(
        rect.left() + (rect.width() / 2.0),
        rect.bottom() + (POINT_RADIUS / 2.0) - POINT_OFFSET,
        POINT_RADIUS, POINT_RADIUS)


def grow_rect(rect, value):
    if not rect:
        return None
    return QtCore.QRectF(
        rect.left() - value,
        rect.top() - value,
        rect.width() + (value * 2),
        rect.height() + (value * 2))

def relative(value, in_min, in_max, out_min, out_max):
    factor = (value - in_min) / (in_max - in_min)
    width = out_max - out_min
    return out_min + (width * (factor))


def proportional_rect(rect, percent=None):
    factor = float(percent) / 100
    width = rect.width() * factor
    height = rect.height() * factor
    left = rect.left() + round((rect.width() - width) / 2)
    top = rect.top() + round((rect.height() - height) / 2)
    return QtCore.QRect(left, top, width, height)


def resize_rect_with_reference(rect, in_reference_rect, out_reference_rect):
    left = relative(
        value=rect.left(),
        in_min=in_reference_rect.left(),
        in_max=in_reference_rect.right(),
        out_min=out_reference_rect.left(),
        out_max=out_reference_rect.right())
    top = relative(
        value=rect.top(),
        in_min=in_reference_rect.top(),
        in_max=in_reference_rect.bottom(),
        out_min=out_reference_rect.top(),
        out_max=out_reference_rect.bottom())
    right = relative(
        value=rect.right(),
        in_min=in_reference_rect.left(),
        in_max=in_reference_rect.right(),
        out_min=out_reference_rect.left(),
        out_max=out_reference_rect.right())
    bottom = relative(
        value=rect.bottom(),
        in_min=in_reference_rect.top(),
        in_max=in_reference_rect.bottom(),
        out_min=out_reference_rect.top(),
        out_max=out_reference_rect.bottom())
    rect.setCoords(left, top, right, bottom)


def resize_rect_with_direction(rect, cursor, direction, force_square=False):
    if direction == 'top_left':
        if cursor.x() < rect.right():
            if cursor.y() < rect.bottom():
                rect.setTopLeft(cursor)
                if force_square:
                    left = rect.right() - rect.height()
                    rect.setLeft(left)

    elif direction == 'bottom_left':
        if cursor.x() < rect.right():
            if cursor.y() > rect.top():
                rect.setBottomLeft(cursor)
                if force_square:
                    rect.setHeight(rect.width())

    elif direction == 'top_right':
        if cursor.x() > rect.left():
            if cursor.y() < rect.bottom():
                rect.setTopRight(cursor)
                if force_square:
                    rect.setWidth(rect.height())

    elif direction == 'bottom_right':
        if cursor.x() > rect.left():
            if cursor.y() > rect.top():
                rect.setBottomRight(cursor)
                if force_square:
                    rect.setHeight(rect.width())

    elif direction == 'left':
        if cursor.x() < rect.right():
            rect.setLeft(cursor.x())
            if force_square:
                rect.setHeight(rect.width())

    elif direction == 'right':
        if cursor.x() > rect.left():
            rect.setRight(cursor.x())
            if force_square:
                rect.setHeight(rect.width())

    elif direction == 'top':
        if cursor.y() < rect.bottom():
            rect.setTop(cursor.y())
            if force_square:
                rect.setWidth(rect.height())

    elif direction == 'bottom':
        if cursor.y() > rect.top():
            rect.setBottom(cursor.y())
            if force_square:
                rect.setWidth(rect.height())


class Transform():
    def __init__(self):
        self.snap = None
        self.direction = None
        self.rect = None
        self.mode = None
        self.square = False
        self.reference_x = None
        self.reference_y = None
        self.reference_rect = None

    def set_rect(self, rect):
        self.rect = rect
        if rect is None:
            self.reference_x = None
            self.reference_y = None
            return

    def set_reference_point(self, cursor):
        self.reference_x = cursor.x() - self.rect.left()
        self.reference_y = cursor.y() - self.rect.top()

    def resize(self, rects, cursor):
        if self.snap is not None:
            x, y = snap(cursor.x(), cursor.y(), self.snap)
            cursor.setX(x)
            cursor.setY(y)
        resize_rect_with_direction(
            self.rect, cursor, self.direction, force_square=self.square)
        self.apply_relative_transformation(rects)

    def apply_relative_transformation(self, rects):
        for rect in rects:
            resize_rect_with_reference(
                rect, self.reference_rect, self.rect)

        self.reference_rect = QtCore.QRectF(
            self.rect.topLeft(), self.rect.bottomRight())

    def move(self, rects, cursor):
        x = cursor.x() - self.reference_x
        y = cursor.y() - self.reference_y
        if self.snap is not None:
            x, y = snap(x, y, self.snap)
        width = self.rect.width()
        height = self.rect.height()
        self.rect.setTopLeft(QtCore.QPointF(x, y))
        self.rect.setWidth(width)
        self.rect.setHeight(height)
        self.apply_relative_transformation(rects)


def snap(x, y, snap):
    x = snap[0] * round(x / snap[0])
    y = snap[1] * round(y / snap[1])
    return x, y


def get_combined_rects(rects):
    if not rects:
        return None
    left = min([rect.left() for rect in rects])
    right = max([rect.right() for rect in rects])
    top = min([rect.top() for rect in rects])
    bottom = max([rect.bottom() for rect in rects])
    return QtCore.QRectF(left, top, right - left, bottom - top)