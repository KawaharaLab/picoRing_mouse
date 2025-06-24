# -*- coding: utf-8 -*-

import os
import sys
import time

import math
import datetime
import numpy as np
import pandas as pd

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg


class GraphViewer(pg.GraphicsLayoutWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.winID = parent.winId()

        self.font = QFont('Arial', 15)

        self.setStyleSheet(
            "QWidget {background-color: rgb(30,30,30); color: rgb(220, 230, 230)}"
            "QPushButton:disabled {color: rgb(190, 200, 200); background-color: rgb(5, 5, 5)}")

        self.rawGraph = pg.PlotWidget(background=(40, 40, 40))
        self.diffGraph = pg.PlotWidget(background=(40, 40, 40))
        self.timelineGraph = pg.PlotWidget(background=(40, 40, 40))

        self.defaultGraphLayout = QHBoxLayout()
        # self.defaultGraphLayout.setSpacing(50)
        self.defaultGraphLayout.addWidget(self.rawGraph)
        self.defaultGraphLayout.addWidget(self.diffGraph)
        self.defaultGraphLayout.addWidget(self.timelineGraph)

        self.startButton = QPushButton("Start", self)
        self.stopButton = QPushButton("Stop", self)
        self.recordButton = QPushButton("Record", self)
        self.saveButton = QPushButton("Save", self)
        self.startButton.clicked.connect(self.startPlot)
        self.stopButton.clicked.connect(self.stopPlot)
        self.saveButton.clicked.connect(self.saveCurrentPlot)
        self.recordButton.clicked.connect(self.recordS21Data)
        self.startButton.setEnabled(False)
        self.startButton.setFont(self.font)
        self.stopButton.setFont(self.font)
        self.saveButton.setFont(self.font)
        self.recordButton.setFont(self.font)

        self.buttonLayout = QGridLayout()
        self.buttonLayout.addWidget(self.startButton, 0, 0)
        self.buttonLayout.addWidget(self.stopButton, 1, 0)
        self.buttonLayout.addWidget(self.recordButton, 0, 1)
        self.buttonLayout.addWidget(self.saveButton, 1, 1)

        self.rawGraphCheckBox = QCheckBox("Show graph output")
        self.diffGraphCheckBox = QCheckBox("Show graph output change")
        self.timelineGraphCheckBox = QCheckBox("Show graph timeline")
        self.rawGraphCheckBox.setChecked(True)
        self.diffGraphCheckBox.setChecked(True)
        self.timelineGraphCheckBox.setChecked(True)
        self.rawGraphCheckBox.stateChanged.connect(self.changeGraphLayout)
        self.diffGraphCheckBox.stateChanged.connect(self.changeGraphLayout)
        self.timelineGraphCheckBox.stateChanged.connect(self.changeGraphLayout)
        self.rawGraphCheckBox.setFont(self.font)
        self.diffGraphCheckBox.setFont(self.font)
        self.timelineGraphCheckBox.setFont(self.font)

        self.graphCheckBoxLayout = QVBoxLayout()
        self.graphCheckBoxLayout.addWidget(self.rawGraphCheckBox)
        self.graphCheckBoxLayout.addWidget(self.diffGraphCheckBox)
        self.graphCheckBoxLayout.addWidget(self.timelineGraphCheckBox)

        self.peaklogText = QLabel("Peak (MHz), SNR (dB):")
        self.peaklogText.setFont(self.font)
        self.statusText = QLabel("Status: initializing...")
        self.statusText.setFont(self.font)
        self.logLayout = QVBoxLayout()
        self.logLayout.addWidget(self.peaklogText)
        self.logLayout.addWidget(self.statusText)

        self.toolLayout = QHBoxLayout()
        self.toolLayout.addLayout(self.buttonLayout)
        self.toolLayout.addLayout(self.graphCheckBoxLayout)
        self.toolLayout.addLayout(self.logLayout)

        mainLayout = QGridLayout()
        mainLayout.addLayout(self.defaultGraphLayout, 0, 0)
        mainLayout.addLayout(self.toolLayout, 1, 0)
        self.setLayout(mainLayout)

        self.S21_log_data = []
        self.MAX_LOG_CNT = 200
        self.is_running = False
        self.is_recording = False

        self.statusbar = parent.statusBar()
        self.statusbar.setFont(self.font)

        self.initGraph()

    def initGraph(self):
        self.rawGraph.addLegend()
        self.diffGraph.addLegend()
        self.timelineGraph.addLegend()

        blue = QColor(52, 73, 235)
        red = QColor(235, 52, 103, 150)
        green = QColor(52, 235, 143)
        pen = pg.mkPen(blue, width=5, style=Qt.DashLine)
        self.base_line = self.rawGraph.plot([], [], name='base', pen=pen)

        pen = pg.mkPen(red, width=5, style=Qt.SolidLine)
        self.raw_line = self.rawGraph.plot([], [], name='raw', pen=pen)

        self.peak_scatter = pg.ScatterPlotItem(
            size=10, brush=pg.mkBrush(green), name='peak')
        self.rawGraph.addItem(self.peak_scatter)

        pen = pg.mkPen(blue, width=7, style=Qt.DashLine)
        self.diff_w_filter_line = self.diffGraph.plot(
            [], [], name='filtered diff', pen=pen)

        pen = pg.mkPen(red, width=7, style=Qt.SolidLine)
        self.diff_line = self.diffGraph.plot(
            [], [], name='raw diff', pen=pen)

        self.peak_scatter_in_diff = pg.ScatterPlotItem(
            size=20, brush=pg.mkBrush(green), name='peak')
        self.diffGraph.addItem(self.peak_scatter_in_diff)

        pen = pg.mkPen(green, width=5, style=Qt.SolidLine)
        self.peak_timeline = self.timelineGraph.plot([], [], pen=pen)
        self.peak_scatter_in_timeline = pg.ScatterPlotItem(
            size=20, brush=pg.mkBrush(green))
        self.timelineGraph.addItem(self.peak_scatter_in_timeline)

        self.rawGraph.setTitle('Output of readout board')
        self.rawGraph.setLabel("left", "S21 (dB)")
        self.rawGraph.setLabel("bottom", "Frequency (MHz)")

        self.diffGraph.setTitle('Peak in output')
        self.diffGraph.setLabel("left", "S21 diff (dB)")
        self.diffGraph.setLabel("bottom", "Frequency (MHz)")

        self.timelineGraph.setTitle('Peak timeline')
        self.timelineGraph.setLabel("left", "Peak (MHz)")
        self.timelineGraph.setLabel("bottom", "Count")

        self.cnt = 0
        self.MAX_CNT = 50
        self.timeline_x = np.arange(0, self.MAX_CNT, 1)
        self.timeline_y = np.zeros(self.MAX_CNT)
        self.peak_timeline.setData(self.timeline_x, self.timeline_y)
        self.timelineGraph.setXRange(0, self.MAX_CNT, padding=0.05)
        self.rawGraph.showGrid(x=True, y=True)
        self.diffGraph.showGrid(x=True, y=True)
        self.timelineGraph.showGrid(x=True, y=True)

        self.is_running = True

    def updateGraph(self, s21_data):
        if not self.is_running:
            return

        self.statusbar.showMessage('graph viewer on')
        # Get signal from util/qt_vna.py
        self.freq = s21_data[0]
        self.raw_dB = s21_data[1]
        self.base_dB = s21_data[2]
        self.diff_dB = s21_data[3]
        self.diff_w_filter_dB = s21_data[4]
        self.peaks = s21_data[5]
        self.vna_fps = s21_data[6]
        self.target_ids = s21_data[7]
        self.thres = s21_data[8]

        self.target_freq = self.freq[self.target_ids]

        if self.is_recording:
            if len(self.S21_log_data) < self.MAX_LOG_CNT:
                self.S21_log_data.append(self.raw_dB)
            else:
                self._saveS21LogtoFile()

        st = time.time()

        if self.rawGraphCheckBox.isChecked():
            base_max = 2 * math.ceil(np.max(self.raw_dB)/2)
            base_min = 2 * math.floor(np.min(self.raw_dB)/2)
            self.rawGraph.setXRange(self.freq[0], self.freq[-1], padding=0.05)
            self.rawGraph.setYRange(base_min - 1, base_max + 1, padding=0.01)
            self.raw_line.setData(self.freq, self.raw_dB)
            self.base_line.setData(self.target_freq, self.base_dB)
            if len(self.peaks) > 0:
                self.target_raw_dB = self.raw_dB[self.target_ids]
                self.peak_scatter.setData(
                    self.target_freq[self.peaks], self.target_raw_dB[self.peaks])
            else:
                self.peak_scatter.setData([], [])

        if self.diffGraphCheckBox.isChecked():
            diff_max = max(np.max(self.diff_w_filter_dB), np.max(self.diff_dB))
            diff_max = 0.2 * math.ceil(diff_max/0.2)
            self.diffGraph.setXRange(
                self.target_freq[0], self.target_freq[-1], padding=0.05)
            self.diffGraph.setYRange(0, diff_max, padding=0.01)
            self.diff_line.setData(self.target_freq, self.diff_dB)
            self.diff_w_filter_line.setData(
                self.target_freq, self.diff_w_filter_dB)
            if len(self.peaks) > 0:
                self.peak_scatter_in_diff.setData(
                    self.target_freq[self.peaks], self.diff_w_filter_dB[self.peaks])
            else:
                self.peak_scatter_in_diff.setData([], [])

        if self.timelineGraphCheckBox.isChecked():
            self.timelineGraph.setYRange(
                self.target_freq[0], self.target_freq[-1], padding=0.05)
            self.timeline_y[self.cnt %
                            self.MAX_CNT] = self.target_freq[self.peaks] if len(self.peaks) else self.freq[0]
            self.peak_timeline.setData(self.timeline_x, self.timeline_y)
            self.peak_scatter_in_timeline.setData([self.timeline_x[self.cnt %
                                                                   self.MAX_CNT]], [self.timeline_y[self.cnt %
                                                                                                    self.MAX_CNT]])
            self.cnt = self.cnt + 1 if self.cnt < 100000 else 0

        elapsed = time.time()-st
        self.draw_fps = 1/(elapsed) if (elapsed > 0) else 1000

        self.statusText.setText(
            'VNA FPS: {:.0f}, Draw FPS: {:.0f}'.format(self.vna_fps, self.draw_fps))
        if len(self.peaks) > 0:
            peak_msg = ["({} MHz, {:.3f} dB), ".format(
                self.target_freq[id], self.diff_dB[id]) for id in self.peaks]
            self.peaklogText.setText("(Peak): " + " ".join(peak_msg))

    def changeGraphLayout(self):
        self.is_running = False
        for i in reversed(range(self.defaultGraphLayout.count())):
            self.defaultGraphLayout.itemAt(i).widget().setParent(None)

        cnt = 0
        if self.rawGraphCheckBox.isChecked():
            self.defaultGraphLayout.addWidget(self.rawGraph, stretch=1)
            cnt = cnt + 1

        if self.diffGraphCheckBox.isChecked():
            self.defaultGraphLayout.addWidget(
                self.diffGraph, stretch=1)
            cnt = cnt + 1

        if self.timelineGraphCheckBox.isChecked():
            self.defaultGraphLayout.addWidget(
                self.timelineGraph, stretch=1)
            cnt = cnt + 1

        if cnt == 0:
            emptyGraph = pg.PlotWidget()
            self.defaultGraphLayout.addWidget(emptyGraph)

        self.is_running = True

    def startPlot(self):
        self.is_running = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

    def _saveS21LogtoFile(self):
        if not self.is_recording:
            return

        now = datetime.datetime.now()
        filename = 'log/s21_type1_on_{}{}{}{}'.format(
            now.month, now.day, now.hour, now.minute)
        np.save(filename, self.S21_log_data)
        self.S21_log_data = []
        self.is_recording = False
        self.recordButton.setEnabled(True)

    def stopPlot(self):
        self.is_running = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self._saveS21LogtoFile()

    def saveCurrentPlot(self):
        self.is_running = False
        self.saveButton.setEnabled(False)

        now = datetime.datetime.now()
        filename = 'log/graph_screenshot_{}{}{}{}'.format(
            now.month, now.day, now.hour, now.minute)
        self.statusText.setText(
            'Saving screenshot and plot data to {}'.format(filename))
        print('Saving screenshot and plot data to {}'.format(filename))

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winID)
        screenshot.save(filename + '.jpg', 'jpg')

        save_base_dB = np.zeros(len(self.freq))
        save_diff_dB = np.zeros(len(self.freq))
        save_diff_w_filter_dB = np.zeros(len(self.freq))
        save_peaks = np.zeros(len(self.freq))
        save_base_dB[self.target_ids] = self.base_dB
        save_diff_dB[self.target_ids] = self.diff_dB
        save_diff_w_filter_dB[self.target_ids] = self.diff_w_filter_dB

        if len(self.peaks) > 0:
            save_peaks[self.peaks] = 1

        raw_data = {'freq': self.freq,
                    'raw_dB': self.raw_dB,
                    'base_dB': save_base_dB,
                    'diff_dB': save_diff_dB,
                    'filtered_diff_dB': save_diff_w_filter_dB,
                    'peaks': save_peaks}

        df = pd.DataFrame(raw_data, columns=['freq', 'raw_dB', 'base_dB',
                                             'diff_dB', 'filtered_diff_dB', 'peaks'])
        df.to_csv(filename + '.csv', index=False)

        self.is_running = True
        self.saveButton.setEnabled(True)

    def recordS21Data(self):
        self.is_recording = True
        self.recordButton.setEnabled(False)
        self.S21_log_data.append(self.freq)

