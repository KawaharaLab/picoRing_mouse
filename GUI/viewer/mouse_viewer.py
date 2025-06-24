import os
import sys
import time

from configparser import ConfigParser

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

class MouseViewer(QWidget):

    def __init__(self, parent, inifile='default.ini'):
        super(MouseViewer, self).__init__(parent)