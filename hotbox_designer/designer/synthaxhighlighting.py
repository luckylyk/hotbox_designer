import keyword
from PySide2 import QtGui, QtCore


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)
        self.rules = []

        keywords = keyword.kwlist
        number_pattern = r'\b[+-]?[0-9]+[lL]?\b'
        comment_pattern = r'#[^\n]*'
        function_pattern = r'\b[A-Za-z0-9_]+(?=\()'

        keyword_format = QtGui.QTextCharFormat()
        keyword_format.setForeground(QtCore.Qt.white)
        keyword_format.setFontWeight(QtGui.QFont.Bold)
        self.rules.extend([
            (QtCore.QRegExp(word), keyword_format) for word in keywords])

        number_format = QtGui.QTextCharFormat()
        number_format.setForeground(QtCore.Qt.cyan)
        self.rules.append(
            (QtCore.QRegExp(number_pattern), number_format))

        comment_format = QtGui.QTextCharFormat()
        comment_format.setForeground(QtCore.Qt.lightGray)
        self.rules.append(
            (QtCore.QRegExp(comment_pattern), comment_format))

        function_format = QtGui.QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(QtCore.Qt.yellow)
        self.rules.append(
            (QtCore.QRegExp(function_pattern), function_format))

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
