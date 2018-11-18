
import json
import os
from functools import partial
from PySide2 import QtWidgets, QtCore

import hotbox_designer
from hotbox_designer import commands
from hotbox_designer.editor.application import HotboxEditor
from hotbox_designer.widgets import BoolCombo, Title
from hotbox_designer.qtutils import icon
from hotbox_designer.data import (
    get_new_hotbox, get_valid_name, TRIGGERING_TYPES, save_hotboxes_datas,
    copy_hotbox_data, ensure_old_data_compatible, load_hotboxes_datas,
    load_templates)


def import_hotbox():
    filenames = QtWidgets.QFileDialog.getOpenFileName(
        None, caption='Import hotbox', directory=os.path.expanduser("~"),
        filter='*.json')
    if not filenames:
        return
    with open(filenames[0], 'r') as f:
        return ensure_old_data_compatible(json.load(f))


def export_hotbox(hotbox):
    filenames = QtWidgets.QFileDialog.getSaveFileName(
        None, caption='Export hotbox', directory=os.path.expanduser("~"),
        filter='*.json')
    filename = filenames[0]
    if not filename:
        return
    if not filename.lower().endswith('.json'):
        filename += '.json'
    with open(filename, 'w') as f:
        json.dump(hotbox, f)


class HotboxManager(QtWidgets.QWidget):
    def __init__(self, software):
        parent = software.main_window
        super(HotboxManager, self).__init__(parent, QtCore.Qt.Tool)
        self.setWindowTitle('Hotbox Designer')
        self.software = software
        self.hotbox_editor = None
        hotboxes_data = load_hotboxes_datas(self.software.file)
        self.table_model = HotboxTableModel(hotboxes_data)
        self.table_view = HotboxTableView()
        self.table_view.set_model(self.table_model)
        self.table_view.selectedRowChanged.connect(self._selected_row_changed)

        self.toolbar = HotboxManagerToolbar()
        self.toolbar.newRequested.connect(self._call_create)
        self.toolbar.editRequested.connect(self._call_edit)
        self.toolbar.deleteRequested.connect(self._call_remove)
        self.toolbar.importRequested.connect(self._call_import)
        self.toolbar.exportRequested.connect(self._call_export)
        self.toolbar.reloadRequested.connect(self._call_reload)

        self.edit = HotboxGeneralSettingWidget()
        self.edit.optionSet.connect(self._call_option_set)
        self.edit.setEnabled(False)
        self.edit.open_command.released.connect(self._call_open_command)
        self.edit.close_command.released.connect(self._call_close_command)
        self.edit.switch_command.released.connect(self._call_switch_command)

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.setContentsMargins(8, 0, 8, 8)
        self.hlayout.setSpacing(4)
        self.hlayout.addWidget(self.table_view)
        self.hlayout.addWidget(self.edit)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.toolbar)
        self.layout.addLayout(self.hlayout)

    def get_selected_hotbox(self):
        row = self.table_view.get_selected_row()
        if row is None:
            return
        return self.table_model.hotboxes[row]

    def save_hotboxes(self, *_):
        save_hotboxes_datas(self.software.file, self.table_model.hotboxes)

    def _selected_row_changed(self):
        hotbox = self.get_selected_hotbox()
        if hotbox is not None:
            self.edit.set_hotbox_settings(hotbox['general'])
            self.edit.setEnabled(True)
        else:
            self.edit.setEnabled(False)

    def _call_open_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return
        command = commands.OPEN_COMMAND.format(
            software=self.software.name,
            name=hotbox['general']['name'])
        CommandDisplayDialog(command, self).exec_()

    def _call_close_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return
        command = commands.CLOSE_COMMAND.format(name=hotbox['general']['name'])
        CommandDisplayDialog(command, self).exec_()

    def _call_switch_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return
        command = commands.SWITCH_COMMAND.format(
            software=self.software.name,
            name=hotbox['general']['name'])
        CommandDisplayDialog(command, self).exec_()

    def _call_edit(self):
        if self.hotbox_editor is not None:
            self.hotbox_editor.close()
        hotbox_data = self.get_selected_hotbox()
        if hotbox_data is None:
            return
        parent = self.software.main_window
        self.hotbox_editor = HotboxEditor(
            hotbox_data, self.software, parent=parent)
        self.hotbox_editor.set_hotbox_data(hotbox_data, reset_stacks=True)
        row = self.table_view.get_selected_row()
        method = partial(self.table_model.set_hotbox, row)
        self.hotbox_editor.hotboxDataModified.connect(method)
        self.hotbox_editor.hotboxDataModified.connect(self.save_hotboxes)
        self.hotbox_editor.show()

    def _call_create(self):
        dialog = CreateHotboxDialog(self.table_model.hotboxes, self)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Rejected:
            return

        self.table_model.layoutAboutToBeChanged.emit()
        self.table_model.hotboxes.append(dialog.hotbox())
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

    def _call_reload(self):
        hotbox_designer.load_hotboxes(self.software)

    def _call_option_set(self, option, value):
        self.table_model.layoutAboutToBeChanged.emit()
        hotbox = self.get_selected_hotbox()
        if option == 'name':
            value = get_valid_name(self.table_model.hotboxes, value)

        if hotbox is not None:
            hotbox['general'][option] = value
        self.table_model.layoutChanged.emit()
        self.save_hotboxes()

    def _call_export(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return
        export_hotbox(hotbox)

    def _call_import(self):
        hotbox = import_hotbox()
        if not hotbox:
            pass
        hotboxes = self.table_model.hotboxes
        name = get_valid_name(hotboxes, hotbox['general']['name'])
        hotbox['general']['name'] = name

        self.table_model.layoutAboutToBeChanged.emit()
        self.table_model.hotboxes.append(hotbox)
        self.table_model.layoutChanged.emit()
        self.save_hotboxes()


class HotboxManagerToolbar(QtWidgets.QToolBar):
    newRequested = QtCore.Signal()
    editRequested = QtCore.Signal()
    deleteRequested = QtCore.Signal()
    importRequested = QtCore.Signal()
    exportRequested = QtCore.Signal()
    reloadRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super(HotboxManagerToolbar, self).__init__(parent)
        self.setIconSize(QtCore.QSize(24, 24))
        self.new = QtWidgets.QAction(icon('manager-new.png'), '', self)
        self.new.setToolTip('Create new hotbox')
        self.new.triggered.connect(self.newRequested.emit)
        self.edit = QtWidgets.QAction(icon('manager-edit.png'), '', self)
        self.edit.setToolTip('Edit hotbox')
        self.edit.triggered.connect(self.editRequested.emit)
        self.delete = QtWidgets.QAction(icon('manager-delete.png'), '', self)
        self.delete.setToolTip('Delete hotbox')
        self.delete.triggered.connect(self.deleteRequested.emit)
        self.import_ = QtWidgets.QAction(icon('manager-import.png'), '', self)
        self.import_.setToolTip('Import hotbox')
        self.import_.triggered.connect(self.importRequested.emit)
        self.export = QtWidgets.QAction(icon('manager-export.png'), '', self)
        self.export.setToolTip('Export hotbox')
        self.export.triggered.connect(self.exportRequested.emit)
        self.reload = QtWidgets.QAction(icon('reload.png'), '', self)
        self.reload.setToolTip('Reload hotboxes')
        self.reload.triggered.connect(self.reloadRequested.emit)

        self.addAction(self.new)
        self.addAction(self.edit)
        self.addAction(self.delete)
        self.addSeparator()
        self.addAction(self.import_)
        self.addAction(self.export)
        self.addSeparator()
        self.addAction(self.reload)


class HotboxTableView(QtWidgets.QTableView):
    selectedRowChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(HotboxTableView, self).__init__(parent)
        self.selection_model = None
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

    def selection_changed(self, *_):
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
        super(HotboxTableModel, self).__init__(parent=parent)
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
        self.submenu = BoolCombo(False)
        self.submenu.valueSet.connect(partial(self.optionSet.emit, 'submenu'))
        self.triggering = QtWidgets.QComboBox()
        self.triggering.addItems(TRIGGERING_TYPES)
        self.triggering.currentIndexChanged.connect(self._triggering_changed)
        self.aiming = BoolCombo(False)
        self.aiming.valueSet.connect(partial(self.optionSet.emit, 'aiming'))

        self.open_command = QtWidgets.QPushButton('show')
        self.close_command = QtWidgets.QPushButton('hide')
        self.switch_command = QtWidgets.QPushButton('switch')

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setHorizontalSpacing(5)
        self.layout.addRow(Title('Options'))
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow('name', self.name)
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow('is submenu', self.submenu)
        self.layout.addRow('triggering', self.triggering)
        self.layout.addRow('aiming', self.aiming)
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow(Title('Display commands'))
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow(self.open_command)
        self.layout.addRow(self.close_command)
        self.layout.addRow(self.switch_command)

    def _triggering_changed(self, _):
        self.optionSet.emit('triggering', self.triggering.currentText())

    def _touch_changed(self, _):
        self.optionSet.emit('touch', self.touch.text())

    def set_hotbox_settings(self, hotbox_settings):
        self.submenu.setCurrentText(str(hotbox_settings['submenu']))
        self.name.setText(hotbox_settings['name'])
        self.triggering.setCurrentText(hotbox_settings['triggering'])
        self.aiming.setCurrentText(str(hotbox_settings['aiming']))


class CreateHotboxDialog(QtWidgets.QDialog):
    def __init__(self, hotboxes, parent=None):
        super(CreateHotboxDialog, self).__init__(parent)
        self.setWindowTitle("Create new hotbox")
        self.hotboxes = hotboxes

        self.new = QtWidgets.QRadioButton("empty hotbox")
        self.duplicate = QtWidgets.QRadioButton("duplicate existing hotbox")
        self.duplicate.setEnabled(bool(self.hotboxes))
        self.template = QtWidgets.QRadioButton("from template")
        self.groupbutton = QtWidgets.QButtonGroup()
        self.groupbutton.addButton(self.new, 0)
        self.groupbutton.addButton(self.duplicate, 1)
        self.groupbutton.addButton(self.template, 2)
        self.new.setChecked(True)

        self.existing = QtWidgets.QComboBox()
        self.existing.addItems([hb['general']['name'] for hb in self.hotboxes])
        self.template_combo = QtWidgets.QComboBox()
        items = [hb['general']['name'] for hb in load_templates()]
        self.template_combo.addItems(items)

        self.up_layout = QtWidgets.QGridLayout()
        self.up_layout.setContentsMargins(0, 0, 0, 0)
        self.up_layout.setSpacing(0)
        self.up_layout.addWidget(self.new, 0, 0)
        self.up_layout.addWidget(self.duplicate, 1, 0)
        self.up_layout.addWidget(self.existing, 1, 1)
        self.up_layout.addWidget(self.template, 2, 0)
        self.up_layout.addWidget(self.template_combo, 2, 1)

        self.ok = QtWidgets.QPushButton('ok')
        self.ok.released.connect(self.accept)
        self.cancel = QtWidgets.QPushButton('cancel')
        self.cancel.released.connect(self.reject)

        self.down_layout = QtWidgets.QHBoxLayout()
        self.down_layout.setContentsMargins(0, 0, 0, 0)
        self.down_layout.addStretch(1)
        self.down_layout.addWidget(self.ok)
        self.down_layout.addWidget(self.cancel)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(12)
        self.layout.addLayout(self.up_layout)
        self.layout.addLayout(self.down_layout)

    def hotbox(self):
        if self.groupbutton.checkedId() == 0:
            return get_new_hotbox(self.hotboxes)
        elif self.groupbutton.checkedId() == 1:
            name = self.existing.currentText()
            hotboxes = self.hotboxes
        elif self.groupbutton.checkedId() == 2:
            name = self.template_combo.currentText()
            hotboxes = load_templates()
        hotbox = [hb for hb in hotboxes if hb['general']['name'] == name][0]
        hotbox = copy_hotbox_data(hotbox)
        name = get_valid_name(hotboxes, hotbox['general']['name'])
        hotbox['general']['name'] = name
        return hotbox


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
