import os
import shiboken2
from PySide2 import QtWidgets
from hotbox_designer.languages import MEL, PYTHON, NUKE_TCL, NUKE_EXPRESSION


HOTBOXES_FILENAME = 'hotboxes.json'
SHARED_HOTBOXES_FILENAME = 'shared_hotboxes.json'


class AbstractApplication(object):

    def __init__(self):
        self.name = type(self).__name__
        folder = self.get_data_folder()
        self.local_file = os.path.join(folder, HOTBOXES_FILENAME)
        self.shared_file = os.path.join(folder, SHARED_HOTBOXES_FILENAME)
        self.main_window = self.get_main_window()
        self.reader_parent = self.get_reader_parent()
        self.available_languages = self.get_available_languages()

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


class Maya(AbstractApplication):

    @staticmethod
    def get_data_folder():
        from maya import cmds
        return cmds.internalVar(userPrefDir=True)

    @staticmethod
    def get_main_window():
        import maya.OpenMayaUI as omui
        main_window = omui.MQtUtil.mainWindow()
        if main_window is not None:
            return shiboken2.wrapInstance(long(main_window), QtWidgets.QWidget)

    @staticmethod
    def get_reader_parent():
        return None

    @staticmethod
    def get_available_languages():
        return MEL, PYTHON


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