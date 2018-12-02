
import json
import os
from functools import partial
from PySide2 import QtWidgets, QtCore

import hotbox_designer
from hotbox_designer.commands import OPEN_COMMAND, CLOSE_COMMAND, SWITCH_COMMAND
from hotbox_designer.designer.application import HotboxEditor
from hotbox_designer.widgets import BoolCombo, Title, CommandButton
from hotbox_designer.qtutils import icon
from hotbox_designer.dialog import (
    import_hotbox, export_hotbox, import_hotbox_link, CreateHotboxDialog,
    CommandDisplayDialog, HotkeySetter, warning)
from hotbox_designer.data import (
    get_valid_name, TRIGGERING_TYPES, save_datas, load_hotboxes_datas,
    hotbox_data_to_html, load_json)


class HotboxManager(QtWidgets.QWidget):
    def __init__(self, application):
        parent = application.main_window
        super(HotboxManager, self).__init__(parent, QtCore.Qt.Tool)
        self.setWindowTitle('Hotbox Designer')
        self.application = application
        self.hotbox_designer = None

        hotboxes_data = load_hotboxes_datas(self.application.local_file)
        self.personnal_model = HotboxPersonalTableModel(hotboxes_data)
        self.personnal_view = HotboxTableView()
        self.personnal_view.set_model(self.personnal_model)
        method = self._personnal_selected_row_changed
        self.personnal_view.selectedRowChanged.connect(method)

        self.toolbar = HotboxManagerToolbar()
        self.toolbar.reload.setEnabled(False)
        self.toolbar.link.setEnabled(False)
        self.toolbar.unlink.setEnabled(False)
        self.toolbar.newRequested.connect(self._call_create)
        self.toolbar.linkRequested.connect(self._call_add_link)
        self.toolbar.unlinkRequested.connect(self._call_unlink)
        self.toolbar.editRequested.connect(self._call_edit)
        self.toolbar.deleteRequested.connect(self._call_remove)
        self.toolbar.importRequested.connect(self._call_import)
        self.toolbar.exportRequested.connect(self._call_export)
        self.toolbar.reloadRequested.connect(self._call_reload)
        self.toolbar.setHotkeyRequested.connect(self._call_set_hotkey)
        setter_enabled = bool(application.available_set_hotkey_modes)
        self.toolbar.hotkeyset.setEnabled(setter_enabled)

        self.edit = HotboxGeneralSettingWidget()
        self.edit.optionSet.connect(self._call_option_set)
        self.edit.setEnabled(False)
        self.edit.open_command.released.connect(self._call_open_command)
        method = self._call_play_open_command
        self.edit.open_command.playReleased.connect(method)
        self.edit.close_command.released.connect(self._call_close_command)
        method = self._call_play_close_command
        self.edit.close_command.playReleased.connect(method)
        self.edit.switch_command.released.connect(self._call_switch_command)
        method = self._call_play_switch_command
        self.edit.switch_command.playReleased.connect(method)

        self.personnal = QtWidgets.QWidget()
        self.hlayout = QtWidgets.QHBoxLayout(self.personnal)
        self.hlayout.setContentsMargins(8, 0, 8, 8)
        self.hlayout.setSpacing(4)
        self.hlayout.addWidget(self.personnal_view)
        self.hlayout.addWidget(self.edit)

        links = load_json(application.shared_file, default=[])
        self.shared_model = HotboxSharedTableModel(links)
        self.shared_view = HotboxTableView()
        self.shared_view.set_model(self.shared_model)
        method = self._shared_selected_row_changed
        self.shared_view.selectedRowChanged.connect(method)

        self.infos = HotboxGeneralInfosWidget()
        self.infos.setEnabled(False)
        self.infos.open_command.released.connect(self._call_open_command)
        method = self._call_play_open_command
        self.infos.open_command.playReleased.connect(method)
        self.infos.close_command.released.connect(self._call_close_command)
        method = self._call_play_close_command
        self.infos.close_command.playReleased.connect(method)
        self.infos.switch_command.released.connect(self._call_switch_command)
        method = self._call_play_switch_command
        self.infos.switch_command.playReleased.connect(method)

        self.shared = QtWidgets.QWidget()
        self.hlayout2 = QtWidgets.QHBoxLayout(self.shared)
        self.hlayout2.setContentsMargins(8, 0, 8, 8)
        self.hlayout2.setSpacing(4)
        self.hlayout2.addWidget(self.shared_view)
        self.hlayout2.addWidget(self.infos)

        self.tabwidget = QtWidgets.QTabWidget()
        self.tabwidget.addTab(self.personnal, "Personal")
        self.tabwidget.addTab(self.shared, "Shared")
        self.tabwidget.currentChanged.connect(self.tab_index_changed)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.tabwidget)

    def get_selected_hotbox(self):
        index = self.tabwidget.currentIndex()
        table = self.shared_view if index else self.personnal_view
        model = self.shared_model if index else self.personnal_model
        row = table.get_selected_row()
        if row is None:
            return
        return model.hotboxes[row]

    def save_hotboxes(self, *_):
        save_datas(self.application.local_file, self.personnal_model.hotboxes)
        datas = self.shared_model.hotboxes_links
        save_datas(self.application.shared_file, datas)

    def _personnal_selected_row_changed(self):
        hotbox = self.get_selected_hotbox()
        if hotbox is not None:
            self.edit.set_hotbox_settings(hotbox['general'])
            self.edit.setEnabled(True)
        else:
            self.edit.setEnabled(False)

    def tab_index_changed(self):
        index = self.tabwidget.currentIndex()
        self.toolbar.edit.setEnabled(index == 0)
        self.toolbar.delete.setEnabled(index == 0)
        self.toolbar.link.setEnabled(index == 1)
        self.toolbar.unlink.setEnabled(index == 1)

    def hotbox_data_modified(self, hotbox_data):
        row = self.personnal_view.get_selected_row()
        self.personnal_model.set_hotbox(row, hotbox_data)
        self.toolbar.reload.setEnabled(True)
        self.save_hotboxes()

    def _shared_selected_row_changed(self):
        index = self.shared_view.get_selected_row()
        hotbox = self.shared_model.hotboxes[index]
        if hotbox is not None:
            self.infos.set_hotbox_data(hotbox)
            self.infos.setEnabled(True)
        else:
            self.infos.setEnabled(False)

    def _get_open_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return warning('Hotbox designer', 'No hotbox selected')
        return OPEN_COMMAND.format(
            application=self.application.name,
            name=hotbox['general']['name'])

    def _call_open_command(self):
        CommandDisplayDialog(self._get_open_command(), self).exec_()

    def _call_play_open_command(self):
        exec(self._get_open_command())

    def _get_close_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return warning('Hotbox designer', 'No hotbox selected')
        return CLOSE_COMMAND.format(name=hotbox['general']['name'])

    def _call_close_command(self):
        CommandDisplayDialog(self._get_close_command(), self).exec_()

    def _call_play_close_command(self):
        exec(self._get_close_command())

    def _get_switch_command(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return warning('Hotbox designer', 'No hotbox selected')
        return SWITCH_COMMAND.format(
            application=self.application.name,
            name=hotbox['general']['name'])

    def _call_switch_command(self):
        CommandDisplayDialog(self._get_switch_command(), self).exec_()

    def _call_play_switch_command(self):
        exec(self._get_switch_command())

    def _call_edit(self):
        if self.tabwidget.currentIndex():
            return

        hotbox_data = self.get_selected_hotbox()
        if hotbox_data is None:
            return warning('Hotbox designer', 'No hotbox selected')

        if self.hotbox_designer is not None:
            self.hotbox_designer.close()

        self.hotbox_designer = HotboxEditor(
            hotbox_data,
            self.application,
            parent=self.application.main_window)
        method = self.hotbox_data_modified
        self.hotbox_designer.hotboxDataModified.connect(method)
        self.hotbox_designer.set_hotbox_data(hotbox_data, reset_stacks=True)
        self.hotbox_designer.show()

    def _call_create(self):
        hotboxes = self.personnal_model.hotboxes + self.shared_model.hotboxes
        dialog = CreateHotboxDialog(hotboxes, self)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Rejected:
            return

        self.personnal_model.layoutAboutToBeChanged.emit()
        self.personnal_model.hotboxes.append(dialog.hotbox())
        self.personnal_model.layoutChanged.emit()
        self.save_hotboxes()
        self.toolbar.reload.setEnabled(True)

    def _call_add_link(self):
        filename = import_hotbox_link()
        if not filename:
            return
        self.shared_model.add_link(filename)
        self.save_hotboxes()
        self.toolbar.reload.setEnabled(True)

    def _call_unlink(self):
        index = self.shared_view.get_selected_row()
        if index is None:
            return warning('Hotbox designer', 'No hotbox selected')
        self.shared_model.remove_link(index)
        self.save_hotboxes()
        self.toolbar.reload.setEnabled(True)

    def _call_remove(self):
        hotbox = self.get_selected_hotbox()
        if hotbox is None:
            return warning('Hotbox designer', 'No hotbox selected')

        areyousure = QtWidgets.QMessageBox.question(
            self,
            'remove',
            'remove a hotbox is definitive, are you sure to continue',
            buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            defaultButton=QtWidgets.QMessageBox.No)

        if areyousure == QtWidgets.QMessageBox.No:
            return

        self.personnal_model.layoutAboutToBeChanged.emit()
        self.personnal_model.hotboxes.remove(hotbox)
        self.personnal_model.layoutChanged.emit()
        self.save_hotboxes()
        self.toolbar.reload.setEnabled(True)

    def _call_reload(self):
        hotbox_designer.load_hotboxes(self.application)
        self.toolbar.reload.setEnabled(False)

    def _call_option_set(self, option, value):
        self.personnal_model.layoutAboutToBeChanged.emit()
        hotbox = self.get_selected_hotbox()
        if option == 'name':
            value = get_valid_name(self.personnal_model.hotboxes, value)

        if hotbox is not None:
            hotbox['general'][option] = value
        self.personnal_model.layoutChanged.emit()
        self.toolbar.reload.setEnabled(True)
        self.save_hotboxes()

    def _call_set_hotkey(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return warning('Hotbox designer', 'No hotbox selected')
        modes = self.application.available_set_hotkey_modes
        dialog = HotkeySetter(modes)
        result = dialog.exec_()
        name = hotbox['general']['name']
        open_cmd = OPEN_COMMAND.format(
            name=name,
            application=self.application.name)
        switch_cmd = SWITCH_COMMAND.format(
            name=name,
            application=self.application.name)
        if result == QtWidgets.QDialog.Rejected:
            return
        self.application.set_hotkey(
            name=name,
            mode=dialog.mode(),
            sequence=dialog.get_key_sequence(),
            open_cmd=open_cmd,
            close_cmd=CLOSE_COMMAND.format(name=name),
            switch_cmd=switch_cmd)

    def _call_export(self):
        hotbox = self.get_selected_hotbox()
        if not hotbox:
            return warning('Hotbox designer', 'No hotbox selected')
        export_hotbox(hotbox)

    def _call_import(self):
        hotbox = import_hotbox()
        if not hotbox:
            return warning('Hotbox designer', 'No hotbox selected')
        hotboxes = self.personnal_model.hotboxes
        name = get_valid_name(hotboxes, hotbox['general']['name'])
        hotbox['general']['name'] = name

        self.personnal_model.layoutAboutToBeChanged.emit()
        self.personnal_model.hotboxes.append(hotbox)
        self.personnal_model.layoutChanged.emit()
        self.save_hotboxes()
        self.toolbar.reload.setEnabled(True)


class HotboxManagerToolbar(QtWidgets.QToolBar):
    newRequested = QtCore.Signal()
    editRequested = QtCore.Signal()
    deleteRequested = QtCore.Signal()
    linkRequested = QtCore.Signal()
    unlinkRequested = QtCore.Signal()
    importRequested = QtCore.Signal()
    exportRequested = QtCore.Signal()
    setHotkeyRequested = QtCore.Signal()
    reloadRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super(HotboxManagerToolbar, self).__init__(parent)
        self.setIconSize(QtCore.QSize(16, 16))
        self.new = QtWidgets.QAction(icon('manager-new.png'), '', self)
        self.new.setToolTip('Create new hotbox')
        self.new.triggered.connect(self.newRequested.emit)
        self.edit = QtWidgets.QAction(icon('manager-edit.png'), '', self)
        self.edit.setToolTip('Edit hotbox')
        self.edit.triggered.connect(self.editRequested.emit)
        self.delete = QtWidgets.QAction(icon('manager-delete.png'), '', self)
        self.delete.setToolTip('Delete hotbox')
        self.delete.triggered.connect(self.deleteRequested.emit)
        self.link = QtWidgets.QAction(icon('link.png'), '', self)
        self.link.setToolTip('Link to external hotbox file')
        self.link.triggered.connect(self.linkRequested.emit)
        self.unlink = QtWidgets.QAction(icon('unlink.png'), '', self)
        self.unlink.setToolTip('Remove hotbox file link')
        self.unlink.triggered.connect(self.unlinkRequested.emit)
        self.import_ = QtWidgets.QAction(icon('manager-import.png'), '', self)
        self.import_.setToolTip('Import hotbox')
        self.import_.triggered.connect(self.importRequested.emit)
        self.export = QtWidgets.QAction(icon('manager-export.png'), '', self)
        self.export.setToolTip('Export hotbox')
        self.export.triggered.connect(self.exportRequested.emit)
        self.hotkeyset = QtWidgets.QAction(icon('touch.png'), '', self)
        self.hotkeyset.setToolTip('Set hotkey')
        self.hotkeyset.triggered.connect(self.setHotkeyRequested.emit)
        self.reload = QtWidgets.QAction(icon('reload.png'), '', self)
        self.reload.setToolTip('Reload hotboxes')
        self.reload.triggered.connect(self.reloadRequested.emit)

        self.addAction(self.new)
        self.addAction(self.edit)
        self.addAction(self.delete)
        self.addSeparator()
        self.addAction(self.link)
        self.addAction(self.unlink)
        self.addSeparator()
        self.addAction(self.import_)
        self.addAction(self.export)
        self.addSeparator()
        self.addAction(self.hotkeyset)
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


class HotboxPersonalTableModel(QtCore.QAbstractTableModel):

    def __init__(self, hotboxes, parent=None):
        super(HotboxPersonalTableModel, self).__init__(parent=parent)
        self.hotboxes = hotboxes

    def columnCount(self, _):
        return 1

    def rowCount(self, _):
        return len(self.hotboxes)

    def set_hotbox(self, row, hotbox):
        self.layoutAboutToBeChanged.emit()
        self.hotboxes[row] = hotbox
        self.layoutChanged.emit()

    def data(self, index, role):
        row, col = index.row(), index.column()
        hotbox = self.hotboxes[row]
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return hotbox['general']['name']


class HotboxSharedTableModel(QtCore.QAbstractTableModel):

    def __init__(self, hotboxes_links, parent=None):
        super(HotboxSharedTableModel, self).__init__(parent=parent)
        self.hotboxes_links = hotboxes_links
        self.hotboxes = [load_json(l) for l in hotboxes_links]

    def columnCount(self, _):
        return 1

    def rowCount(self, _):
        return len(self.hotboxes_links)

    def add_link(self, hotbox_link):
        self.layoutAboutToBeChanged.emit()
        self.hotboxes_links.append(hotbox_link)
        self.hotboxes.append(load_json(hotbox_link))
        self.layoutChanged.emit()

    def remove_link(self, index):
        self.layoutAboutToBeChanged.emit()
        self.hotboxes_links.pop(index)
        self.hotboxes.pop(index)
        self.layoutChanged.emit()

    def data(self, index, role):
        row, col = index.row(), index.column()
        hotbox = self.hotboxes_links[row]
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return hotbox


class HotboxGeneralInfosWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HotboxGeneralInfosWidget, self).__init__(parent)
        self.setFixedWidth(200)
        self.label = QtWidgets.QLabel()
        self.open_command = CommandButton('show')
        self.close_command = CommandButton('hide')
        self.switch_command = CommandButton('switch')

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(Title('Infos'))
        self.layout.addSpacing(8)
        self.layout.addWidget(self.label)
        self.layout.addSpacing(8)
        self.layout.addStretch(1)
        self.layout.addWidget(Title('Commands'))
        self.layout.addSpacing(8)
        self.layout.addWidget(self.open_command)
        self.layout.addWidget(self.close_command)
        self.layout.addWidget(self.switch_command)

    def set_hotbox_data(self, hotbox_data):
        self.label.setText(hotbox_data_to_html(hotbox_data))


class HotboxGeneralSettingWidget(QtWidgets.QWidget):
    optionSet = QtCore.Signal(str, object)
    applyRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super(HotboxGeneralSettingWidget, self).__init__(parent)
        self.setFixedWidth(200)
        self.name = QtWidgets.QLineEdit()
        self.name.textEdited.connect(partial(self.optionSet.emit, 'name'))
        self.submenu = BoolCombo(False)
        self.submenu.valueSet.connect(partial(self.optionSet.emit, 'submenu'))
        self.triggering = QtWidgets.QComboBox()
        self.triggering.addItems(TRIGGERING_TYPES)
        self.triggering.currentIndexChanged.connect(self._triggering_changed)
        self.aiming = BoolCombo(False)
        self.aiming.valueSet.connect(partial(self.optionSet.emit, 'aiming'))
        self.leaveclose = BoolCombo(False)
        method = partial(self.optionSet.emit, 'leaveclose')
        self.leaveclose.valueSet.connect(method)

        self.open_command = CommandButton('show')
        self.close_command = CommandButton('hide')
        self.switch_command = CommandButton('switch')

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
        self.layout.addRow('close on leave', self.leaveclose)
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow(Title('Commands'))
        self.layout.addItem(QtWidgets.QSpacerItem(0, 8))
        self.layout.addRow(self.open_command)
        self.layout.addRow(self.close_command)
        self.layout.addRow(self.switch_command)

    def _triggering_changed(self, _):
        self.optionSet.emit('triggering', self.triggering.currentText())

    def _touch_changed(self, _):
        self.optionSet.emit('touch', self.touch.text())

    def set_hotbox_settings(self, hotbox_settings):
        self.blockSignals(True)
        self.submenu.setCurrentText(str(hotbox_settings['submenu']))
        self.name.setText(hotbox_settings['name'])
        self.triggering.setCurrentText(hotbox_settings['triggering'])
        self.aiming.setCurrentText(str(hotbox_settings['aiming']))
        self.leaveclose.setCurrentText(str(hotbox_settings['leaveclose']))
        self.blockSignals(False)