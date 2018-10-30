from PySide2 import QtWidgets, QtCore, QtGui
from hotbox_designer.interactive import Shape, get_shape_rect_from_options
from hotbox_designer.painting import draw_shape
from hotbox_designer.geometry import proportional_rect
from hotbox_designer.convert import VALIGNS, HALIGNS
from hotbox_designer.utils import get_cursor


TEST = {
    'general': {'control': False, 'centerx': 570, 'triggering': 'click', 'height': 600, 'name': '', 'width': 900, 'aiming': False, 'centery': 210, 'alt': False, 'touch': ''},
    'shapes': [
        {'bordercolor.clicked': '#red', 'action.left.close': False, 'shape.left': 140.0, 'text.size': 12, 'shape.width': 300.0, 'image.height': 32, 'bordercolor.hovered': '#888888', 
        'image.fit': False, 'shape': 'square', 'bgcolor.normal': '#888888', 'text.halign': 'center', 'text.valign': 'center', 'borderwidth.clicked': 0, 'text.color': '#FFFFFF', 
        'bgcolor.transparency': 0, 'bordercolor.normal': '#888888', 'action.right.language': 'python', 'text.bold': False, 'image.path': '', 'shape.top': 40.0, 
        'action.right.close': False, 'shape.height': 20.0, 'image.width': 32, 'bordercolor.transparency': 0, 'bgcolor.hovered': '#888888', 'borderwidth.normal': 0, 
        'text.italic': False, 'action.left': False, 'borderwidth.hovered': 0, 'text.content': '', 'action.right': False, 'action.left.command': '', 'action.left.language': 
        'python', 'bgcolor.clicked': '#888888', 'action.right.command': '', 'border': False},
        {'bordercolor.clicked': '#888888', 'action.left.close': False, 'shape.left': 140.0, 'text.size': 12, 'shape.width': 300.0, 'image.height': 32, 'bordercolor.hovered': '#888888',
        'image.fit': False, 'shape': 'square', 'bgcolor.normal': '#888888', 'text.halign': 'center', 'text.valign': 'center', 'borderwidth.clicked': 0, 'text.color': '#FFFFFF',
        'bgcolor.transparency': 125.0, 'bordercolor.normal': '#888888', 'action.right.language': 'python', 'text.bold': False, 'image.path': '', 'shape.top': 40.0,
        'action.right.close': False, 'shape.height': 100.0, 'image.width': 32, 'bordercolor.transparency': 125.0, 'bgcolor.hovered': '#888888', 'borderwidth.normal': 0,
        'text.italic': False, 'action.left': False, 'borderwidth.hovered': 0, 'text.content': '', 'action.right': False, 'action.left.command': '',
        'action.left.language': 'python', 'bgcolor.clicked': '#888888', 'action.right.command': '', 'border': False},
        {'bordercolor.clicked': '#FFFFFF', 'action.left.close': False, 'shape.left': 160.0, 'text.size': 12, 'shape.width': 120.0, 'image.height': 32, 'bordercolor.hovered': '#393939',
        'image.fit': True, 'shape': 'square', 'bgcolor.normal': '#888888', 'text.halign': 'center', 'text.valign': 'center', 'borderwidth.clicked': 2, 'text.color': '#FFFFFF',
        'bgcolor.transparency': 0, 'bordercolor.normal': '#000000', 'action.right.language': 'python', 'text.bold': False, 'image.path': '',
        'shape.top': 100.0, 'action.right.close': False, 'shape.height': 30.0, 'image.width': 32, 'bordercolor.transparency': 0, 'bgcolor.hovered': '#AAAAAA',
        'borderwidth.normal': 1.0, 'text.italic': False, 'action.left': True, 'borderwidth.hovered': 1.25, 'text.content': 'ok', 'action.right': True, 'action.left.command': 'print(\'left\')',
        'action.left.language': 'python', 'bgcolor.clicked': '#DDDDDD', 'action.right.command': 'print(\'right\')', 'border': True},
        {'bordercolor.clicked': '#FFFFFF', 'action.left.close': False,
        'shape.left': 290.0, 'text.size': 12, 'shape.width': 130.0, 'image.height': 32, 'bordercolor.hovered': '#393939', 'image.fit': True, 'shape': 'square',
        'bgcolor.normal': '#888888', 'text.halign': 'center', 'text.valign': 'center', 'borderwidth.clicked': 2, 'text.color': '#FFFFFF', 'bgcolor.transparency': 0,
        'bordercolor.normal': '#000000', 'action.right.language': 'python', 'text.bold': False, 'image.path': '', 'shape.top': 100.0, 'action.right.close': False,
        'shape.height': 30.0, 'image.width': 32, 'bordercolor.transparency': 0, 'bgcolor.hovered': '#AAAAAA', 'borderwidth.normal': 1.0, 'text.italic': False,
        'action.left': True, 'borderwidth.hovered': 1.25, 'text.content': 'cancel', 'action.right': False, 'action.left.command': '', 'action.left.language': 'python',
        'bgcolor.clicked': '#DDDDDD', 'action.right.command': '', 'border': True},
        {'bordercolor.clicked': '#FFFFFF', 'action.left.close': False, 'shape.left': 150.0,
        'text.size': 16, 'shape.width': 200.0, 'image.height': 32, 'bordercolor.hovered': '#393939', 'image.fit': False, 'shape': 'square', 'bgcolor.normal': '#888888',
        'text.halign': 'left', 'text.valign': 'top', 'borderwidth.clicked': 0, 'text.color': '#FFFFFF', 'bgcolor.transparency': 255, 'bordercolor.normal': '#000000',
        'action.right.language': 'python', 'text.bold': True, 'image.path': '', 'shape.top': 40.0, 'action.right.close': False, 'shape.height': 50.0, 'image.width': 32,
        'bordercolor.transparency': 0, 'bgcolor.hovered': '#AAAAAA', 'borderwidth.normal': 0, 'text.italic': False, 'action.left': False, 'borderwidth.hovered': 0,
        'text.content': 'okina kurino', 'action.right': False, 'action.left.command': '', 'action.left.language': 'python', 'bgcolor.clicked': '#DDDDDD',
        'action.right.command': '', 'border': False},
        {'bordercolor.clicked': '#FFFFFF', 'action.left.close': False, 'shape.left': 170.0, 'text.size': 16,
        'shape.width': 230.0, 'image.height': 32, 'bordercolor.hovered': '#393939', 'image.fit': False, 'shape': 'square', 'bgcolor.normal': '#888888',
        'text.halign': 'left', 'text.valign': 'top', 'borderwidth.clicked': 0, 'text.color': 'black', 'bgcolor.transparency': 255, 'bordercolor.normal': '#000000',
        'action.right.language': 'python', 'text.bold': False, 'image.path': '', 'shape.top': 70.0, 'action.right.close': False, 'shape.height': 20.0, 'image.width': 32,
        'bordercolor.transparency': 0, 'bgcolor.hovered': '#AAAAAA', 'borderwidth.normal': 0, 'text.italic': False, 'action.left': False, 'borderwidth.hovered': 0,
        'text.content': 'kinoshidadae', 'action.right': False, 'action.left.command': '', 'action.left.language': 'python',
        'bgcolor.clicked': '#DDDDDD', 'action.right.command': '', 'border': False}]}
