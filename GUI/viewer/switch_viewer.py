# -*- coding: utf-8 -*-

import os
import sys
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


class SwitchViewer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.statusbar = parent.statusBar()

        btnSize = QSize(700, 700)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIconSize(btnSize)
        # self.playButton.setStyleSheet(
        #    'background-image: url(pictures/music_off.png)')
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        self.playButton.setEnabled(True)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(
            self.playButton, stretch=5, alignment=Qt.AlignCenter)
        self.mainLayout.addWidget(self.positionSlider, stretch=1)

        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        self.setLayout(self.mainLayout)

        self.statusbar.showMessage('Ready to play {}'.format(
            QFileInfo('music/test.wav').absoluteFilePath()))

        self.mediaPlayer.setMedia(QMediaContent(
            QUrl.fromLocalFile(QFileInfo('music/test.wav').absoluteFilePath())))

        self.mediaPlayer.setPlaybackRate(1.3)

        self.switch_on_cnt = 0
        self.pre_switch_state = None

    def pause(self):
        self.mediaPlayer.pause()

    def play(self):
        # self.playButton.setStyleSheet('')
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            # self.playButton.setStyleSheet(
            #    'background-image: url(pictures/music_off.png)')
        else:
            self.mediaPlayer.play()
            # self.playButton.setStyleSheet(
            #    'background-image: url(pictures/music_on.png)')

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        error_msg = '[error] {}'.format(self.mediaPlayer.errorString())
        self.statusbar.showMessage(error_msg)
        print(error_msg)

    @pyqtSlot(QKeyEvent)
    def onKeyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space:
            self.play()
        elif event.key() == Qt.Key_R:
            self.setPosition(position=0)

    def updateMusicState(self, sensor_info):
        switch_state = sensor_info['mouse']
        self.statusbar.showMessage('switch state: {}'.format(switch_state))

        if self.pre_switch_state == None:
            self.pre_switch_state = switch_state
            return

        if switch_state == 'press': #on
            self.switch_on_cnt = self.switch_on_cnt + 1
            if self.switch_on_cnt > 10:
                self.play()
                self.switch_on_cnt = 0
            return

        if switch_state == 'none': #off
            # self.setPosition(position=0)
            # if self.switch_on_cnt > 100:
            #     self.setPosition(position=0)
            # elif self.switch_on_cnt > 2:
            #     self.play()
            #     self.switch_on_cnt = 0
            print(self.switch_on_cnt)

            #self.switch_on_cnt = 0
