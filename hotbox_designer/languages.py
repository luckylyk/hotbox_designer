
PYTHON = 'python'
MEL = 'mel'
NUKE_TCL = 'nuke tcl'
NUKE_EXPRESSION = 'nuke expression'
HSCRIPT = 'houdini script'


def execute_code(language, code):
    return EXECUTORS[language](code)


def execute_python(code):
    exec(code)


def execute_mel(code):
    from maya import mel
    mel.eval(code.replace(u'\u2029', '\n'))


def execute_nuke_tcl(code):
    import nuke
    nuke.tcl(code)


def execute_nuke_expression(code):
    import nuke
    nuke.expression(code)


def execute_hscript(code):
    import hou
    hou.hscript(code)


EXECUTORS = {
    PYTHON: execute_python,
    MEL: execute_mel,
    NUKE_TCL: execute_nuke_tcl,
    NUKE_EXPRESSION: execute_nuke_expression,
    HSCRIPT: execute_hscript
}
