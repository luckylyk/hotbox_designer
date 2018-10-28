import os
from PySide2 import QtWidgets
import shiboken2


FILENAME = 'hotboxes.json'


class AbstractContext():
    def __init__(self):
        self.file = self.get_file()
        self.parent = self.get_parent()

    @staticmethod
    def get_file():
        raise NotImplementedError

    @staticmethod
    def get_parent():
        raise NotImplementedError


class MayaContext(AbstractContext):
    @staticmethod
    def get_file():
        from maya import cmds
        return os.path.join(cmds.internalVar(userPrefDir=True), FILENAME)

    @staticmethod
    def get_parent():
        import maya.OpenMayaUI as omui
        main_window = omui.MQtUtil.mainWindow()
        if main_window is not None:
            return shiboken2.wrapInstance(long(main_window), QtWidgets.QWidget)