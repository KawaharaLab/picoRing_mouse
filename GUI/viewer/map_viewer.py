
# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *


class MapViewer(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.winID = parent.winId()

        self.paper = QLabel()
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.paper, alignment=Qt.AlignHCenter)

        self.original_img = QPixmap("./pictures/paper.jpg")
        self.img_w, self.img_h = self.original_img.width(), self.original_img.height()
        self.window_geometry = parent.geometry()
        self.window_w, self.window_h = self.window_geometry.width(
        ), self.window_geometry.height() - 200
        self.window_w = 300
        self.window_h = 500
        self.offset_w = 0
        self.offset_h = 0
        self.scroll_angle_pre = self.scroll_angle_now = None
        self.current_img = self._renewCropImg()

        self.setLayout(self.mainLayout)

    def updateMapPos(self, sensor_info):
        joystick_state = sensor_info['joystick']

    def _renewCropImg(self):
        self._renewOffsetH()
        cropped_area = QRect(
            0, self.offset_h, self.window_w, self.window_h)
        current_img = self.original_img.copy(cropped_area)
        self.paper.setPixmap(current_img)

    def _renewOffsetH(self):
        self.offset_h = self.offset_h if self.offset_h + \
            self.window_h < self.img_h else self.img_h - self.window_h
        self.offset_h = self.offset_h if self.offset_h >= 0 else 0

    @pyqtSlot(QKeyEvent)
    def onKeyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_K:
            self.offset_h = self.offset_h - 200
        elif event.key() == Qt.Key_J:
            self.offset_h = self.offset_h + 200
        elif event.key() == Qt.Key_Space:
            self.offset_h = 0

        self._renewCropImg()

        event.accept()

