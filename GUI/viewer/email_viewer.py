# -*- coding: utf-8 -*-

import os
import sys
import time

import math
import datetime
import numpy as np
import pandas as pd
from configparser import ConfigParser

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class EmailViewer(QWidget):

    def __init__(self, parent, inifile='setting/default.ini'):
        super().__init__(parent)
        self.winID = parent.winId()
        self.statusbar = parent.statusBar()

        self.image_paths = [
        "./email/Email1.png",
        "./email/Email2.png",
        "./email/Email3.png",
        "./email/Email4.png",
        "./email/Email5.png",
        "./email/Email6.png",
        "./email/Email7.png",
        "./email/Email8.png",
    ]
        self.current_index = 1

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)
        self.email_counter_next = 0
        self.email_counter_pre = 0

    def updateEmailPos(self, sensor_info):

        scroll_state = sensor_info['mouse']
        self.statusbar.showMessage('scroll state: {}'.format(scroll_state))

        if scroll_state == 'none':
            return

        #self.scroll_pic.setPixmap(self.img_dict[scroll_state])

        if scroll_state == 'left' or scroll_state == 'press':
            if self.email_counter_pre > 70:
                self.showPreviousPage()
                print('left')
                self.email_counter_pre = 0
            else:
                self.email_counter_pre = self.email_counter_pre + 1

        #elif scroll_state == 'right' or scroll_state == 'up' or scroll_state == 'down':

        elif scroll_state == 'right':
            if self.email_counter_next > 70:
                self.showNextPage()
                print('right')
                self.email_counter_next = 0
            else:
                self.email_counter_next = self.email_counter_next + 1

    def updateImage(self):
        if 0 <= self.current_index < len(self.image_paths):
            pixmap = QPixmap(self.image_paths[self.current_index])
            fixed_size = QSize(800, 1600)  # Example fixed size
            # Scale the pixmap to the fixed size, preserving the aspect ratio
            scaled_pixmap = pixmap.scaled(fixed_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Set the scaled pixmap to the label
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("No Image Available")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.showPreviousPage()
        elif event.key() == Qt.Key_Right:
            self.showNextPage()

    def showPreviousPage(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.updateImage()

    def showNextPage(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.updateImage()

    @pyqtSlot(QKeyEvent)
    def onKeyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Left:
            self.showPreviousPage()
        elif event.key() == Qt.Key_Right:
            self.showNextPage()
        elif event.key() == Qt.Key_Up:
            self.showNextPage()
        elif event.key() == Qt.Key_Down:
            self.showNextPage()

        event.accept()
