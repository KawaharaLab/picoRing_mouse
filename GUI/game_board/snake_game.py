# -*- coding: utf-8 -*-
import os
import sys
import random

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SnakeGame(QFrame):
    msgStatusbar = pyqtSignal(str)
    # speed of the snake
    SPEED = 200
    # block width and height
    WIDTHINBLOCKS = 20*0.75
    HEIGHTINBLOCKS = 20

    def __init__(self, parent):
        super().__init__(parent)

        self.isPaused = True
        self.setStyleSheet('background-color: black')

        self.timer = QBasicTimer()
        self._initSnake()
        self.drop_food()

    def _initSnake(self):
        self.snake = [[1, 10], [1, 11], [1, 12], [1, 13], [1, 14], [1, 15]]
        self.current_x_head = self.snake[0][0]
        self.current_y_head = self.snake[0][1]
        self.grow_snake = False
        self.direction = 1
        self.food = []  # food list

    def square_width(self):
        return self.contentsRect().width() / self.WIDTHINBLOCKS

    def square_height(self):
        return self.contentsRect().height() / self.HEIGHTINBLOCKS

    # start method
    def start(self):
        # self.setStyleSheet('background-color: (20, 20, 20)')
        # self.setFocusPolicy(Qt.StrongFocus)
        self.isPaused = False
        self._initSnake()
        self.drop_food()
        self.msgStatusbar.emit(
            '[snake game] score: {}'.format(len(self.snake)))
        self.timer.start(self.SPEED, self)

    def pause(self):
        self.timer.stop()
        self.isPaused = True
        # self.setFocusPolicy(Qt.NoFocus)

    # paint event
    def paintEvent(self, event):
        if self.isPaused:
            return

        painter = QPainter(self)
        rect = self.contentsRect()
        boardtop = rect.bottom() - self.HEIGHTINBLOCKS * self.square_height()

        # drawing snake
        for pos in self.snake:
            self.draw_square(painter, rect.left() + pos[0] * self.square_width(),
                             boardtop + pos[1] * self.square_height())

        # drawing food
        for pos in self.food:
            self.draw_square(painter, rect.left() + pos[0] * self.square_width(),
                             boardtop + pos[1] * self.square_height())

        painter.end()
        event.accept()

    # drawing square
    def draw_square(self, painter, x, y):
        color = QColor(0x228B22)
        # painting rectangle
        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color)

    def updateState(self, state):
        if state == 'left':
            self.direction = 1
        elif state == 'right':
            self.direction = 2
        elif state == 'down':
            self.direction = 3
        elif state == 'up':
            self.direction = 4

    @pyqtSlot(QKeyEvent)
    def onKeyPressEvent(self, event: QKeyEvent):
        if self.isPaused:
            event.accept()

        key = event.key()
        if key == Qt.Key_A:
            self.direction = 1
        elif key == Qt.Key_D:
            self.direction = 2
        elif key == Qt.Key_S:
            self.direction = 3
        elif key == Qt.Key_W:
            self.direction = 4
        event.accept()

    def moveSnake(self):
        # if direction is left change its position
        if self.direction == 1:
            self.current_x_head = self.current_x_head - 1 \
                if self.current_x_head != 0 else self.WIDTHINBLOCKS - 1

        # if direction is right change its position
        if self.direction == 2:
            self.current_x_head = self.current_x_head + 1 \
                if self.current_x_head != self.WIDTHINBLOCKS else 0

        # if direction is down change its position
        if self.direction == 3:
            self.current_y_head = self.current_y_head + 1 \
                if self.current_y_head != self.HEIGHTINBLOCKS else 0

        # if direction is up change its position
        if self.direction == 4:
            self.current_y_head = self.current_y_head - 1 \
                if self.current_y_head != 0 else self.HEIGHTINBLOCKS

        # changing head position
        head = [self.current_x_head, self.current_y_head]
        self.snake.insert(0, head)

        # if snake grow is False
        if not self.grow_snake:
            self.snake.pop()
        else:
            self.msgStatusbar.emit(str(len(self.snake)-2))
            self.grow_snake = False

    # time event method
    def timerEvent(self, event):
        if self.isPaused:
            return

        self.moveSnake()
        self.is_food_collision()
        # self.is_suicide()
        self.update()
        event.accept()

    # method to check if snake collides itself
    def is_suicide(self):
        # traversing the snake
        for i in range(1, len(self.snake)):
            # if collision found
            if self.snake[i] == self.snake[0]:
                self.msgStatusbar.emit("Game Ended")
                self.setStyleSheet('background-color: red')
                self.timer.stop()
                self.update()
                print('game end')
                self.pause()

    def is_food_collision(self):
        # traversing the position of the food
        for pos in self.food:
            # if food position is similar of snake position
            if pos == self.snake[0]:
                self.food.remove(pos)
                self.drop_food()
                self.grow_snake = True

    # method to drop food on screen
    def drop_food(self):
        # creating random co-ordinates
        x = random.randint(3, self.WIDTHINBLOCKS - 3)
        y = random.randint(3, self.HEIGHTINBLOCKS - 3)

        # traversing if snake position is not equal to the
        # food position so that food do not drop on snake
        for pos in self.snake:
            # if position matches
            if pos == [x, y]:
                self.drop_food()

        # append food location
        self.food.append([x, y])
