
import os
import json
from hotbox_designer.templates import HOTBOX


DEFAULT_NAME = 'MyHotbox_{}'
TRIGGERING_TYPES = 'click only', 'click or close'
HOTBOX_REPRESENTATION = """\
<b>Name </b>{name}<br>
<b>Submenu </b>{submenu}<br>
<b>Triggering </b>{triggering}<br>
<b>Aiming </b>{aiming}<br>
<b>Close on leave </b>{leaveclose}<br>
"""


def get_new_hotbox(hotboxes):
    options = HOTBOX.copy()
    options.update({'name': get_valid_name(hotboxes)})
    return {
        'general': options,
        'shapes': []}


def get_valid_name(hotboxes, proposal=None):
    names = [hotbox['general']['name'] for hotbox in hotboxes]
    index = 0
    name = proposal or DEFAULT_NAME.format(str(index).zfill(2))
    while name in names:
        if proposal:
            name = proposal + "_" + str(index).zfill(2)
        else:
            name = DEFAULT_NAME.format(str(index).zfill(2))
        index += 1
    return name


def load_hotboxes_datas(filename):
    datas = load_json(filename, default=[])
    return [ensure_old_data_compatible(data) for data in datas]


def load_json(filename, default=None):
    if not os.path.exists(filename):
        return default
    with open(filename, 'r') as f:
        return json.load(f)


def save_datas(filename, hotboxes_data):
    with open(filename, 'w') as f:
        json.dump(hotboxes_data, f, indent=2)


def copy_hotbox_data(data):
    copied = {}
    copied['general'] = data['general'].copy()
    copied['shapes'] = [shape.copy() for shape in data['shapes']]
    return copied


def ensure_old_data_compatible(data):
    """
    Tests and update datas done with old version of the script
    This function contain all the data structure history to convertion
    """
    try:
        del data['submenu']
    except:
        pass
    try:
        data['general']['submenu']
    except KeyError:
        data['general']['submenu'] = False
    try:
        data['general']['leaveclose']
    except KeyError:
        data['general']['leaveclose'] = False

    return data


def load_templates():
    path = os.path.join(os.path.dirname(__file__), 'resources', 'templates')
    files = os.listdir(path)
    templates = []
    for file_ in files:
        filepath = os.path.join(path, file_)
        with open(filepath, 'r') as f:
            templates.append(json.load(f))
    return templates


def hotbox_data_to_html(data):
    return HOTBOX_REPRESENTATION.format(
        name=data['general']['name'],
        submenu=data['general']['submenu'],
        triggering=data['general']['triggering'],
        aiming=data['general']['aiming'],
        leaveclose=data['general']['leaveclose'])
