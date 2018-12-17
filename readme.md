
# Hotbox Designer
Python plug-in for CGI Softwares.
It provide simple tools to create visually a hotbox menus, simply manage them and use them in the main software.

<img src="https://raw.githubusercontent.com/luckylyk/hotbox_designer/master/documentation/hotbox.gif" alt="drawing" align="center" width="500"/>

### Table of contents
* [Credits](#credits)
* [Implementation](#implementation)
* [Installation](#installation)
    * [Maya](#autodesk-maya)
    * [Nuke](#nuke)
    * [Houdini](#houdini)
* [Tutorials](#tutorials)
* [Code samples](#code-samples)
    * [Launch manager](#launch-manager)
    * [Create custom widget](#create-custom-widget)
        * [Basic widget](#basic-widget)
        * [Advanced widget](#advanced-widget)
* [Tools](#tools)
    * [Designer](#designer)
    * [Manager](#manager)
    * [Reader](#reader)

### Credits
main coder: Lionel Brouyère
contributor: Vincent Girès
tester: David Vincze, Vincent Girès
### Implementation
| Software       | Implementation state | Application as string | Hotkey setter   |
| ------         | ------               | ------                | -----           |
| Autodesk Maya  | done                 | 'maya'                | available       |
| Foundry Nuke   | done                 | 'nuke'                | available       |
| Autodesk 3dsMax| planned              | undefined             | Not available   |
| SideFX Houdini | done                 | 'houdini'             | Not available   |

For each software who provide python and support PySide2/PyQt5, the implementation should be easy.

### Installation
#### Autodesk Maya

place the "hotbox_designer" folder into the maya script folder

| os       | path                                          |
| ------   | ------                                        |
| linux    | ~/< username >/maya                           |
| windows  | \Users\<username>\Documents\maya              |
| mac os x | ~<username>/Library/Preferences/Autodesk/maya |

#### Nuke
Place the _"hotbox_designer"_ folder into _~/.nuke_ or make it available in PYTHONPATH<br />
Add this script to menu.py or make it available in NUKE_PATH:
```python
import nuke
import hotbox_designer
from hotbox_designer.applications import Nuke
from hotbox_designer.manager import HotboxManager

nuke_app = Nuke()
hotbox_manager = HotboxManager(nuke_app)

nuke_menu = nuke.menu('Nuke')
menu = nuke_menu.addMenu('Hotbox Designer')
menu.addCommand(
    name='Manager',
    command=hotbox_manager.show)
nuke_app.create_menus()
```
Hotkeys are saved in _~/.nuke/hotbox_hotkey.json_.<br />
To delete it, right now, the only way is to delete it in the file.

#### Houdini
soon
### Tutorials
* [My first hotbox](https://vimeo.com/304248049)
* [Create a submenu](https://vimeo.com/304252379)
### Code Samples
#### Launch manager
```python
import hotbox_designer
hotbox_designer.launch_manager('maya') # or any other available application name as string
```
#### Create custom widget
* ##### Basic widget
```python
from hotbox_designer import load_json, HotboxWidget
# it can be integrated in a layout of an parent widget
widget = HotboxWidget()
# That can be changed interactively
hotbox_data = load_json(r"your exported hotbox as json filepath")
widget.set_hotbox_data(hotbox_data)
```
* ##### Advanced widget
Example of an template explorer

```python
from hotbox_designer import HotboxWidget, load_templates
from PySide2 import QtWidgets, QtCore

class HotboxTemplateNavigator(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(HotboxTemplateNavigator, self).__init__(*args, **kwargs)
        self.templates = load_templates()
        items = [d['general']['name'] for d in self.templates]
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(items)
        self.combo.currentIndexChanged.connect(self.combo_index_changed)
        self.hotbox_widget = HotboxWidget()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.hotbox_widget)
        self.layout.addStretch(1)

    def combo_index_changed(self):
        index = self.combo.currentIndex()
        data = self.templates[index]
        self.hotbox_widget.set_hotbox_data(data)
        size = QtCore.QSize(data["general"]["width"], data["general"]["height"])
        self.hotbox_widget.setFixedSize(size)
        self.adjustSize()


hotbox_template_navigator = HotboxTemplateNavigator(None, QtCore.Qt.Window)
hotbox_template_navigator.show()
```

### Tools
The application is separated in three parts:
- ##### Designer
this is the hotbox design part. It look like a simple version of QtDesigner
![N|Solid](https://raw.githubusercontent.com/luckylyk/hotbox_designer/master/documentation/heditor.jpg)
- ##### Manager
its a simple ui who let manage multiple hotboxes and save them
![N|Solid](https://raw.githubusercontent.com/luckylyk/hotbox_designer/master/documentation/manager2.jpg)
- ##### Reader
this contains the final hotbox widget. That's what is called when you use your menu as final product.
