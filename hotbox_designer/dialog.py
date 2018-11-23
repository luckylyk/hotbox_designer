import os
import json
from PySide2 import QtWidgets
from hotbox_designer.data import (
    get_new_hotbox, get_valid_name, copy_hotbox_data, load_templates,
    ensure_old_data_compatible)


def import_hotbox():
    filenames = QtWidgets.QFileDialog.getOpenFileName(
        None, caption='Import hotbox', directory=os.path.expanduser("~"),
        filter='*.json')
    if not filenames:
        return
    with open(filenames[0], 'r') as f:
        return ensure_old_data_compatible(json.load(f))


def import_hotbox_link():
    filenames = QtWidgets.QFileDialog.getOpenFileName(
        None, caption='Import hotbox', directory=os.path.expanduser("~"),
        filter='*.json')
    if filenames:
        return filenames[0]
    return None


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
