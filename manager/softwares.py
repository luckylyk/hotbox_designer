import os
from PySide2 import QtWidgets
import shiboken2
from hotbox_designer.utils import load_hotboxes

FILENAME = 'hotboxes.json'


class AbstractContext(object):
    def __init__(self):
        self.file = self.get_file()
        self.parent = self.get_parent()

    @staticmethod
    def get_file():
        raise NotImplementedError

    @staticmethod
    def get_parent():
        raise NotImplementedError

    @staticmethod
    def is_active(hotbox):
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

    @staticmethod
    def is_active_in_software(hotbox):
        from maya import cmds
        alt = hotbox['general']['alt']
        ctrl = hotbox['general']['ctrl']
        touch = hotbox['general']['touch']
        current_command_set = cmds.hotkey(
            touch,
            query=True,
            altModifier=alt,
            ctrlModifier=ctrl,
            name=True)
        return current_command_set == hotbox['general']['name']

    @staticmethod
    def activate_hotbox_in_software(hotbox, press_command, release_command):
        from maya import cmds
        name = hotbox['general']['name']
        alt = hotbox['general']['alt']
        ctrl = hotbox['general']['ctrl']
        touch = hotbox['general']['touch']
        command = cmds.nameCommand(name + '_show', command=press_command)
        cmds.hotkey(touch, altModifier=alt, ctrlModifier=ctrl, name=command)
        command = cmds.nameCommand(name + '_show', command=press_command)
        cmds.hotkey(
            touch, altModifier=alt, ctrlModifier=ctrl, releaseName=command)
