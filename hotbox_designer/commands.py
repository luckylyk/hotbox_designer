
OPEN_COMMAND = """\
import hotbox_designer
from hotbox_designer import applications
hotbox_designer.initialize(applications.{application}())
hotbox_designer.show('{name}')
"""

CLOSE_COMMAND = """\
import hotbox_designer
hotbox_designer.hide('{name}')
"""

SWITCH_COMMAND = """\
import hotbox_designer
from hotbox_designer import applications
hotbox_designer.initialize(applications.{application}())
hotbox_designer.switch('{name}')
"""
