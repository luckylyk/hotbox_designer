from hotbox_designer.reader.application import HotboxReader
from hotbox_designer.utils import load_hotboxes

hotboxes = {}

def initialize(context):
    if hotboxes:
        return

    hotboxes_datas = load_hotboxes(context.file)
    for hotboxes_data in hotboxes_datas:
        name = hotboxes_data['general']['name']
        reader = HotboxReader(hotboxes_data, parent=context.parent)
        hotboxes[name] = reader


def show_hotbox(name):
    hotboxes['name'].show()


def hide_hotbox(name):
    hotboxes['name'].hide()
