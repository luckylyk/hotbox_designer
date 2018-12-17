import os
import json
from hotbox_designer.reader import HotboxReader, HotboxWidget
from hotbox_designer.manager import HotboxManager
from hotbox_designer.data import (
    load_hotboxes_datas, load_json, ensure_old_data_compatible,
    load_templates)
from hotbox_designer.applications import Nuke, Maya, Houdini


hotboxes = {}
hotbox_manager = None
APPLICATIONS = {'maya': Maya, 'nuke': Nuke, 'houdini': Houdini}


def launch_manager(application):
    if hotbox_manager is None:
        global hotbox_manager
        hotbox_manager = HotboxManager(APPLICATIONS[application]())
    hotbox_manager.show()


def initialize(application):
    if hotboxes:
        return
    load_hotboxes(application)


def load_hotboxes(application):
    hotboxes_datas = load_hotboxes_datas(application.local_file)
    file_ = application.shared_file
    hotboxes_datas += [
        ensure_old_data_compatible(load_json(f)) for f in load_json(file_)]

    for hotboxes_data in hotboxes_datas:
        name = hotboxes_data['general']['name']
        reader = HotboxReader(hotboxes_data, parent=None)
        reader.hideSubmenusRequested.connect(hide_submenus)
        hotboxes[name] = reader


def show(name):
    hotboxes[name].show()


def hide(name):
    hotboxes[name].hide()


def switch(name):
    if hotboxes[name].isVisible():
        return hide(name)
    return show(name)


def hide_submenus():
    for name in hotboxes:
        if hotboxes[name].is_submenu:
            hide(name)
