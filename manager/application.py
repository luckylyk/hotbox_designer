
from functools import partial
from PySide2 import QtWidgets, QtGui, QtCore
from hotbox_designer.editor.application import HotboxEditor
from hotbox_designer.widgets import BoolCombo, Title
from hotbox_designer.utils import load_hotboxes, save_hotboxes
from hotbox_designer.templates import get_new_hotbox


TRIGGERING_TYPES = 'on click', 'on close', 'both'

PRESS_COMMAND_TEMPLATE = """
import hotbox_designer
hotbox_designer.initialize(filename)
hotbox_designer.show_hotbox('{}')
"""

RELEASE_COMMAND_TEMPLATE = """
import hotbox_designer
hotbox_designer.hide_hotbox('{}')
"""

def generate_commands(name):
    return (
        PRESS_COMMAND_TEMPLATE.format(name),
        RELEASE_COMMAND_TEMPLATE.format(name))


class HotboxManager(QtWidgets.QWidget):
    def __init__(self, context):
        super(HotboxManager, self).__init__(context.parent, QtCore.Qt.Tool)
        self.context = context
        self.hotbox_editor = None
        hotboxes = load_hotboxes(self.context.file)
        self.table_model = HotboxTableModel(context, hotboxes)
        self.table_view = HotboxTableView()
        self.table_view.set_model(self.table_model)
        self.table_view.selectedRowChanged.connect(self._selected_row_changed)

        self.add_button = QtWidgets.QPushButton('create')
        self.add_button.released.connect(self._call_create)
        self.edit_button = QtWidgets.QPushButton('edit')
        self.edit_button.released.connect(self._call_edit)
        self.remove_button = QtWidgets.QPushButton('remove')
        self.remove_button.released.connect(self._call_remove)
        self.buttons = QtWidgets.QHBoxLayout()
        self.buttons.setContentsMargins(0, 0, 0, 0)
        self.buttons.addWidget(self.add_button)
        self.buttons.addWidget(self.edit_button)
        self.buttons.addWidget(self.remove_button)
        self.table_layout = QtWidgets.QVBoxLayout()
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_layout.setSpacing(0)
        self.table_layout.addWidget(self.table_view)
        self.table_layout.addLayout(self.buttons)

        self.edit = HotboxGeneralSettingWidget()
        self.edit.optionSet.connect(self._call_option_set)
        self.edit.applyRequested.connect(self._call_apply_hotbox)
        self.edit.setEnabled(False)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addLayout(self.table_layout)
        self.layout.addWidget(self.edit)

    def get_selected_hotbox(self):
        row = self.table_view.get_selected_row()
        if row is None:
            return
        return self.table_model.hotboxes[row]

    def save_hotboxes(self, *useless):
        save_hotboxes(self.context.file, self.table_model.hotboxes)

    def _selected_row_changed(self):
        hotbox = self.get_selected_hotbox()
        if hotbox is not None:
            self.edit.set_hotbox_settings(hotbox['general'])
            self.edit.setEnabled(True)
        else:
            self.edit.setEnabled(False)

    def _call_apply_hotbox(self):
        hotbox_data = self.get_selected_hotbox()
        press_command, release_command = generate_commands(hotbox_data)
        self.context.activate_hotbox_in_software(
            hotbox_data, press_command, release_command)

    def _call_edit(self):
        hotbox_data = self.get_selected_hotbox()
        if hotbox_data is None:
            return
        self.hotbox_editor = HotboxEditor(hotbox_data, parent=self.context.get_parent())
        self.hotbox_editor.set_hotbox_data(hotbox_data)
        row = self.table_view.get_selected_row()
        method = partial(self.table_model.set_hotbox, row)
        self.hotbox_editor.hotboxDataModified.connect(method)
        self.hotbox_editor.hotboxDataModified.connect(self.save_hotboxes)
        self.hotbox_editor.setWindowModality(QtCore.Qt.ApplicationModal)
        self.hotbox_editor.show()

    def _call_create(self):
        self.table_model.layoutAboutToBeChanged.emit()
        self.table_model.hotboxes.append(get_new_hotbox())
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

    def _call_option_set(self, option, value):
        self.table_model.layoutAboutToBeChanged.emit()
        hotbox = self.get_selected_hotbox()
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
    HEADERS = 'name', 'shortcut'

    def __init__(self, context, hotboxes, parent=None):
        super(HotboxTableModel, self).__init__(parent=None)
        self.hotboxes = hotboxes
        self.context = context

    def columnCount(self, _):
        return len(self.HEADERS)

    def rowCount(self, _):
        return len(self.hotboxes)

    def headerData(self, index, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            return
        if role == QtCore.Qt.DisplayRole:
            return self.HEADERS[index]

    def set_hotbox(self, row, hotbox):
        self.layoutAboutToBeChanged.emit()
        self.hotboxes[row] = hotbox

    def data(self, index, role):
        row, col = index.row(), index.column()
        hotbox = self.hotboxes[row]
        if role == QtCore.Qt.BackgroundRole:
            if not self.context.is_active_in_software(hotbox):
                return QtGui.QColor(255, 0, 0, 25)
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return hotbox['general']['name']
            elif col == 1:
                return get_keysequance_displayname(hotbox)


def get_keysequance_displayname(hotbox):
    text = ''
    if hotbox['general']['alt']:
        text += 'alt + '
    if hotbox['general']['control']:
        text += 'ctrl + '
    text += hotbox['general']['touch']
    return text


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
        self.touch = TouchEdit()
        self.touch.textEdited.connect(self._touch_changed)
        self.alt = BoolCombo(False)
        self.alt.valueSet.connect(partial(self.optionSet.emit, 'alt'))
        self.control = BoolCombo(False)
        self.control.valueSet.connect(partial(self.optionSet.emit, 'control'))
        self.apply = QtWidgets.QPushButton('apply')
        self.apply.released.connect(self.applyRequested.emit)

        self.flayout = QtWidgets.QFormLayout()
        self.flayout.setContentsMargins(0, 0, 0, 0)
        self.flayout.setSpacing(0)
        self.flayout.setHorizontalSpacing(5)
        self.flayout.addRow(Title('Options'))
        self.flayout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.flayout.addRow('name', self.name)
        self.flayout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.flayout.addRow('triggering', self.triggering)
        self.flayout.addRow('aiming', self.aiming)
        self.flayout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.flayout.addRow('touch', self.touch)
        self.flayout.addRow('alt', self.alt)
        self.flayout.addRow('control', self.control)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.flayout)
        self.layout.addStretch(1)
        self.layout.addWidget(self.apply)

    def _triggering_changed(self, _):
        self.optionSet.emit('triggering', self.triggering.currentText())

    def _touch_changed(self, _):
        self.optionSet.emit('touch', self.touch.text())

    def set_hotbox_settings(self, hotbox_settings):
        self.name.setText(hotbox_settings['name'])
        self.triggering.setCurrentText(hotbox_settings['triggering'])
        self.aiming.setCurrentText(str(hotbox_settings['aiming']))
        self.touch.setText(hotbox_settings['touch'])
        self.alt.setCurrentText(str(hotbox_settings['alt']))
        self.control.setCurrentText(str(hotbox_settings['control']))


class TouchEdit(QtWidgets.QLineEdit):
    def keyPressEvent(self, event):
        self.setText(QtGui.QKeySequence(event.key()).toString().lower())
        self.textEdited.emit(self.text())