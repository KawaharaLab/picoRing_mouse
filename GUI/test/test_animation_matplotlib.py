# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import traceback

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

from util.peak_detector import *
from util.nanovna import NanoVNA


start_freq = 30.0
end_freq = 33.0
step_freq = 0.03
point_num = 101


def main(argv):
    vna = NanoVNA()
    vna.set_frequencies(start_freq*1e6, end_freq*1e6, point_num)
    vna.set_sweep(start_freq*1e6, end_freq*1e6)

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 2, 1)
    ax_diff = fig.add_subplot(1, 2, 2)
    ave_graph, = ax.plot([], [], lw=1, ls='--', label='signal w/o peak')
    raw_graph, = ax.plot([], [], lw=1, label='raw signal')
    peak_graph, = ax.plot([], [], 'o', ms=1, label='peak (>0.1 dB)')

    diff_graph, = ax_diff.plot([], [], lw=1, label='diff')
    peak_in_diff_graph, = ax_diff.plot(
        [], [], 'o', ms=5, label='peak (>0.1 dB)')

    def init():
        ave_graph.set_data([], [])
        raw_graph.set_data([], [])
        peak_graph.set_data([], [])
        diff_graph.set_data([], [])
        peak_in_diff_graph.set_data([], [])

        ax.set_ylabel("S21 LogMag (dBm)")
        ax.set_xlabel("Frequency (MHz)")
        ax.legend()
        ax.set_xlim([start_freq, end_freq])
        ax_diff.set_ylabel("Diff of S21 LogMag (dBm)")
        ax_diff.set_xlabel("Frequency (MHz)")
        ax_diff.set_xlim([start_freq, end_freq])
        ax_diff.set_ylim([-0.5, 0.5])
        ax_diff.set_yticks(np.arange(-0.5, 0.6, 0.1))
        ax_diff.legend()
        ax_diff.grid()

        return ave_graph, raw_graph, peak_graph, diff_graph, peak_in_diff_graph,

    def animate(i):

        st = time.time()
        freq = np.arange(start_freq, end_freq+0.01, step_freq)
        data = vna.scan()
        s21 = data[1]
        dB = 20 * np.log10(np.abs(s21))
        mt = time.time()

        target_ids = np.where((freq >= 30.3) & (freq <= 32.))
        # print(freq.shape)
        # print(dB.shape)
        peaks, base_dB, diff_dB, _ = detect_peak_with_polyfit(
            deg=4, thres=0.03, x=freq[target_ids], y=dB[target_ids])
        et = time.time()
        print('elapsed time of data acquisition and peak deection: {:2f}ms, {:.2f}ms'.format(
            (mt-st)*1e3, (et-mt)*1e3))
        freq_target = freq[target_ids]
        ave_graph.set_data(freq_target, base_dB)
        base_max = np.max(base_dB)
        base_min = np.min(base_dB)
        ax.set_ylim([base_min - 1, base_max + 1])
        raw_graph.set_data(freq, dB)
        diff_graph.set_data(freq_target, diff_dB)

        if peaks.size:
            print("peak frequecy: ", freq_target[peaks])
            peak_graph.set_data(freq_target[peaks], dB[target_ids][peaks])
            peak_in_diff_graph.set_data(freq_target[peaks], diff_dB[peaks])
        else:
            peak_graph.set_data([], [])
            peak_in_diff_graph.set_data([], [])

        return ave_graph, raw_graph, peak_graph, diff_graph, peak_in_diff_graph,

    try:
        anim = animation.FuncAnimation(
            fig, animate, init_func=init, frames=10, interval=1, blit=True, repeat=True)

        def calibrate(val):
            anim.pause()
            print("Calibration ...")
            anim.resume()
            print("Calibration done")

        axes = plt.axes([0.85, 0.9, 0.1, 0.05])
        bcalibration = Button(axes, 'Calibrate', color="white")
        bcalibration.on_clicked(calibrate)
        plt.show()

    except Exception as e:
        del vna
        plt.close()
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main(sys.argv)
    sys.exit()
