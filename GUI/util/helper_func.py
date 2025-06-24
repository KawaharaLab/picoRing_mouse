# -*- coding: utf-8 -*-
import os
import sys

import numpy as np


def findNearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return array(idx)


def findNearestID(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx
