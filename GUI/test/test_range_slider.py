from superqt import QLabeledSlider, QLabeledRangeSlider, QLabeledDoubleSlider, QLabeledDoubleRangeSlider
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

app = QApplication([])

ORIENTATION = Qt.Vertical

w = QWidget()
qls = QLabeledSlider(ORIENTATION)
qls.valueChanged.connect(lambda e: print("qls valueChanged", e))
qls.setRange(0, 500)
qls.setValue(300)


qlds = QLabeledDoubleSlider(ORIENTATION)
qlds.valueChanged.connect(lambda e: print("qlds valueChanged", e))
qlds.setRange(0, 1)
qlds.setValue(0.5)
qlds.setSingleStep(0.1)

qlrs = QLabeledRangeSlider(ORIENTATION)
qlrs.valueChanged.connect(lambda e: print(
    "QLabeledRangeSlider valueChanged", e))
qlrs.setRange(0, 100)
qlrs.setValue((20, 60))

qldrs = QLabeledDoubleRangeSlider(ORIENTATION)
qldrs.valueChanged.connect(lambda e: print("qlrs valueChanged", e))
qldrs.setRange(27, 30)
qldrs.setSingleStep(0.5)
qldrs.setValue((28.5, 29.5))


w.setLayout(QVBoxLayout() if ORIENTATION == Qt.Horizontal else QHBoxLayout())
w.layout().addWidget(qls)
w.layout().addWidget(qlds)
w.layout().addWidget(qlrs)
w.layout().addWidget(qldrs)
w.show()
w.resize(500, 150)
app.exec_()
