This tool is currently in development and not available in a stable version.

# Hotbox Designer
https://vimeo.com/299771986

### Credits 
main coder: Lionel Brouyère  
contributor: Vincent Girès  
tester: David Vincze, Vincent Girès  

### Description
Python plug-in for CGI Softwares.  
It provide simple tools to create visually a hotbox menus, simply manage them and use them in the main software.

### Implementation
| Software      | Implementation state | Application as string | Hotkey setter   |
| ------        | ------               | ------                | -----           |
| Autodesk Maya | done                 | 'maya'                | wip (to test)   |
| Foundry Nuke  | done                 | 'nuke'                | wip (to test)   |
| Blender       | in progress          | undefined             | Not available   |
| 3dsMax        | planned              | undefined             | Not available   |
| Natron        | planned              | undefined             | Not available   |
| Houdini       | planned              | undefined             | Not available   |

For each software who provide python and support PySide2/PyQt5, the implementation should be easy.

### Installation
#### Autodesk Maya

place the "hotbox_designer" folder into the maya script folder

| os | path |
| ------ | ------ |
| linux | ~/< username >/maya |
| windows | \Users\<username>\Documents\maya |
| mac os x | ~<username>/Library/Preferences/Autodesk/maya |

#### Nuke
Place the _"hotbox_designer"_ folder into _~/.nuke_<br />

### Launch command
```python
import hotbox_designer
hotbox_designer.launch_manager('application name as string')
```

### Tools
The application is separated in three parts:
- the manager
its a simple ui who let manage multiple hotboxes and save them
![N|Solid](https://raw.githubusercontent.com/luckylyk/hotbox_designer/master/documentation/manager2.jpg)
- the editor
this is the hotbox design part. It look like a simple version of QtDesigner
![N|Solid](https://raw.githubusercontent.com/luckylyk/hotbox_designer/master/documentation/heditor.jpg)
- the reader
this contains the final hotbox widget. That's what is called when you use your menu as final product.
