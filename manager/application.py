from PySide2 import QtWidgets, QtGui, QtCore
from hotbox_designer.widgets import BoolCombo


TRIGGERING_TYPES = 'on click', 'on close', 'both'


class HotboxManager(QtWidgets.QWidget):
    def __init__(self, context):
        super(HotboxManager, self).__init__(context.parent, QtCore.Qt.Tool)
        self.context = context
        self.table_model = HotboxTableModel(self.context.load_hotboxes())
        self.table_view = HotboxTableView()
        self.table_view.setModel(self.table_model)
        self.edit = HotboxGeneralSettingWidget()

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.table_view)
        self.layout.addWidget(self.edit)


class HotboxTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(HotboxTableView, self).__init__(parent)
        self.verticalHeader().hide()
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)


class HotboxTableModel(QtCore.QAbstractTableModel):
    HEADERS = 'name', 'shortcut'

    def __init__(self, hotboxes, parent=None):
        super(HotboxTableModel, self).__init__(parent=None)
        self.hotboxes = hotboxes

    def columnCount(self, _):
        return len(self.HEADERS)

    def rowCount(self, _):
        return len(self.hotboxes)

    def headerData(self, index, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            return
        if role == QtCore.Qt.DisplayRole:
            return self.HEADERS[index]

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self.hotboxes[row]['name']
            elif col == 1:
                text = ''
                if self.hotboxes[row]['general']['alt']:
                    text += 'alt + '
                if self.hotboxes[row]['general']['control']:
                    text += 'ctrl + '
                text += self.hotboxes[row]['general']['touch']
                return text


class HotboxGeneralSettingWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HotboxGeneralSettingWidget, self).__init__(parent)
        self.setFixedWidth(150)
        self.name = QtWidgets.QLineEdit()
        self.triggering = QtWidgets.QComboBox()
        self.triggering.addItems(TRIGGERING_TYPES)
        self.aiming = BoolCombo(False)
        self.touch = QtWidgets.QComboBox()
        self.alt = BoolCombo(False)
        self.control = BoolCombo(False)

        self.save = QtWidgets.QPushButton('save')
        self.edit = QtWidgets.QPushButton('edit')
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.addWidget(self.save)
        self.button_layout.addWidget(self.edit)

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addRow('name', self.name)
        self.layout.addRow('triggering', self.triggering)
        self.layout.addRow('aiming', self.aiming)
        self.layout.addRow('touch', self.touch)
        self.layout.addRow('alt', self.alt)
        self.layout.addRow('control', self.control)
        self.layout.addRow(self.button_layout)

    def set_hotbox(self, hotbox):
        self.name.setText(hotbox['name'])
        self.triggering.setCurrentText(hotbox['triggering'])
        self.aiming.setCurrentText(str(hotbox['aiming']))
        self.touch.setCurrentText(hotbox['touch'])
        self.alt.setCurrentText(str(hotbox['alt']))
        self.control.setCurrentText(str(hotbox['control']))
