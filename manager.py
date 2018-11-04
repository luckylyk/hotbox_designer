
from functools import partial
from PySide2 import QtWidgets, QtGui, QtCore

import hotbox_designer
from hotbox_designer.editor.application import HotboxEditor
from hotbox_designer.widgets import BoolCombo, Title
from hotbox_designer.templates import HOTBOX


PRESS_COMMAND_TEMPLATE = """import hotbox_designer
from hotbox_designer import sofwares
software = softwares.Maya()
hotbox_designer.initialize(software)
hotbox_designer.show_hotbox('{}')
"""

RELEASE_COMMAND_TEMPLATE = """import hotbox_designer
hotbox_designer.hide_hotbox('{}')
"""


def get_new_hotbox(hotboxes):
    options =  HOTBOX.copy()
    options.update({'name': get_valid_name(hotboxes)})
    return {
        'general': options,
        'shapes': []
    }

DEFAULT_NAME = 'MyHotbox_{}'
TRIGGERING_TYPES = 'on click', 'on close', 'both'


def get_valid_name(hotboxes, proposal=None):
    names = [hotbox['general']['name'] for hotbox in hotboxes]
    index = 0
    name = proposal or DEFAULT_NAME.format(str(index).zfill(2))
    while name in names:
        if proposal:
            name = proposal + "_" + str(index).zfill(2)
        else:
            name = DEFAULT_NAME.format(str(index).zfill(2))
        index += 1
    return name


class HotboxManager(QtWidgets.QWidget):
    def __init__(self, context):
        self.setWindowTitle('Hotbox Designer')
        parent = context.main_window
        super(HotboxManager, self).__init__(parent, QtCore.Qt.Tool)
        self.context = context
        self.hotbox_editor = None
        hotboxes_data = hotbox_designer.load_data(self.context.file)
        self.table_model = HotboxTableModel(hotboxes_data)
        self.table_view = HotboxTableView()
        self.table_view.set_model(self.table_model)
        self.table_view.selectedRowChanged.connect(self._selected_row_changed)

        self.add_button = QtWidgets.QPushButton('create')
        self.add_button.released.connect(self._call_create)
        self.edit_button = QtWidgets.QPushButton('edit')
        self.edit_button.released.connect(self._call_edit)
        self.remove_button = QtWidgets.QPushButton('remove')
        self.remove_button.released.connect(self._call_remove)
        self.reinitialize = QtWidgets.QPushButton('reinitialize hotboxes')
        self.reinitialize.released.connect(self._call_reinitialize)

        self.hbuttons = QtWidgets.QHBoxLayout()
        self.hbuttons.setContentsMargins(0, 0, 0, 0)
        self.hbuttons.addWidget(self.add_button)
        self.hbuttons.addWidget(self.edit_button)
        self.hbuttons.addWidget(self.remove_button)
        self.vbuttons = QtWidgets.QVBoxLayout()
        self.vbuttons.setContentsMargins(0, 0, 0, 0)
        self.vbuttons.addLayout(self.hbuttons)
        self.vbuttons.addWidget(self.reinitialize)

        self.table_layout = QtWidgets.QVBoxLayout()
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_layout.setSpacing(0)
        self.table_layout.addWidget(self.table_view)
        self.table_layout.addLayout(self.vbuttons)

        self.edit = HotboxGeneralSettingWidget()
        self.edit.optionSet.connect(self._call_option_set)
        self.edit.setEnabled(False)
        self.press_command = QtWidgets.QPushButton('show on press command')
        self.press_command.released.connect(self._call_press_command)
        self.release_command = QtWidgets.QPushButton('show on release command')
        self.release_command.released.connect(self._call_release_command)

        self.edit_layout = QtWidgets.QVBoxLayout()
        self.edit_layout.setContentsMargins(0, 0, 0, 0)
        self.edit_layout.setSpacing(0)
        self.edit_layout.addWidget(self.edit)
        self.edit_layout.addStretch(1)
        self.edit_layout.addWidget(self.press_command)
        self.edit_layout.addWidget(self.release_command)

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.addLayout(self.table_layout)
        self.hlayout.addLayout(self.edit_layout)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.hlayout)

    def get_selected_hotbox(self):
        row = self.table_view.get_selected_row()
        if row is None:
            return
        return self.table_model.hotboxes[row]

    def save_hotboxes(self, *useless):
        hotbox_designer.save_data(self.context.file, self.table_model.hotboxes)

    def _selected_row_changed(self):
        hotbox = self.get_selected_hotbox()
        if hotbox is not None:
            self.edit.set_hotbox_settings(hotbox['general'])
            self.edit.setEnabled(True)
        else:
            self.edit.setEnabled(False)

    def _call_edit(self):
        hotbox_data = self.get_selected_hotbox()
        if hotbox_data is None:
            return
        parent = self.context.main_window
        self.hotbox_editor = HotboxEditor(hotbox_data, parent=parent)
        self.hotbox_editor.set_hotbox_data(hotbox_data)
        row = self.table_view.get_selected_row()
        method = partial(self.table_model.set_hotbox, row)
        self.hotbox_editor.hotboxDataModified.connect(method)
        self.hotbox_editor.hotboxDataModified.connect(self.save_hotboxes)
        self.hotbox_editor.setWindowModality(QtCore.Qt.ApplicationModal)
        self.hotbox_editor.show()

    def _call_create(self):
        hotbox = get_new_hotbox(self.table_model.hotboxes)
        self.table_model.layoutAboutToBeChanged.emit()
        self.table_model.hotboxes.append(hotbox)
        self.table_model.layoutChanged.emit()
        self.save_hotboxes()

    def _call_remove(self):
        hotbox = self.get_selected_hotbox()
        if hotbox is None:
            return

        areyousure = QtWidgets.QMessageBox.question(
            self,
            'remove',
            'remove a hotbox is definitive, are you sure to continue',
            buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            defaultButton=QtWidgets.QMessageBox.No)

        if areyousure == QtWidgets.QMessageBox.No:
            return

        self.table_model.layoutAboutToBeChanged.emit()
        self.table_model.hotboxes.remove(hotbox)
        self.table_model.layoutChanged.emit()
        self.save_hotboxes()

    def _call_reinitialize(self):
        hotbox_designer.initialize(self.context)

    def _call_press_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return
        command = PRESS_COMMAND_TEMPLATE.format(hotbox['general']['name'])
        CommandDisplayDialog(command, self).exec_()

    def _call_release_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return
        command = RELEASE_COMMAND_TEMPLATE.format(hotbox['general']['name'])
        CommandDisplayDialog(command, self).exec_()

    def _call_option_set(self, option, value):
        self.table_model.layoutAboutToBeChanged.emit()
        hotbox = self.get_selected_hotbox()
        if option == 'name':
            value = get_valid_name(self.table_model.hotboxes, value)

        if hotbox is not None:
            hotbox['general'][option] = value
        self.table_model.layoutChanged.emit()
        self.save_hotboxes()


