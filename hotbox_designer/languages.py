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


EXECUTORS = {
    'python': execute_python,
    'mel': execute_mel,
    'nuke_tcl': execute_nuke_tcl,
    'nuke_expression': execute_nuke_expression
}
