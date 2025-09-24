import os
import json
from hotbox_designer.vendor.Qt import QtWidgets
from hotbox_designer.dialog import warning
from hotbox_designer.languages import (
    MEL, PYTHON, NUKE_TCL, NUKE_EXPRESSION, HSCRIPT, RUMBA_SCRIPT)


HOTBOXES_FILENAME = 'hotboxes.json'
SHARED_HOTBOXES_FILENAME = 'shared_hotboxes.json'
SETMODE_PRESS_RELEASE = 'open on press | close on release'
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

    @staticmethod
    def update_hotkeys():
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
        """Get the main window for maya.

        Returns:
            shiboken2.wrapInstance: The pointer to the maya main window.
        """
        import maya.OpenMayaUI as omui
        import shiboken2
        if os.name == 'posix':
            return None
        ptr = omui.MQtUtil.mainWindow()
        if ptr is not None:
            return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)

    @staticmethod
    def get_reader_parent():
        return None

    @staticmethod
    def get_available_languages():
        return [MEL, PYTHON]

    @staticmethod
    def get_available_set_hotkey_modes():
        return [SETMODE_PRESS_RELEASE, SETMODE_SWITCH_ON_PRESS]

    def set_hotkey(
            self, name, mode, sequence, open_cmd, close_cmd, switch_cmd):
        from maya import cmds, mel
        current_hotkey_set = cmds.hotkeySet(current=True, query=True)
        if current_hotkey_set == 'Maya_Default':
            msg = (
                'The current hotkey set is locked,'
                'change in the hotkey editor')
            warning('Hotbox designer', msg)
            return mel.eval("hotkeyEditorWindow;")

        use_alt = 'Alt' in sequence
        use_ctrl = 'Ctrl' in sequence
        use_shift = 'Shift' in sequence
        touch = sequence.split("+")[-1]
        show_name = 'showHotbox_' + name
        hide_name = 'hideHotbox_' + name
        switch_name = 'switchHotbox_' + name
        if mode == SETMODE_PRESS_RELEASE:
            cmds.nameCommand(
                show_name,
                annotation='show ' + name + ' hotbox',
                command=format_command_for_mel(open_cmd),
                sourceType="python")
            cmds.nameCommand(
                hide_name,
                annotation='hide ' + name + ' hotbox',
                command=format_command_for_mel(close_cmd),
                sourceType="python")
            cmds.hotkey(
                keyShortcut=touch,
                altModifier=use_alt,
                ctrlModifier=use_ctrl,
                shiftModifier=use_shift,
                name=show_name,
                releaseName=hide_name)
        else:
            cmds.nameCommand(
                switch_name,
                annotation='switch ' + name + ' hotbox',
                command=format_command_for_mel(switch_cmd),
                sourceType="python")
            cmds.hotkey(
                keyShortcut=touch,
                altModifier=use_alt,
                ctrlModifier=use_ctrl,
                shiftModifier=use_shift,
                name=switch_name)


def format_command_for_mel(command):
    '''
    cause cmds.nameCommand fail to set python command, this method
    embed the given command to a mel command callin "python" function.
    It put everylines in a single one cause mel is not supporting multi-lines
    strings. Hopefully Autodesk gonna fixe this soon.
    '''
    command = command.replace("\n", ";")
    command = 'python("{}")'.format(command)
    return command


class Nuke(AbstractApplication):

    @staticmethod
    def get_data_folder():
        return os.path.expanduser('~/.nuke')

    @staticmethod
    def get_main_window():
        for widget in QtWidgets.QApplication.instance().topLevelWidgets():
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

    def set_hotkey(
            self, name, mode, sequence, open_cmd, close_cmd, switch_cmd):
        self.save_hotkey(name, sequence, switch_cmd)
        self.create_menus()

    def get_hotkey_file(self):
        hotkey_file = os.path.join(
            self.get_data_folder(), 'hotbox_hotkey.json')
        return hotkey_file

    def load_hotkey(self):
        hotkey_file = self.get_hotkey_file()
        if not os.path.exists(hotkey_file):
            return {}
        with open(hotkey_file, 'r') as f:
            return json.load(f)

    def save_hotkey(self, name, sequence, command):
        data = self.load_hotkey()
        data[name] = {
            'sequence': sequence,
            'command': command}
        with open(str(self.get_hotkey_file()), 'w+') as f:
            json.dump(data, f, indent=2)

    def create_menus(self):
        import nuke
        nuke_menu = nuke.menu('Nuke')
        menu = nuke_menu.addMenu('Hotbox Designer')
        hotkey_data = self.load_hotkey()
        for name, value in hotkey_data.items():
            menu.addCommand(
                name='Hotboxes/{name}'.format(name=name),
                command=str(value['command']), shortcut=value['sequence'])


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
        return [PYTHON, HSCRIPT]

    @staticmethod
    def get_available_set_hotkey_modes():
        return [SETMODE_SWITCH_ON_PRESS]

    def set_hotkey(
            self, name, mode, sequence, open_cmd, close_cmd, switch_cmd):
        from hotbox_designer.qtutils import set_shortcut
        from functools import partial
        set_shortcut(sequence, self.main_window, partial(execute, switch_cmd))

