This tool is currently in development and not available in a stable version.


# Hotbox Designer
author: Lionel Brouyère

tester: David Vincze

https://vimeo.com/299771986
### Description
Python plug-in for CGI Softwares.
It provide a really simple way to design fully custom hotbox menus.
### Installation
#### Autodesk Maya

place the "hotbox_designer" folder into the maya script folder

| os | path |
| ------ | ------ |
| linux | ~<username>/maya |
| windows | \Users\<username>\Documents\maya |
| mac os x | ~<username>/Library/Preferences/Autodesk/maya |

python command to launch the hotbox designer manager
```python
from hotbox_designer.manager import HotboxManager
from hotbox_designer.softwares import Maya
hotboxes_manager = HotboxManager(Maya())
hotboxes_manager.show()
```
#### For Nuke
Place the _"hotbox_designer"_ folder into _~/.nuke_<br />
Python command to launch the hotbox designer manager:
```python
from hotbox_designer.manager import HotboxManager
from hotbox_designer.softwares import Nuke
hotboxes_manager = HotboxManager(Nuke())
hotboxes_manager.show()
```
#### For Blender
TODO
### Architecture
The application is separated in three parts:
- the manager
its a simple ui who let manage multiple hotboxes and save them
![N|Solid](https://raw.githubusercontent.com/luckylyk/hotbox_designer/master/documentation/manager.jpg)
- the editor
this is the hotbox design part. It look like a simple version of QtDesigner
![N|Solid](https://raw.githubusercontent.com/luckylyk/hotbox_designer/master/documentation/heditor.jpg)
- the reader
this contains the final hotbox widget
