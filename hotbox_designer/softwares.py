import os
from PySide2 import QtWidgets
import shiboken2


FILENAME = 'hotboxes.json'


class AbstractSoftware(object):
    NAME = 'NONE'

    def __init__(self):
        self.file = self.get_file()
        self.main_window = self.get_main_window()
        self.reader_parent = self.get_reader_parent()
        self.available_languages = self.get_available_languages()

    @staticmethod
    def get_file():
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


class Maya(AbstractSoftware):
    NAME = 'Maya'

    @staticmethod
    def get_file():
        from maya import cmds
        return os.path.join(cmds.internalVar(userPrefDir=True), FILENAME)

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
        return 'mel', 'python'


class Nuke(AbstractContext):
    NAME = 'Nuke'

    @staticmethod
    def get_file():
        return os.path.join(os.path.expanduser('~/.nuke'), FILENAME)

    @staticmethod
    def get_main_window():
        for w in QtWidgets.qApp.topLevelWidgets():
            if w.inherits('QMainWindow'):
                return w

    @staticmethod
    def get_reader_parent():
        return None

    @staticmethod
    def get_available_languages():
        return 'python', 'nuke_tcl', 'nuke_expression'
