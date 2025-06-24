# -*- coding: utf-8 -*-
import os
import sys
import time

import datetime
import numpy as np
import pandas as pd
from configparser import ConfigParser

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

from util.helper_func import *


SENSOR_LIST = ['switch', 'slider', 'joystick', 'scroll', 'mouse']


class SensorViewer(QWidget):
    sensor_info_signal = pyqtSignal(object)

    class Table(object):
        def __init__(self, state_list, peak_list, img_dict, peak_range):
            self.state_list = state_list
            self.peak_list = peak_list
            self.img_dict = img_dict
            self.peak_range = peak_range

        def img(self, key):
            return self.img_dict[key]

    def __init__(self, parent, inifile='setting/default.ini', dark_mode=False):
        super().__init__(parent)
        self.winID = parent.winId()

        self.inifile = inifile
        self.parser = ConfigParser()
        self.parser.read(self.inifile)
        self.PEAK_TABLE = {}
        for key in SENSOR_LIST:
            self.PEAK_TABLE[key] = self._createPeakInfoTable(key)

        self.font = QFont('Arial', 12)
        self.sensorFont = QFont('Arial', 20)
        self.boldFont = QFont('Arial', 12)
        self.logFont = QFont('Arial', 10)
        self.boldFont.setBold(True)
        self.status_label_dict, self.status_pic_dict, self.qt_table_dict = {}, {}, {}
        for key in SENSOR_LIST:
            self.status_label_dict[key] = QLabel('{} sensor: none'.format(key))
            self.status_label_dict[key].setFont(self.sensorFont)
            self.status_pic_dict[key] = QLabel()
            self.status_pic_dict[key].setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.status_pic_dict[key].setScaledContents(True)
            self.status_pic_dict[key].setPixmap(
                self.PEAK_TABLE[key].img('none'))
            self.status_pic_dict[key].setScaledContents(True)
            self.qt_table_dict[key] = self._createQtTable(self.PEAK_TABLE[key])

        self.current_sensor = SENSOR_LIST[4]
        self.sensorLayout = QVBoxLayout()
        self.sensorLayout.addWidget(
            self.status_pic_dict[self.current_sensor], stretch=4, alignment=Qt.AlignCenter)
        # self.sensorLayout.addWidget(
        #     self.status_label_dict[self.current_sensor], stretch=2, alignment=Qt.AlignCenter)
        # self.sensorLayout.addWidget(
        #     self.qt_table_dict[self.current_sensor], stretch=3)

        self.comboLabel = QLabel('Choose sensor type:')
        self.comboLabel.setFont(self.boldFont)

        self.sensorComboBox = QComboBox(self)
        self.sensorComboBox.addItems(SENSOR_LIST)
        self.sensorComboBox.setFont(self.boldFont)
        self.sensorComboBox.currentTextChanged.connect(self.changeSensorMode)
        self.sensorComboBox.setEditable(True)
        line_edit = self.sensorComboBox.lineEdit()
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setFont(self.boldFont)
        line_edit.setReadOnly(True)

        self.comboLayout = QHBoxLayout()
        self.comboLayout.addWidget(self.comboLabel, alignment=Qt.AlignRight)
        self.comboLayout.addWidget(
            self.sensorComboBox, alignment=Qt.AlignLeft)

        self.startButton = QPushButton('Start', self)
        self.stopButton = QPushButton('Stop', self)
        self.recordButton = QPushButton('Record', self)
        self.saveButton = QPushButton('Save', self)
        self.startButton.clicked.connect(self.startViewer)
        self.stopButton.clicked.connect(self.stopViewer)
        self.saveButton.clicked.connect(self.saveCurrentSetup)
        self.startButton.setFont(self.font)
        self.stopButton.setFont(self.font)
        self.recordButton.setFont(self.font)
        self.saveButton.setFont(self.font)
        self.startButton.setEnabled(False)

        self.logViewer = QPlainTextEdit(self)
        self.logViewer.setReadOnly(True)
        self.logViewer.setFont(self.logFont)

        self.buttonLayout = QGridLayout()
        self.buttonLayout.addWidget(self.startButton, 0, 0)
        self.buttonLayout.addWidget(self.stopButton, 1, 0)
        self.buttonLayout.addWidget(self.recordButton, 0, 1)
        self.buttonLayout.addWidget(self.saveButton, 1, 1)

        self.controlLayout = QVBoxLayout()
        self.controlLayout.addLayout(self.comboLayout, stretch=1)
        self.controlLayout.addLayout(self.buttonLayout, stretch=3)
        self.controlLayout.addWidget(self.logViewer, stretch=2)
        self.controlLayout.setSpacing(10)

        green = QColor(52, 235, 143)
        blue = QColor(0, 0, 255)
        text = QColor(50, 50, 50) if dark_mode else QColor(10, 10, 10)
        # pg.setConfigOption('foreground', 'k')
        self.timelineGraph = pg.PlotWidget(background=(
            30, 30, 30)) if dark_mode else pg.PlotWidget(background=(250, 250, 255))
        self.timelineGraph.addLegend()
        pen = pg.mkPen(blue, width=7, style=Qt.SolidLine)
        self.peak_timeline = self.timelineGraph.plot(
            [], [], pen=pen, viewbox=None)

        self.peak_scatter_in_timeline = pg.ScatterPlotItem(
            size=20, brush=pg.mkBrush(blue))
        self.timelineGraph.addItem(self.peak_scatter_in_timeline)
        self.timelineGraph.setLabel("left", "Peak (MHz)")
        self.timelineGraph.setLabel("bottom", "Count")
        self.peakLabel = pg.LabelItem(
            'none', size='12pt', color=text)
        self.inst = self.timelineGraph.getPlotItem()
        self.peakLabel.setParentItem(self.inst)
        self.peakLabel.anchor(itemPos=(1, 0), parentPos=(1, 0), offset=(0, 0))

        self.cnt = 0
        self.MAX_CNT = 100
        self.timeline_x = np.arange(0, self.MAX_CNT, 1)
        self.timeline_y = np.zeros(self.MAX_CNT)
        self.peak_timeline.setData(self.timeline_x, self.timeline_y)
        self.timelineGraph.setXRange(0, self.MAX_CNT, padding=0.05)
        self.timelineGraph.showGrid(x=True, y=True)

        self.sensorinfoLayout = QVBoxLayout()
        self.sensorinfoLayout.addLayout(self.sensorLayout, stretch=5)
        self.sensorinfoLayout.addLayout(self.controlLayout, stretch=1)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.sensorinfoLayout, stretch=1)
        self.mainLayout.addWidget(self.timelineGraph, stretch=1)
        self.mainLayout.setSpacing(100)
        self.setLayout(self.mainLayout)

        self.is_running = True
        self.on_viewer = True

        self.statusbar = parent.statusBar()
        self.statusbar.setFont(self.font)

    def _createPeakInfoTable(self, section, dark_mode=False):
        key_list, peak_list = [], []
        img_dict = {}
        peak_range = None
        for key in self.parser[section]:
            if key == 'range':
                peak_range = float(self.parser[section][key])
                continue
            key_list.append(key)
            peak_list.append(float(self.parser[section][key]))

            img = QPixmap("./pictures/{}_{}.png".format(section, key)
                          ).scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_dict[key] = img

        return self.Table(key_list, peak_list, img_dict, peak_range)

    def _createQtTable(self, itable):
        qtable = QTableWidget()
        qtable.setRowCount(1)
        qtable.setColumnCount(len(itable.state_list) + 1)
        header = itable.state_list.copy()
        header.append('range')
        qtable.setHorizontalHeaderLabels(header)
        qtable.setVerticalHeaderLabels(["Freq (MHz)"])
        for i in range(len(itable.state_list)):
            freq = QTableWidgetItem()
            freq.setData(Qt.EditRole, itable.peak_list[i])
            qtable.setItem(0, i, freq)

        peak_range = QTableWidgetItem()
        peak_range.setData(Qt.EditRole, itable.peak_range)
        qtable.setItem(0, len(itable.state_list), peak_range)

        qtable.resizeRowsToContents()
        qtable.resizeColumnsToContents()
        return qtable

    def updateSensorState(self, peak_data):
        if not self.is_running:
            return

        self.statusbar.showMessage('sensor viewer on')

        self.freq = peak_data[0]
        self.peaks = peak_data[1]
        self.target_ids = peak_data[2]
        self.target_freq = self.freq[self.target_ids]

        if len(self.peaks):
            self.peak_freq = self.target_freq[self.peaks]
            self.changeSensorState(self.peak_freq)

        if self.on_viewer:
            self.timelineGraph.setYRange(
                self.freq[0], self.freq[-1], padding=0.05)
            peak = self.target_freq[self.peaks] if len(
                self.peaks) else np.array([self.freq[0]])
            # peak = np.where(peak < 27.8, 27.4, peak)#27.4#
            # peak = np.where(peak > 27.81, 28.45, peak)
            self.timeline_y[self.cnt % self.MAX_CNT] = peak
            self.peak_timeline.setData(self.timeline_x, self.timeline_y)
            self.peak_scatter_in_timeline.setData([self.timeline_x[self.cnt % self.MAX_CNT]],
                                                  [self.timeline_y[self.cnt % self.MAX_CNT]])
            self.peakLabel.setText('{:.2f} MHz'.format(peak[0]))

        self.cnt = self.cnt + 1 if self.cnt < 100000 else 0

    def changeSensorState(self, peaks):
        ncolumn = self.qt_table_dict[self.current_sensor].columnCount()

        # update table
        for column in range(ncolumn):
            freq = self.qt_table_dict[self.current_sensor].item(0, column)
            if column == ncolumn - 1:
                self.PEAK_TABLE[self.current_sensor].peak_range = float(
                    freq.text())
            else:
                self.PEAK_TABLE[self.current_sensor].peak_list[column] = float(
                    freq.text())

        # renew img
        sensor_info = {}
        for sensor in SENSOR_LIST:
            state = self._findState(peaks[0], sensor)
            sensor_info[sensor] = state

        if self.on_viewer:
            self.status_pic_dict[self.current_sensor].setPixmap(
                self.PEAK_TABLE[self.current_sensor].img(sensor_info[self.current_sensor]))
            self.status_pic_dict[self.current_sensor].setScaledContents(True)
            self.status_label_dict[self.current_sensor].setText(
                '{} sensor: {}'.format(self.current_sensor, sensor_info[self.current_sensor]))

        self.sensor_info_signal.emit(sensor_info)

    def startViewer(self, only_update=False):
        self.is_running = True
        self.on_viewer = False if only_update else True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

    def stopViewer(self):
        self.is_running = False
        self.on_viewer = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

    def saveCurrentSetup(self):
        self.is_running = False
        self.saveButton.setEnabled(False)

        now = datetime.datetime.now()
        filename = 'log/peak_screenshot_{}{}{}{}'.format(
            now.month, now.day, now.hour, now.minute)
        self.logViewer.appendPlainText(
            'Saving screenshot and peak data to {}'.format(filename))
        print('Saving screenshot and plot data to {}'.format(filename))

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winID)
        screenshot.save('{}.jpg'.format(filename), 'jpg')

        save_peaks = np.zeros(len(self.freq))

        if len(self.peaks) > 0:
            save_peaks[self.peaks] = 1

        save_data = {'freq': self.freq,
                     'peaks': save_peaks}

        df = pd.DataFrame(save_data, columns=['freq', 'peaks'])
        df.to_csv('{}.csv'.format(filename), index=False)

        updateParser = ConfigParser()
        updateParser.read(self.inifile)
        for sensor in SENSOR_LIST:
            itable = self.PEAK_TABLE[sensor]
            state_list = itable.state_list
            peak_list = itable.peak_list

            for i in range(len(state_list)):
                updateParser[sensor][state_list[i]] = str(peak_list[i])

            updateParser[sensor]['range'] = str(itable.peak_range)

        inipath = 'setting/{}{}{}{}.ini'.format(
            now.month, now.day, now.hour, now.minute)
        with open(inipath, 'w') as configurefile:
            updateParser.write(configurefile)
            self.logViewer.appendPlainText(
                'Saving inifile to {}'.format(inipath))
            print('Saving screenshot and plot data to {}'.format(inipath))

        self.is_running = True
        self.saveButton.setEnabled(True)

    def changeSensorMode(self, sensor):
        self.current_sensor = sensor
        # self.sensorComboBox.setCurrentText(self.current_sensor)
        for i in reversed(range(self.sensorLayout.count())):
            self.sensorLayout.itemAt(i).widget().setParent(None)

        self.sensorLayout.addWidget(
            self.status_pic_dict[self.current_sensor], stretch=5, alignment=Qt.AlignCenter)
        # self.sensorLayout.addWidget(
        #     self.status_label_dict[self.current_sensor], stretch=2, alignment=Qt.AlignCenter)
        # self.sensorLayout.addWidget(
        #     self.qt_table_dict[self.current_sensor], stretch=3)

    def _findState(self, peak, sensor_type):
        itable = self.PEAK_TABLE[sensor_type]
        peak_range = itable.peak_range
        id = findNearestID(array=itable.peak_list, value=peak)
        state = itable.state_list[id] if (
            np.abs(itable.peak_list[id] - peak) < peak_range/2) else 'none'

        return state
