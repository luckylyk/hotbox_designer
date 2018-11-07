import os
from PySide2 import QtWidgets
import shiboken2
from hotbox_designer import load_data

FILENAME = 'hotboxes.json'


class AbstractContext(object):
    def __init__(self):
        self.file = self.get_file()
        self.main_window = self.get_main_window()
        self.reader_parent = self.get_reader_parent()

    @staticmethod
    def get_file():
        raise NotImplementedError

    @staticmethod
    def get_reader_parent():
        raise NotImplementedError

    @staticmethod
    def get_main_window():
        raise NotImplementedError


class Maya(AbstractContext):
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
