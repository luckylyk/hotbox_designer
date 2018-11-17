from PySide2 import QtCore, QtGui
from hotbox_designer.qtutils import VALIGNS, HALIGNS
from hotbox_designer.geometry import grow_rect


MANIPULATOR_BORDER = 5
SELECTION_COLOR = '#3388FF'


def draw_editor(painter, rect, snap=None):
    # draw border
    pen = QtGui.QPen(QtGui.QColor('#333333'))
    pen.setStyle(QtCore.Qt.DashDotLine)
    pen.setWidth(3)
    brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 25))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)

    if snap is None:
        return
    # draw snap grid
    pen = QtGui.QPen(QtGui.QColor('red'))
    painter.setPen(pen)
    x = 0
    y = 0
    while y < rect.bottom():
        painter.drawPoint(x, y)
        x += snap[0]
        if x > rect.right():
            x = 0
            y += snap[1]


def draw_editor_center(painter, rect, point):
    color = QtGui.QColor(200, 200, 200, 125)
    painter.setPen(QtGui.QPen(color))
    painter.setBrush(QtGui.QBrush(color))
    painter.drawRect(rect)

    path = get_center_path(QtCore.QPoint(*point))
    pen = QtGui.QPen(QtGui.QColor(50, 125, 255))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.drawPath(path)


def get_center_path(point):
    ext = 12
    int_ = 5
    path = QtGui.QPainterPath(point)
    path.moveTo(QtCore.QPoint(point.x() - ext, point.y()))
    path.lineTo(QtCore.QPoint(point.x() - int_, point.y()))
    path.moveTo(QtCore.QPoint(point.x() + int_, point.y()))
    path.lineTo(QtCore.QPoint(point.x() + ext, point.y()))
    path.moveTo(QtCore.QPoint(point.x(), point.y() - ext))
    path.lineTo(QtCore.QPoint(point.x(), point.y() - int_))
    path.moveTo(QtCore.QPoint(point.x(), point.y() + int_))
    path.lineTo(QtCore.QPoint(point.x(), point.y() + ext))
    path.addEllipse(point, 1, 1)
    return path


def draw_shape(painter, shape):
    options = shape.options
    content_rect = shape.content_rect()
    if shape.clicked:
        bordercolor = QtGui.QColor(options['bordercolor.clicked'])
        backgroundcolor = QtGui.QColor(options['bgcolor.clicked'])
        bordersize = options['borderwidth.clicked']
    elif shape.hovered:
        bordercolor = QtGui.QColor(options['bordercolor.hovered'])
        backgroundcolor = QtGui.QColor(options['bgcolor.hovered'])
        bordersize = options['borderwidth.hovered']
    else:
        bordercolor = QtGui.QColor(options['bordercolor.normal'])
        backgroundcolor = QtGui.QColor(options['bgcolor.normal'])
        bordersize = options['borderwidth.normal']
    textcolor = QtGui.QColor(options['text.color'])
    alpha = options['bordercolor.transparency'] if options['border'] else 255
    bordercolor.setAlpha(255 - alpha)
    backgroundcolor.setAlpha(255 - options['bgcolor.transparency'])

    pen = QtGui.QPen(bordercolor)
    pen.setStyle(QtCore.Qt.SolidLine)
    pen.setWidthF(bordersize)
    painter.setPen(pen)
    painter.setBrush(QtGui.QBrush(backgroundcolor))
    if options['shape'] == 'square':
        painter.drawRect(shape.rect)
    else:
        painter.drawEllipse(shape.rect)

    if shape.pixmap is not None:
        rect = shape.image_rect or content_rect
        painter.drawPixmap(rect, shape.pixmap)

    painter.setPen(QtGui.QPen(textcolor))
    painter.setBrush(QtGui.QBrush(textcolor))
    option = QtGui.QTextOption()
    flags = VALIGNS[options['text.valign']] | HALIGNS[options['text.halign']]
    option.setAlignment(flags)
    font = QtGui.QFont()
    font.setBold(options['text.bold'])
    font.setItalic(options['text.italic'])
    font.setPixelSize(options['text.size'])
    painter.setFont(font)
    text = options['text.content']
    painter.drawText(QtCore.QRectF(content_rect), flags, text)


def draw_selection_square(painter, rect):
    bordercolor = QtGui.QColor(SELECTION_COLOR)
    backgroundcolor = QtGui.QColor(SELECTION_COLOR)
    backgroundcolor.setAlpha(85)
    painter.setPen(QtGui.QPen(bordercolor))
    painter.setBrush(QtGui.QBrush(backgroundcolor))
    painter.drawRect(rect)


def draw_manipulator(painter, manipulator, cursor):
    hovered = manipulator.hovered_rects(cursor)

    if manipulator.rect in hovered:
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
        brush = QtGui.QBrush(QtGui.QColor(125, 125, 125))
        brush.setStyle(QtCore.Qt.FDiagPattern)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawPath(manipulator.hovered_path)

    pen = QtGui.QPen(QtGui.QColor('black'))
    brush = QtGui.QBrush(QtGui.QColor('white'))
    painter.setBrush(brush)
    for rect in manipulator.handler_rects():
        pen.setWidth(3 if rect in hovered else 1)
        painter.setPen(pen)
        painter.drawEllipse(rect)

    pen.setWidth(1)
    pen.setStyle(QtCore.Qt.DashLine)  # if not moving else QtCore.Qt.SolidLine)
    painter.setPen(pen)
    painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
    painter.drawRect(manipulator.rect)


def draw_aiming_background(painter, rect):
    pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 1))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)


def draw_aiming(painter, center, target):
    pen = QtGui.QPen(QtGui.QColor(35, 35, 35))
    pen.setWidth(3)
    painter.setPen(pen)
    painter.setBrush(QtGui.QColor(0, 0, 0, 0))
    painter.drawLine(center, target)


def get_hovered_path(rect):
    path = QtGui.QPainterPath()
    path.addRect(rect)
    path.addRect(grow_rect(rect, MANIPULATOR_BORDER))
    return path