import os
import json
from functools import partial
from hotbox_designer.reader import HotboxReader
from hotbox_designer.utils import set_shortcut


hotboxes = {}


def initialize(context):
    if hotboxes:
        return
    load_hotboxes(context)


def load_hotboxes(context):
    hotboxes_datas = load_data(context.file)
    for hotboxes_data in hotboxes_datas:
        name = hotboxes_data['general']['name']
        reader = HotboxReader(hotboxes_data, parent=None)
        hotboxes[name] = reader


def show(name):
    hotboxes[name].show()


def hide(name):
    hotboxes[name].hide()


def load_data(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)


def save_data(filename, hotboxes_data):
    with open(filename, 'w') as f:
        json.dump(hotboxes_data, f, indent=2)
