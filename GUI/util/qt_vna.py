# -*- coding: utf-8 -*-
import os
import sys
import time
from configparser import ConfigParser

import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from superqt import QLabeledDoubleRangeSlider

from util.peak_detector import *
from util.nanovna import NanoVNA


class QtVNA(QWidget):

    s21_signal = pyqtSignal(object)
    peak_signal = pyqtSignal(object)

    def __init__(self, parent=None, inifile=None, logfile=None):
        super().__init__(parent)

        self.s21_data = None
        self.is_running = False

        self.inifile = inifile
        self.logfile = logfile

        self.font = QFont('Arial', 10)
        self.logfont = QFont('Arial', 10)
        self.freq_range_label = QLabel("Set target frequency range (MHz)")
        self.freq_range_label.setFont(self.font)

        self.freq_range_slider = QLabeledDoubleRangeSlider(
            Qt.Orientation.Horizontal, self)
        self.freq_range_slider.setFont(self.font)

        self.freqRangeLayout = QHBoxLayout()
        self.freqRangeLayout.setSpacing(100)
        self.freqRangeLayout.addWidget(
            self.freq_range_label, stretch=1, alignment=Qt.AlignRight)
        self.freqRangeLayout.addWidget(self.freq_range_slider, stretch=3)

        self.threshold_label = QLabel("Set peak threshold (dB)")
        self.threshold_label.setFont(self.font)

        self.thres = 0.03
        self.threshold_slider = QLabeledDoubleRangeSlider(
            Qt.Orientation.Horizontal, self)
        self.threshold_slider.setFont(self.font)
        self.threshold_slider.setRange(0.0, 0.1)
        self.threshold_slider.setSingleStep(0.01)
        self.threshold_slider.setValue((0.00, self.thres))
        self.threshold_slider.setDecimals(3)
        self.threshold_slider.valueChanged.connect(
            lambda range: self.setThres(range))

        self.thresRangeLayout = QHBoxLayout()
        self.thresRangeLayout.setSpacing(100)
        self.thresRangeLayout.addWidget(
            self.threshold_label, stretch=1, alignment=Qt.AlignRight)
        self.thresRangeLayout.addWidget(
            self.threshold_slider, stretch=3)

        self.log_viewer = QPlainTextEdit(self)
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(self.logfont)

        self.rangeLayout = QVBoxLayout()
        self.rangeLayout.addLayout(self.freqRangeLayout)
        self.rangeLayout.addLayout(self.thresRangeLayout)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setSpacing(100)
        self.mainLayout.addLayout(self.rangeLayout, stretch=1)
        self.mainLayout.addWidget(self.log_viewer, stretch=3)
        self.setLayout(self.mainLayout)

        self.statusbar = parent.statusBar()
        self.statusbar.setFont(self.font)

    def initVNA(self):
        self.vna = None
        print('Open VNA')
        if self.logfile:
            self._initLogVNA()
        else:
            self._initPicoVNA()
        time.sleep(1)
        self.is_running = True

        self.freq_range_slider.setRange(self.start_freq, self.end_freq)
        self.freq_range_slider.setSingleStep(self.freq_step)
        self.freq_range_slider.setValue((self.start_freq, self.end_freq))
        self.freq_range_slider.setDecimals(1)
        self.freq_range_slider.valueChanged.connect(
            lambda range: self.setFreqRange(range))

    def _initLogVNA(self):
        self.S21_log_data = np.load(self.logfile)
        self.log_viewer.appendPlainText("Replaying {}".format(self.logfile))
        self.freq = self.S21_log_data[0]
        self.start_freq = self.now_start_freq = self.freq[0]
        self.end_freq = self.now_end_freq = self.freq[-1]
        self.freq_step = self.freq[1] - self.freq[0]
        self.step_num = len(self.freq)
        self.log_cnt = 1
        self.MAX_LOG_CNT = len(self.S21_log_data)


    def _initZNBVNA(self):
        self.parser = ConfigParser()
        self.parser.read(self.inifile)

        self.start_freq = self.now_start_freq = self.parser.getfloat(
            'VNA', 'start_freq')
        self.freq_step = self.parser.getfloat('VNA', 'freq_step')
        self.step_num = self.parser.getint('VNA', 'step_num')
        self.input_power = self.parser.getint('VNA', 'input_power')
        self.bandwidth = self.parser.getint('VNA', 'bandwidth')
        self.end_freq = self.now_end_freq = self.start_freq + \
            self.freq_step * (self.step_num - 1)
        self.freq = np.arange(
            self.start_freq, self.end_freq + self.freq_step/2, self.freq_step)
        self.dB, self.base_dB, self.diff_dB, self.diff_dB_w_filter, self.std_dB, self.peaks = \
            None, None, None, None, None, None
        self.fps = 0

        self.vna = VnaZnb("TCPIP::169.254.227.231::INSTR")
        self.vna.initial_process()
        self.vna.set_port(log_port="1", phys_port="1")
        self.vna.set_port(log_port="2", phys_port="2")
        self.vna.set_freq_range(start_freq="27MHz", stop_freq="30MHz")
        self.vna.set_freq_bandwidth(freq="10kHz")
        self.vna.set_sweep_number(sweep_number="51")


        self.vna.set_frequencies(
            self.start_freq*1e6, self.end_freq*1e6, self.step_num)
        self.vna.set_sweep(self.start_freq*1e6, self.end_freq*1e6)
        # load calibration file
        # ans = self.vna.LoadCal(
        #    self.parser.get('VNA', 'calibration_file'))
        # self.log_viewer.appendPlainText("Result of LoadCal: {}".format(ans))

        # self.setupEnhance()

    def _initPicoVNA(self):

        self.parser = ConfigParser()
        self.parser.read(self.inifile)

        self.start_freq = self.now_start_freq = self.parser.getfloat(
            'VNA', 'start_freq')
        self.freq_step = self.parser.getfloat('VNA', 'freq_step')
        self.step_num = self.parser.getint('VNA', 'step_num')
        self.input_power = self.parser.getint('VNA', 'input_power')
        self.bandwidth = self.parser.getint('VNA', 'bandwidth')
        self.end_freq = self.now_end_freq = self.start_freq + \
            self.freq_step * (self.step_num - 1)
        self.freq = np.arange(
            self.start_freq, self.end_freq + self.freq_step/2, self.freq_step)

        self.vna = NanoVNA()
        self.vna.set_frequencies(
            self.start_freq*1e6, self.end_freq*1e6, self.step_num)
        self.vna.set_sweep(self.start_freq*1e6, self.end_freq*1e6)
        # load calibration file
        # ans = self.vna.LoadCal(
        #    self.parser.get('VNA', 'calibration_file'))
        # self.log_viewer.appendPlainText("Result of LoadCal: {}".format(ans))

        self.dB, self.base_dB, self.diff_dB, self.diff_dB_w_filter, self.std_dB, self.peaks = \
            None, None, None, None, None, None

        self.fps = 0
        # self.setupEnhance()

    def getFreqRange(self):
        return self.start_freq, self.end_freq, self.freq_step, self.step_num

    def setFreqRange(self, freq_range):
        target_start_freq, target_end_freq = freq_range
        start_id = 0
        end_id = self.step_num - 1
        if np.where(self.freq >= target_start_freq)[0].size != 0:
            start_id = np.where(self.freq >= target_start_freq)[0][0]
        if np.where(self.freq >= target_end_freq)[0].size != 0:
            end_id = np.where(self.freq >= target_end_freq)[0][0]

        self.now_start_freq = self.start_freq + self.freq_step * start_id
        self.now_end_freq = self.end_freq - \
            self.freq_step * (self.step_num - 1 - end_id)

    def setThres(self, thres_range):
        _, thres = thres_range
        self.thres = thres

    def _getRawS21(self):
        # Get S21 data from log file during replaying mode
        if self.logfile:
            self.log_cnt = self.log_cnt % self.MAX_LOG_CNT
            self.raw_dB = self.S21_log_data[self.log_cnt]
            self.log_cnt = self.log_cnt + 1
            return self.freq, self.raw_dB

        # Get S21 data from PicoVNA
        self.vna.fetch_frequencies()
        s21 = self.vna.data(1)
        dB = 20 * np.log10(np.abs(s21))
        return self.freq, dB

    def setupEnhance(self, smoo=1, bw=10000, ave=1):
        ans = self.vna.setEnhance("Smoo", smoo)
        print("Result of setEnhance (Smooth: {}): {}".format(smoo, ans))

        ans = self.vna.setEnhance("BW", bw)
        print("Result of setEnhance (BW: {} kHz): {}".format(bw/1e3, ans))

        ans = self.vna.setEnhance("Aver", ave)
        print("Result of setEnhance (Average cnt. {}): {}".format(ave, ans))

    def average(self, ave_num=10):
        dB_arr = np.zeros(shape=(ave_num, self.step_num))

        for i in range(ave_num):
            _, dB = self._getRawS21()
            dB_arr[i] = dB

        self.base_dB = np.average(dB_arr, axis=0)
        self.std_dB = np.std(dB_arr, axis=0, ddof=1)

    def getFPS(self):
        return self.fps

    def stop(self):
        print("close VNA")
        self.is_running = False
        time.sleep(0.1)
        if self.logfile == None:
            del self.vna

    def update(self, print_time=False):
        if not self.is_running:
            return

        st = time.time()
        self.freq, self.dB = self._getRawS21()

        self.target_ids = np.where(
            (self.freq >= self.now_start_freq) & (self.freq <= self.now_end_freq))
        mt = time.time()

        self.peaks, self.base_dB, self.diff_dB_w_filter, self.diff_dB = detect_peak_with_polyfit(
            deg=4, thres=self.thres, y=self.dB[self.target_ids], x=self.freq[self.target_ids])
        et = time.time()
        if print_time:
            print("getRawS21: {:.0f}ms, detectPeak: {:.0f}ms".format(
                (mt-st)*1e3, (et-mt)*1e3))

        self.fps = 1/(et-st) if et - st > 0 else 1000
        self.s21_data = [self.freq, self.dB, self.base_dB, self.diff_dB,
                         self.diff_dB_w_filter, self.peaks, self.fps, self.target_ids, self.thres]
        self.s21_signal.emit(self.s21_data)
        self.peak_signal.emit([self.freq, self.peaks, self.target_ids])

    def _detectNearMetal(self):
        pass

    def __del__(self):
        self.stop()
