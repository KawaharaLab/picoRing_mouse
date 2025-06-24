import os
import sys
import glob

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Pic(QAbstractButton):
    def __init__(self, pixmap_path, parent=None):
        super(Pic, self).__init__(parent)
        self.pixmap = QPixmap(pixmap_path)

    def sizeHint(self):
        return QSize(500, 500)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def pixChanged(self, pixmap):
        self.pixmap = QPixmap(pixmap)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Scroll Area which contains the widgets, set as the centralWidget
        self.scroll = QScrollArea()
        # Widget that contains the collection of Vertical Box
        self.widget = QWidget()
        # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.vbox = QHBoxLayout()
        # self.vbox.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        for path in glob.glob('icon/*.png'):
            object = QLabel()
            pic = QPixmap(path)
            pic.scaled(500, 500)
            object.setPixmap(pic)
            object.setStyleSheet('padding:100px')
            self.vbox.addWidget(object)

        self.vbox.setSpacing(200)

        self.widget.setLayout(self.vbox)

        # Scroll Area Properties
        self.scroll.setWidget(self.widget)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(False)
        self.scroll.setBackgroundRole(QPalette.Dark)
        # self.scroll.ensureWidgetVisible()

        layout = QHBoxLayout()
        layout.addWidget(self.scroll)
        self.setLayout(layout)

        self.setGeometry(0, 0, 1000, 900)
        # self.setWindowTitle('Scroll Area Demonstration')
        self.show()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:

        current_pos = self.scroll.horizontalScrollBar().value()
        if event.key() == Qt.Key_K:
            self.scroll.horizontalScrollBar().setValue(current_pos + 100)
        elif event.key() == Qt.Key_J:
            self.scroll.horizontalScrollBar().setValue(current_pos - 100)

        # if self.scroll.childAt(0, 0).isVisible():
        #    print('test')
        current_pos = self.scroll.horizontalScrollBar().value()
        print(current_pos)
        return super().keyPressEvent(event)

    def checkCurrentArea(self):
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
