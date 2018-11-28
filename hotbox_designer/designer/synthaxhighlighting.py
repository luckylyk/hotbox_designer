import keyword
from PySide2 import QtGui, QtCore


TEXT_STYLES = {
    'keyword': {
        'color': QtCore.Qt.white,
        'bold': True,
        'italic': False
    },
    'number': {
        'color': QtCore.Qt.cyan,
        'bold': False,
        'italic': False
    },
    'comment': {
        'color': QtCore.Qt.red,
        'bold': False,
        'italic': False
    },
    'function': {
        'color': QtCore.Qt.green,
        'bold': False,
        'italic': True
    },
    'string': {
        'color': QtCore.Qt.yellow,
        'bold': False,
        'italic': False
    },
    'boolean': {
        'color': QtCore.Qt.darkYellow,
        'bold': True,
        'italic': False
    }
}


def create_textcharformat(color, bold=False, italic=False):
    format = QtGui.QTextCharFormat()
    format.setForeground(color)
    if bold:
        format.setFontWeight(QtGui.QFont.Bold)
    if italic:
        format.setFontItalic(True)
    return format


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    PATTERNS = {
        'keyword': r'\b|'.join(keyword.kwlist),
        'number': r'\b[+-]?[0-9]+[lL]?\b',
        'comment': r'#[^\n]*',
        'function': r'\b[A-Za-z0-9_]+(?=\()',
        'string': r'".*"|\'.*\'',
        'boolean': r'\bTrue\b|\bFalse\b'
    }

    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)
        self.rules = []
        for name, properties in TEXT_STYLES.items():
            if name not in self.PATTERNS:
                continue
            text_format = create_textcharformat(
                color=properties['color'],
                bold=properties['bold'],
                italic=properties['italic'])
            self.rules.append(
                (QtCore.QRegExp(self.PATTERNS[name]), text_format))

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
