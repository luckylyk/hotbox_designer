import os
from PySide2 import QtWidgets
from hotbox_designer.languages import (
    MEL, PYTHON, NUKE_TCL, NUKE_EXPRESSION, HSCRIPT)


HOTBOXES_FILENAME = 'hotboxes.json'
SHARED_HOTBOXES_FILENAME = 'shared_hotboxes.json'
SETMODE_PRESS_RELEASE = 'open on press and close on release'
SETMODE_SWITCH_ON_PRESS = 'switch on press'


def execute(command):
    exec(command)


class AbstractApplication(object):

    def __init__(self):
        self.name = type(self).__name__
        folder = self.get_data_folder()
        self.local_file = os.path.join(folder, HOTBOXES_FILENAME)
        self.shared_file = os.path.join(folder, SHARED_HOTBOXES_FILENAME)
        self.main_window = self.get_main_window()
        self.reader_parent = self.get_reader_parent()
        self.available_languages = self.get_available_languages()
        self.available_set_hotkey_modes = self.get_available_set_hotkey_modes()

    @staticmethod
    def get_data_folder():
        raise NotImplementedError

    @staticmethod
    def get_reader_parent():
        raise NotImplementedError

    @staticmethod
    def get_main_window():
        raise NotImplementedError

    @staticmethod
    def get_available_languages():
        raise NotImplementedError

    @staticmethod
    def get_available_set_hotkey_modes():
        raise NotImplementedError

    def set_hotkey(self, mode, sequence, open_cmd, close_cmd, switch_cmd):
        raise NotImplementedError


class Maya(AbstractApplication):

    @staticmethod
    def get_data_folder():
        from maya import cmds
        return cmds.internalVar(userPrefDir=True)

    @staticmethod
    def get_main_window():
        import maya.OpenMayaUI as omui
        import shiboken2
        main_window = omui.MQtUtil.mainWindow()
        if main_window is not None:
            return shiboken2.wrapInstance(long(main_window), QtWidgets.QWidget)

    @staticmethod
    def get_reader_parent():
        return None

    @staticmethod
    def get_available_languages():
        return MEL, PYTHON

    @staticmethod
    def get_available_set_hotkey_modes():
        return SETMODE_PRESS_RELEASE, SETMODE_SWITCH_ON_PRESS

    def set_hotkey(self, mode, sequence, open_cmd, close_cmd, switch_cmd):
        from maya import cmds
        use_alt = 'Alt' in sequence
        use_ctrl = 'Ctrl' in sequence
        touch = sequence.split("+")[-1]
        if mode == SETMODE_PRESS_RELEASE:
            cmds.nameCommand(
                'show hotbox',
                annotation='show hotbox',
                command=open_cmd)
            cmds.hotkey(
                keyShortcut=touch,
                altModifier=use_alt,
                ctrlModifier=use_ctrl,
                name='openhotbox')
            cmds.nameCommand(
                'close hotbox',
                annotation='close hotbox',
                command=close_cmd)
            cmds.hotkey(
                keyShortcut=touch,
                altModifier=use_alt,
                ctrlModifier=use_ctrl,
                name='closehotbox')
        else:
            cmds.nameCommand(
                'switch hotbox',
                annotation='switch hotbox',
                command=switch_cmd)
            cmds.hotkey(
                keyShortcut=touch,
                altModifier=use_alt,
                ctrlModifier=use_ctrl,
                name='switchhotbox')


class Nuke(AbstractApplication):

    @staticmethod
    def get_data_folder():
        return os.path.expanduser('~/.nuke')

    @staticmethod
    def get_main_window():
        for widget in QtWidgets.qApp.topLevelWidgets():
            if widget.inherits('QMainWindow'):
                return widget

    @staticmethod
    def get_reader_parent():
        return None

    @staticmethod
    def get_available_languages():
        return PYTHON, NUKE_TCL, NUKE_EXPRESSION

    @staticmethod
    def get_available_set_hotkey_modes():
        return [SETMODE_SWITCH_ON_PRESS]

    def set_hotkey(self, mode, sequence, open_cmd, close_cmd, switch_cmd):
        from hotbox_designer.qtutils import set_shortcut
        from functools import partial
        set_shortcut(sequence, self.main_window, partial(execute, switch_cmd))


class Houdini(AbstractApplication):

    @staticmethod
    def get_data_folder():
        return os.path.expanduser('~/houdini17.0')

    @staticmethod
    def get_main_window():
        import hou
        return hou.qt.mainWindow()

    @staticmethod
    def get_reader_parent():
        return None

    @staticmethod
    def get_available_languages():
        return PYTHON, HSCRIPT

    @staticmethod
    def get_available_set_hotkey_modes():
        return [SETMODE_SWITCH_ON_PRESS]

    def set_hotkey(self, mode, sequence, open_cmd, close_cmd, switch_cmd):
        from hotbox_designer.qtutils import set_shortcut
        from functools import partial
        set_shortcut(sequence, self.main_window, partial(execute, switch_cmd))