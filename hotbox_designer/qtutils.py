import os
from Qt import QtGui, QtWidgets, QtCore


VALIGNS = {
    'top': QtCore.Qt.AlignTop,
    'center': QtCore.Qt.AlignVCenter,
    'bottom': QtCore.Qt.AlignBottom}
HALIGNS = {
    'left': QtCore.Qt.AlignLeft,
    'center': QtCore.Qt.AlignHCenter,
    'right': QtCore.Qt.AlignRight}
ICONDIR = os.path.dirname(__file__)


def icon(filename):
    return QtGui.QIcon(os.path.join(ICONDIR, 'resources', 'icons', filename))


def get_cursor(widget):
    return widget.mapFromGlobal(QtGui.QCursor.pos())


def set_shortcut(keysequence, parent, method):
    shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(keysequence), parent)
    shortcut.activated.connect(method)
