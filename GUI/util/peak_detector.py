# -*- coding: utf-8 -*-
import os
import sys
import deprecation

import numpy as np
import pandas as pd
import scipy.signal as sig
from numpy.lib.stride_tricks import sliding_window_view


def _detect_sensor_peak(diff_data, peak_kind='max_only'):

    peak_ids, _ = sig.find_peaks(
        diff_data, prominence=(0.1, 50.0), width=(0.1, 50))

    if peak_kind == 'max_only' and len(peak_ids) > 0:
        max_peak_id = np.argmax(diff_data[peak_ids])
        return np.array([peak_ids[max_peak_id]])

    return peak_ids


def detect_peak_with_polyfit(deg, thres, y, x=None, offset=0.1):
    if x is None:
        x = np.arange(0, len(y), 1)
    # calculate S21 curve w/o tiny peaks
    yn = np.poly1d(np.polyfit(x, y, deg))
    # calculate S21 change
    raw_diff = y - (yn(x) + offset)
    # remove noise
    raw_diff[raw_diff > 0] = 0
    raw_diff[np.abs(raw_diff) <= (offset + thres)] = 0
    filtered_diff = np.abs(raw_diff)
    # detect tiny peak in S21 curve
    peak_ids = _detect_sensor_peak(filtered_diff, peak_kind='max_only')

    return peak_ids, yn(x) + offset, filtered_diff - offset, -(y-yn(x))


def _SMA_sliding_window(data, window_size=3):
    SMA_data = np.average(sliding_window_view(data, window_size), axis=1)
    for i in range(window_size-1):
        tmp = np.average(data[len(data)-window_size+i+1:])
        SMA_data = np.append(SMA_data, tmp)
    return SMA_data


@deprecation.deprecated(details='unsupported')
def detect_peak_with_ave(data, ave_data):
    diff = data - ave_data
    diff = np.abs(diff)
    peak_ids = _detect_sensor_peak(diff)

    return peak_ids, ave_data, diff


@deprecation.deprecated(details='unsupported')
def detect_peak_with_moving_ave(data, method='EMA'):
    ave_data = None

    if method == 'SMA':
        ave_data = _SMA_sliding_window(data, window_size=5)

    if method == 'EMA':
        df = pd.DataFrame(data)
        ave_data = df.ewm(com=2).mean().to_numpy().T[0]

    diff = data - ave_data
    diff = np.abs(diff)

    peak_ids = _detect_sensor_peak(diff)

    return peak_ids, ave_data, diff, data - ave_data


def main(argv):
    pass


if __name__ == '__main__':
    main(sys.argv)
    sys.exit()
