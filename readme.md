
# Hotbox Designer
Python plug-in for CGI Softwares.  
It provide simple tools to create visually a hotbox menus, simply manage them and use them in the main software.
https://vimeo.com/299771986

### Table of contents
* [Credits](#credits)
* [Implementation](#implementation)
* [Installation](#installation)
    * [Maya](#autodesk-maya)
    * [Nuke](#nuke)
    * [Houdini](#houdini)
* [Tutorials](#tutorials)
* [Launch command](#launch-command)
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
| Foundry Nuke   | done                 | 'nuke'                | wip (to test)   |
| Blender        | in progress          | undefined             | Not available   |
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
Place the _"hotbox_designer"_ folder into _~/.nuke_<br />

#### Houdini
soon
### Tutorials
* ##### [My first hotbox](https://vimeo.com/304248049)
* ##### [Create a submenu](https://vimeo.com/304252379)
### Launch command
```python
import hotbox_designer
hotbox_designer.launch_manager('maya') # or any other available application name as string
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
