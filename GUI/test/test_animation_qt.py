# -*- coding: utf-8 -*-

import os
import sys
import time
from random import randint

import PyQt5
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from util.peak_detector import *


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # self.statusText.setText("Status: setting up VNA...")
        self.vna = PicoVNA()
        self.font = QFont('Arial', 10)

        self.setWindowTitle("iRing viewer")
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 100, screen.width() - 200, screen.height() - 100)
        self.graphLayout = QVBoxLayout()
        self.graphRaw = pg.PlotWidget()
        self.graphDiff = pg.PlotWidget()
        self.graphLayout.addWidget(self.graphRaw)
        self.graphLayout.addWidget(self.graphDiff)

        self.peaklogText = QLabel("Peak (MHz), SNR (dB):")
        self.peaklogText.setFont(self.font)
        self.peaklogText.setFixedWidth(int(screen.width()/2 - 100))
        self.statusText = QLabel("Status: initializing...")
        self.statusText.setFont(self.font)
        self.buttonLayout = QHBoxLayout()
        self.startButton = QPushButton("Start")
        self.stopButton = QPushButton("Stop")
        self.readerCalibrationButton = QPushButton("Calc base")
        self.sensorCalibrationButton = QPushButton("Scale peak")
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.readerCalibrationButton.clicked.connect(self.calibrate)
        self.buttonLayout.addWidget(self.startButton)
        self.buttonLayout.addWidget(self.stopButton)
        self.buttonLayout.addWidget(self.readerCalibrationButton)
        self.buttonLayout.addWidget(self.sensorCalibrationButton)

        leftLayout = QGridLayout()
        leftLayout.addLayout(self.graphLayout, 1, 0)
        leftLayout.addWidget(self.peaklogText, 2, 0)
        leftLayout.addWidget(self.statusText, 3, 0)
        leftLayout.addLayout(self.buttonLayout, 4, 0)
        mainLayout = QGridLayout()
        mainLayout.addLayout(leftLayout, 1, 0)
        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        self.initGraph()

    def initGraph(self):
        self.graphRaw.addLegend()
        self.graphDiff.addLegend()
        self.freq, self.ave_dB, _ = self.vna.getBaseS21()
        self.freq, self.std_dB, _ = self.vna.getStdS21()
        # styles = {'color': '#fff', 'font-size':'20px'}
        pen = pg.mkPen('b', width=5, style=QtCore.Qt.DashLine)
        self.base_line = self.graphRaw.plot(
            self.freq, self.ave_dB, name='base line', pen=pen)
        pen = pg.mkPen('r', width=5, style=QtCore.Qt.SolidLine)
        self.raw_line = self.graphRaw.plot(
            self.freq, self.ave_dB, name='raw data', pen=pen)
        self.peak_scatter = pg.ScatterPlotItem(
            size=10, brush=pg.mkBrush(30, 255, 35, 255), name='peak')
        self.graphRaw.addItem(self.peak_scatter)
        pen = pg.mkPen('r', width=5, style=QtCore.Qt.SolidLine)
        self.diff_line = self.graphDiff.plot(
            self.freq, [], name='diff data', pen=pen)
        pen = pg.mkPen('b', width=5, style=QtCore.Qt.DashLine)
        self.std_line = self.graphDiff.plot(
            self.freq, self.std_dB, name='standard deviations', pen=pen)
        self.peak_scatter_in_diff = pg.ScatterPlotItem(
            size=10, brush=pg.mkBrush(30, 255, 35, 255), name='peak')
        self.graphDiff.addItem(self.peak_scatter_in_diff)
        self.graphRaw.setLabel("left", "S21 (dBm)")
        self.graphRaw.setLabel("bottom", "Frequency (MHz)")
        self.graphDiff.setLabel("left", "S21 diff (dBm)")
        self.graphDiff.setLabel("bottom", "Frequency (MHz)")

        self.graphRaw.showGrid(x=True, y=True)
        self.graphDiff.showGrid(x=True, y=True)
        base_max = np.max(self.ave_dB)
        base_min = np.min(self.ave_dB)
        self.graphRaw.setYRange(base_min - 1, base_max + 1, padding=0)
        self.graphDiff.setYRange(-0.01, 0.2, padding=0)
        self.graphTimer = QtCore.QTimer()
        self.graphTimer.setInterval(5)
        self.graphTimer.timeout.connect(self.updatePlotData)
        self.graphTimer.start()

    def updatePlotData(self):
        # self.statusText.setText("Status: monitoring...")
        _, raw_dB, _ = self.vna.getS21()
        st = time.time()
        peaks, self.ave_dB, diff_dB, _ = detect_peak_with_polyfit(
            deg=10, thres=0.03, y=raw_dB)
        et = time.time()
        self.statusText.setText('Status: monitoring... , FPS: {:.1f}, Elapsed time of peak deection: {:.1f}ms'.format(
            self.vna.getFPS(), (et-st)*1e3))

        base_max = int(np.max(raw_dB))
        base_min = int(np.min(raw_dB))
        self.graphRaw.setYRange(base_min - 1, base_max + 1, padding=0)

        diff_max = np.max(diff_dB)
        diff_max = max(0.2, diff_max)

        self.graphDiff.setYRange(-0.01, diff_max + 0.1, padding=0)

        self.raw_line.setData(self.freq, raw_dB)
        self.base_line.setData(self.freq, self.ave_dB)
        self.diff_line.setData(self.freq, diff_dB)

        if len(peaks) > 0:
            self.peak_scatter.setData(self.freq[peaks], raw_dB[peaks])
            self.peak_scatter_in_diff.setData(self.freq[peaks], diff_dB[peaks])
            peak_dB_SNR = diff_dB - self.std_dB
            peak_msg = ["({} MHz, {:.3f} dB), ".format(
                self.freq[id], peak_dB_SNR[id]) for id in peaks]
            self.peaklogText.setText("(Peak, SNR): " + " ".join(peak_msg))
            self.updateSensorState(self.freq[peaks])

    def updateSensorState(self, peak_freqs):
        self.tab_input_status.changeJoystickState(peak_freqs)

    def start(self):
        if self.graphTimer.isActive():
            self.stop()

        self.graphTimer.timeout.connect(self.updatePlotData)
        self.graphTimer.start()

    def stop(self):
        self.graphTimer.timeout.disconnect()
        self.graphTimer.stop()

    def calibrate(self):
        self.graphTimer.timeout.disconnect()
        self.graphTimer.stop()
        self.statusText.setText("Status: setting up reader...")
        self.vna.average(ave_num=100)
        self.freq, self.ave_dB, _ = self.vna.getBaseS21()
        _, self.std_dB, _ = self.vna.getStdS21()
        self.base_line.setData(self.freq, self.ave_dB)
        self.std_line.setData(self.freq, self.std_dB)
        base_max = np.max(self.ave_dB)
        base_min = np.min(self.ave_dB)
        self.graphRaw.setYRange(base_min - 2, base_max + 2, padding=0)
        self.graphTimer.timeout.connect(self.updatePlotData)
        self.graphTimer.start()


def main(argv):
    def handler(msg_type, msg_log_context, msg_string):
        pass

    PyQt5.QtCore.qInstallMessageHandler(handler)

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)
