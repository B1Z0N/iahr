import sys
import os
from PyQt5 import QtWidgets, QtCore

class Win(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        _b1 = QtWidgets.QPushButton('Sample text')
        _text = QtWidgets.QLabel()
        _text.setAlignment(QtCore.Qt.AlignCenter)
        self._text = _text

        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(_b1)
        self.setLayout(_layout)
        _b1.clicked.connect(self.b1_click_handler)

    def b1_click_handler(self):
        _refcnt = sys.gettotalrefcount()
        self._text.setText(f'Ref count: {_refcnt}')

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    
    window = Win()
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec_())
