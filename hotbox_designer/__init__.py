import os
import json
from hotbox_designer.reader import HotboxReader
from hotbox_designer.data import load_hotboxes_datas

hotboxes = {}


def initialize(software):
    if hotboxes:
        return
    load_hotboxes(software)


def load_hotboxes(software):
    hotboxes_datas = load_hotboxes_datas(software.file)
    for hotboxes_data in hotboxes_datas:
        name = hotboxes_data['general']['name']
        reader = HotboxReader(hotboxes_data, parent=None)
        hotboxes[name] = reader


def show(name):
    hotboxes[name].show()


def hide(name):
    hotboxes[name].hide()


def switch(name):
    if hotboxes[name].isVisible():
        return show(name)
    return hide(name)


def hide_submenus():
    # iteritems() or items() not usernot used for python 2 and 3 compatibility
    names = hotboxes.keys()
    for name in names:
        if hotboxes[name].is_submenu:
            hide(name)