class Rumba(AbstractApplication):

    @staticmethod
    def get_data_folder():
        return os.path.expanduser('~/.rumba')

    @staticmethod
    def get_main_window():
        import rumbapy
        return rumbapy.widget("MainWindow")

    @staticmethod
    def get_reader_parent():
        return None

    @staticmethod
    def get_available_languages():
        return [RUMBA_SCRIPT, PYTHON]

    @staticmethod
    def get_available_set_hotkey_modes():
        return [SETMODE_SWITCH_ON_PRESS]

    def set_hotkey(
            self, name, mode, sequence, open_cmd, close_cmd, switch_cmd):
        self.save_hotkey(name, sequence, switch_cmd)
        self.create_menus(reload=True)

    def update_hotkeys(self):
        hotkey_file = self.get_hotkey_file()
        updated_hotkeys = self.remove_hotbox_item(
            self.load_hotboxes(), self.load_hotkey()
        )
        with open(hotkey_file, 'w') as f:
            json.dump(updated_hotkeys, f, indent=2)

    def get_hotboxes_file(self):
        hotboxes_file = os.path.join(
            self.get_data_folder(), HOTBOXES_FILENAME)
        return hotboxes_file

    def get_hotkey_file(self):
        hotkey_file = os.path.join(
            self.get_data_folder(), 'hotbox_hotkey.json')
        return hotkey_file

    def load_hotboxes(self):
        hotboxes_file = self.get_hotboxes_file()
        if not os.path.exists(hotboxes_file):
            return []
        with open(hotboxes_file, 'r') as f:
            return json.load(f)
        
    def load_hotkey(self):
        hotkey_file = self.get_hotkey_file()
        if not os.path.exists(hotkey_file):
            return {}
        with open(hotkey_file, 'r') as f:
            return json.load(f)

    def save_hotkey(self, name, sequence, command):
        hotkey_data = self.load_hotkey()
        updated_hotkey_data = self.remove_hotbox_item(self.load_hotboxes(), hotkey_data)
        updated_hotkey_data[name] = {
            'sequence': sequence,
            'command': command}
        with open(str(self.get_hotkey_file()), 'w') as f:
            json.dump(updated_hotkey_data, f, indent=2)

    def delete_menu(self, menu_bar: QtWidgets.QMenuBar, menu_title: str):
        """Find and delete a menu with a specific title from the menu bar."""
        menus = menu_bar.actions()
        for menu in menus:
            if menu.menu() and menu.text() == menu_title:
                menu_bar.removeAction(menu)

    def create_menus(self, reload=False):
        """Create the Hotbox Designer menu in Rumba's menu bar."""
        import rumbapy
        from functools import partial

        main_window = rumbapy.widget("MainWindow")
        menu_bar = main_window.menubar
        menu_title = "&Hotbox Designer"

        if reload:
            self.delete_menu(menu_bar, menu_title)

        hotbox_menu = menu_bar.addMenu(menu_title)

        hotkey_data = self.load_hotkey()

        for name, value in hotkey_data.items():
            action = rumbapy.action.new(
                name=name,
                widget=main_window,
                trigger=partial(lambda cmd: exec(cmd), value['command']),
                icon=None,
                shortcut=value["sequence"]
            )
            hotbox_menu.addAction(action)

    def remove_hotbox_item(self, hotboxes, hotbox_hotkey):
        """
        Remove hotbox items that are not present in the current hotboxes
        """
        hotbox_items = {item.get("general", {}).get("name") for item in hotboxes}
        
        updated_hotkey = {
            key: value for key, value in hotbox_hotkey.items()
            if key in hotbox_items
        }
        
        return updated_hotkey