# TEST = {
#     'shapes': 
#     [        {'shape.width': 120.0, 'text.content': 'Button', 'text.valign': 'center', 'shape.top': 286.5, 'border': True, 'image.height': 32, 'action.left': True, 'bordercolor.clicked': '#FFFFFF', 'borderwidth.normal': 1.0, 'action.right.close': False, 'bordercolor.hovered': '#393939', 'shape.height': 25.0, 'bgcolor.transparency': 0, 'image.path': '', 'text.bold': False, 'shape': 'square', 'action.left.language': 'python', 'action.left.command': '', 'action.right': False, 'action.right.language': 'python', 'bgcolor.normal': '#888888', 'text.italic': False, 'bgcolor.clicked': '#DDDDDD', 'bordercolor.normal': '#000000', 'text.color': '#FFFFFF', 'borderwidth.clicked': 2, 'image.width': 32, 'bordercolor.transparency': 0, 'action.right.command': '', 'image.fit': True, 'text.halign': 'center', 'action.left.close': False, 'shape.left': 389.0, 'borderwidth.hovered': 1.25, 'text.size': 12, 'bgcolor.hovered': '#AAAAAA'}],
#         'general': {'alt': False, 'triggering': 'click', 'height': 600, 'control': False, 'name': '', 'centerx': 450, 'aiming': False, 'centery': 300, 'width': 900, 'touch': ''}}


class HotboxReader(QtWidgets.QWidget):
    def __init__(self, hotbox_data, parent=None):
        super(HotboxReader, self).__init__(parent, QtCore.Qt.Window)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        settings = hotbox_data['general']
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

    def mouseReleaseEvent(self, event):
        for shape in self.shapes:
            if shape.is_interactive() and shape.hovered:
                shape.execute(left=self.left_clicked, right=self.right_clicked)
                close = shape.autoclose(
                    left=self.left_clicked, right=self.right_clicked)
                break
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


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = HotboxReader(TEST)
    window.show()
    app.exec_()