class HotboxTableView(QtWidgets.QTableView):
    selectedRowChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(HotboxTableView, self).__init__(parent)
        vheader = self.verticalHeader()
        vheader.hide()
        vheader.setSectionResizeMode(vheader.ResizeToContents)
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        hheader.hide()
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setShowGrid(False)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def selection_changed(self, *args):
        return self.selectedRowChanged.emit()

    def set_model(self, model):
        self.setModel(model)
        self.selection_model = self.selectionModel()
        self.selection_model.selectionChanged.connect(self.selection_changed)

    def get_selected_row(self):
        indexes = self.selection_model.selectedIndexes()
        rows = list({index.row() for index in indexes})
        if not rows:
            return None
        return rows[0]


class HotboxTableModel(QtCore.QAbstractTableModel):

    def __init__(self, hotboxes, parent=None):
        super(HotboxTableModel, self).__init__(parent=None)
        self.hotboxes = hotboxes

    def columnCount(self, _):
        return 1

    def rowCount(self, _):
        return len(self.hotboxes)

    def set_hotbox(self, row, hotbox):
        self.layoutAboutToBeChanged.emit()
        self.hotboxes[row] = hotbox

    def data(self, index, role):
        row, col = index.row(), index.column()
        hotbox = self.hotboxes[row]
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return hotbox['general']['name']


class HotboxGeneralSettingWidget(QtWidgets.QWidget):
    optionSet = QtCore.Signal(str, object)
    applyRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super(HotboxGeneralSettingWidget, self).__init__(parent)
        self.setFixedWidth(150)
        self.name = QtWidgets.QLineEdit()
        self.name.textEdited.connect(partial(self.optionSet.emit, 'name'))
        self.triggering = QtWidgets.QComboBox()
        self.triggering.addItems(TRIGGERING_TYPES)
        self.triggering.currentIndexChanged.connect(self._triggering_changed)
        self.aiming = BoolCombo(False)
        self.aiming.valueSet.connect(partial(self.optionSet.emit, 'aiming'))

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setHorizontalSpacing(5)
        self.layout.addRow(Title('Options'))
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow('name', self.name)
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow('triggering', self.triggering)
        self.layout.addRow('aiming', self.aiming)


    def _triggering_changed(self, _):
        self.optionSet.emit('triggering', self.triggering.currentText())

    def _touch_changed(self, _):
        self.optionSet.emit('touch', self.touch.text())

    def set_hotbox_settings(self, hotbox_settings):
        self.name.setText(hotbox_settings['name'])
        self.triggering.setCurrentText(hotbox_settings['triggering'])
        self.aiming.setCurrentText(str(hotbox_settings['aiming']))


class CommandDisplayDialog(QtWidgets.QDialog):
    def __init__(self, command, parent=None):
        super(CommandDisplayDialog, self).__init__(parent)
        self.setWindowTitle("Command")
        self.text = QtWidgets.QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(command)
        self.ok = QtWidgets.QPushButton('ok')
        self.ok.released.connect(self.accept)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.ok)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addLayout(self.button_layout)


class TouchEdit(QtWidgets.QLineEdit):
    def keyPressEvent(self, event):
        self.setText(QtGui.QKeySequence(event.key()).toString().lower())
        self.textEdited.emit(self.text())