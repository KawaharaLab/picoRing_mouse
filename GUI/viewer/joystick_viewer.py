# -*- coding: utf-8 -*-
import sys
import random

from configparser import ConfigParser

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from game_board.snake_game import *
from game_board.tetris_game import *


class JoystickViewer(QWidget):

    GAME_LIST = ['snake', 'tetris']

    def __init__(self, parent, inifile='setting/default.ini'):
        super().__init__(parent)

        self.font = QFont('Arial', 24)
        self.boldFont = QFont('Arial', 24)

        self.window_geometry = parent.geometry()
        self.window_w, self.window_h = self.window_geometry.width(
        ), self.window_geometry.height()
        img_size = 500
        self.img_rect = QRect(self.window_w - img_size + 200,
                              100, img_size, img_size)

        self.game_board = {}
        self.current_game = 'snake'
        self.gameLayout = QVBoxLayout()
        self.game_board['snake'] = SnakeGame(self)
        self.game_board['tetris'] = TetrisGame(self)
        self.gameLayout.addWidget(
            QFrame(self), alignment=Qt.AlignVCenter)

        self.startButton = QPushButton('Start')
        self.stopButton = QPushButton('Stop')
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.pause)
        self.startButton.setFont(self.font)
        self.stopButton.setFont(self.font)
        self.stopButton.setEnabled(False)

        self.gameLabel = QLabel('Select game: ')
        self.gameLabel.setFont(self.font)
        self.gameComboBox = QComboBox()
        self.gameComboBox.setFont(self.boldFont)
        self.gameComboBox.addItems(self.GAME_LIST)
        self.gameComboBox.setCurrentText(self.current_game)
        self.gameComboBox.currentTextChanged.connect(self.changeGame)
        self.gameComboBox.setEditable(True)
        line_edit = self.gameComboBox.lineEdit()
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setFont(self.boldFont)
        line_edit.setReadOnly(True)

        self.parser = ConfigParser()
        self.parser.read(inifile)
        section = 'mouse'
        self.img_dict = {}
        for key in self.parser[section]:
            if key == 'range':
                continue
            img = QImage("./pictures/{}_{}.png".format(section, key))
            self.img_dict[key] = img

        self.joystick_state = 'none'

        self.toolLayout = QVBoxLayout()
        self.toolLayout.addWidget(
            self.gameLabel, alignment=Qt.AlignLeft | Qt.AlignBottom)
        self.toolLayout.addWidget(self.gameComboBox, alignment=Qt.AlignLeft)
        self.toolLayout.addWidget(self.startButton)
        self.toolLayout.addWidget(self.stopButton)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(self.gameLayout, stretch=4)
        mainLayout.addLayout(self.toolLayout, stretch=1)
        self.setLayout(mainLayout)

        self.statusbar = parent.statusBar()
        for game in self.GAME_LIST:
            self.game_board[game].msgStatusbar[str].connect(
                self.statusbar.showMessage)

        self.changeGame(self.current_game)

    def start(self):
        screen = self.gameLayout.geometry()
        game_screen = QRect()
        if self.current_game == 'snake':
            game_screen = QRect(
                int((screen.width() - screen.height())/2), screen.top(),
                screen.height()*0.75, screen.height())
        elif self.current_game == 'tetris':
            game_screen = QRect(
                int((screen.width() - screen.height()/2)/2), screen.top(),
                screen.height()*0.75, screen.height())
        self.game_board[self.current_game].setGeometry(game_screen)
        self.game_board[self.current_game].start()

        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)

    def pause(self):
        self.game_board[self.current_game].pause()
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)

    def updateJoystickState(self, sensor_info):
        self.joystick_state = sensor_info['mouse']
        self.statusbar.showMessage(
            'joystick state: {}'.format(self.joystick_state))
        self.game_board[self.current_game].updateState(self.joystick_state)
        self.update()

    @ pyqtSlot(QKeyEvent)
    def onKeyPressEvent(self, event: QKeyEvent):
        self.game_board[self.current_game].onKeyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.img_rect,
                          self.img_dict[self.joystick_state])
        event.accept()

    def changeGame(self, game):
        self.game_board[self.current_game].pause()
        self.current_game = game

        for i in reversed(range(self.gameLayout.count())):
            self.gameLayout.itemAt(i).widget().setParent(None)

        self.gameLayout.addWidget(
            self.game_board[self.current_game], alignment=Qt.AlignCenter)
        self.pause()
