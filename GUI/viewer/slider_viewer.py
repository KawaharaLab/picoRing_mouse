# -*- coding: utf-8 -*-

import os
import sys
import time

from configparser import ConfigParser

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


class SliderViewer(QWidget):

    def __init__(self, parent, inifile='default.ini'):
        super(SliderViewer, self).__init__(parent)

        self.statusbar = parent.statusBar()

        btnSize = QSize(16, 16)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        self.playButton.setEnabled(True)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(videoWidget)

        self.parser = ConfigParser()
        self.parser.read(inifile)
        section = 'slider'
        self.img_dict = {}
        for key in self.parser[section]:
            if key == 'range':
                continue
            img = QPixmap("./pictures/{}_{}.png".format(section, key))
            self.img_dict[key] = img

        self.slider_pic = QLabel()
        self.slider_pic.setPixmap(self.img_dict['none'])

        self.videoLayout = QVBoxLayout()
        self.videoLayout.addWidget(videoWidget, stretch=3)
        self.videoLayout.addLayout(controlLayout, stretch=2)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(
            self.slider_pic, alignment=Qt.AlignCenter | Qt.AlignTop, stretch=1)
        self.mainLayout.addLayout(self.videoLayout, stretch=4)

        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        self.setLayout(self.mainLayout)

        self.statusbar.showMessage('Ready to play {}'.format(
            QFileInfo('picoRing_mouse_v2.mp4').absoluteFilePath()))

        # self.mediaPlayer.setMedia(QMediaContent(
        #     QUrl.fromLocalFile(QFileInfo('picoRing_mouse_v2.mp4').absoluteFilePath())))
        self.mediaPlayer.setMedia(QMediaContent(
            QUrl.fromLocalFile('/Users/faner/picoRing_GUI_with_VNA_v5/video/picoRing_mouse_v2.mp4')))

        self.slider_state_pre = None

    def pause(self):
        self.mediaPlayer.pause()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

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
        elif event.key() == Qt.Key_J:
            pos = self.positionSlider.value()
            self.setPosition(pos - 1000)
        elif event.key() == Qt.Key_K:
            pos = self.positionSlider.value()
            self.setPosition(pos + 1000)

    def updateVideoState(self, sensor_info):
        slider_state = sensor_info['slider']
        self.statusbar.showMessage('slider state: {}'.format(slider_state))
        if self.slider_state_pre == None:
            self.slider_state_pre = slider_state
            return

        if slider_state == 'press' and self.slider_state_pre == 'none':
            self.play()
            #print('test')
            time.sleep(0.4)
        # elif slider_state == 'strong_left':
        #     pos = self.positionSlider.value()
        #     self.setPosition(pos - 2000)
        # elif slider_state == 'strong_right':
        #     pos = self.positionSlider.value()
        #     self.setPosition(pos + 2000)
        # elif slider_state == 'weak_left':
        #     pos = self.positionSlider.value()
        #     self.setPosition(pos - 1000)
        # elif slider_state == 'weak_right':
        #     pos = self.positionSlider.value()
        #     self.setPosition(pos + 1000)

        self.slider_pic.setPixmap(self.img_dict[slider_state])
        self.slider_state_pre = slider_state
