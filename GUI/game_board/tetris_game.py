# -*- coding: utf-8 -*-
import sys
import random

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class TetrisGame(QFrame):
    msgStatusbar = pyqtSignal(str)

    BoardWidth = 12
    BoardHeight = 16
    Speed = 350

    def __init__(self, parent):
        super().__init__(parent)

        self.game_counter = 0
        self.game_counter_up = 0
        self.game_counter_left = 0
        self.game_counter_right = 0
        self.parent = parent
        self.isPaused = True
        self.setStyleSheet('background-color: rgb(10, 10, 10)')
        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False

        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []
        self.clearBoard()
        self.curPiece = None

        self.curPiece = Shape()

    def shapeAt(self, x, y):
        return self.board[(y * self.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * self.BoardWidth) + x] = shape

    def squareWidth(self):
        return self.contentsRect().width() // self.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() // self.BoardHeight

    def start(self):
        """starts game"""
        self.isPaused = False
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard()

        self.msgStatusbar.emit(
            'numLinesRemoved: {}'.format(self.numLinesRemoved))

        self.newPiece()
        self.timer.start(self.Speed, self)

    def pause(self):
        """pauses game"""
        self.isPaused = True
        self.timer.stop()

        self.update()

    def paintEvent(self, event: QPaintEvent):
        """paints all shapes of the game"""

        if self.isPaused:
            return

        painter = QPainter(self)
        rect = self.contentsRect()
        boardTop = rect.bottom() - self.BoardHeight * self.squareHeight()

        for i in range(self.BoardHeight):
            for j in range(self.BoardWidth):
                shape = self.shapeAt(j, self.BoardHeight - i - 1)

                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                                    rect.left() + j * self.squareWidth(),
                                    boardTop + i * self.squareHeight(), shape)

        if self.curPiece.shape() != Tetrominoe.NoShape:

            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                                boardTop + (self.BoardHeight -
                                            y - 1) * self.squareHeight(),
                                self.curPiece.shape())
        painter.end()
        event.accept()

    @pyqtSlot(QKeyEvent)
    def onKeyPressEvent(self, event: QKeyEvent):

        if self.curPiece.shape() == Tetrominoe.NoShape:
            super().keyPressEvent(event)
            return

        if self.isPaused:
            return

        key = event.key()
        self.game_counter = self.game_counter + 1
        if key == Qt.Key_P:
            self.pause()
        elif key == Qt.Key_A:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)
        elif key == Qt.Key_D:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)
        elif key == Qt.Key_W:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)
        elif key == Qt.Key_S:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
        elif key == Qt.Key_Space:
            self.dropDown()

        event.accept()

    def updateState(self, state):
        if state == 'left':
            if self.game_counter_left > 8:
                self.tryMove(self.curPiece, self.curX - 1, self.curY)
                self.game_counter_left = 0
            else:
                self.game_counter_left = self.game_counter_left + 1
        elif state == 'right':
            if self.game_counter_right > 8:
                self.tryMove(self.curPiece, self.curX + 1, self.curY)
                self.game_counter_right = 0
            else:
                self.game_counter_right = self.game_counter_right + 1
        elif state == 'up':
            if self.game_counter_up > 12:
                self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
                self.game_counter_up = 0
            else:
                self.game_counter_up = self.game_counter_up + 1
        # elif state == 'press':
        #     if self.game_counter_up > 8:
        #         self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)
        #         self.game_counter_up = 0
        #     else:
        #         self.game_counter_up = self.game_counter_up + 1
        # elif state == 'up':
        #     if self.game_counter_up > 6:
        #         self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
        #         self.game_counter_up = 0
        #     else:
        #         self.game_counter_up = self.game_counter_up + 1

    def timerEvent(self, event):
        """handles timer event"""
        # if event.timerId() == self.timer.timerId():
        if self.isPaused:
            event.accept()

        if self.isWaitingAfterLine:
            self.isWaitingAfterLine = False
            self.newPiece()
        else:
            self.oneLineDown()

        event.accept()

        # else:
        #    super(Board, self).timerEvent(event)

    def clearBoard(self):
        """clears shapes from the board"""
        self.board = []
        for i in range(self.BoardHeight * self.BoardWidth):
            self.board.append(Tetrominoe.NoShape)

    def dropDown(self):
        newY = self.curY

        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1

        self.pieceDropped()

    def oneLineDown(self):
        """goes one line down with a shape"""

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def pieceDropped(self):
        """after dropping shape, remove full lines and create new shape"""

        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()

    def removeFullLines(self):
        """removes all full lines from the board"""

        numFullLines = 0
        rowsToRemove = []

        for i in range(self.BoardHeight):

            n = 0
            for j in range(self.BoardWidth):
                if self.shapeAt(j, i) != Tetrominoe.NoShape:
                    n = n + 1

            if n == self.BoardWidth:
                rowsToRemove.append(i)

        rowsToRemove.reverse()

        for m in rowsToRemove:

            for k in range(m, self.BoardHeight):
                for l in range(self.BoardWidth):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:
            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msgStatusbar.emit(str(self.numLinesRemoved))

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()
            # self.onPaintEvent()

    def newPiece(self):
        """creates a new shape"""

        self.curPiece.setRandomShape()
        self.curX = self.BoardWidth // 2 + 1
        self.curY = self.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.msgStatusbar.emit("Game over")

    def tryMove(self, newPiece, newX, newY):
        """tries to move a shape"""

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= self.BoardWidth or y < 0 or y >= self.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True

    def drawSquare(self, painter, x, y, shape):
        """draws a square of a shape"""

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)


class Tetrominoe(object):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):
    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):
        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape
        self.setShape(Tetrominoe.NoShape)

    def shape(self):
        """returns shape"""
        return self.pieceShape

    def setShape(self, shape):
        """sets a shape"""
        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):
        """chooses a random shape"""
        self.setShape(random.randint(1, 7))

    def x(self, index):
        """returns x coordinate"""
        return self.coords[index][0]

    def y(self, index):
        """returns y coordinate"""
        return self.coords[index][1]

    def setX(self, index, x):
        """sets x coordinate"""
        self.coords[index][0] = x

    def setY(self, index, y):
        """sets y coordinate"""
        self.coords[index][1] = y

    def minX(self):
        """returns min x value"""
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    def maxX(self):
        """returns max x value"""
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    def minY(self):
        """returns min y value"""
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def maxY(self):
        """returns max y value"""
        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotateLeft(self):
        """rotates shape to the left"""
        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotateRight(self):
        """rotates shape to the right"""
        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result
