"""

"""

import os
import itertools
from PyQt5.QtWidgets import (QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QAbstractItemView,
                             QHBoxLayout, QVBoxLayout, QSizePolicy, QMessageBox)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import (Qt, QPoint)

from figshare_interface import (Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class MetadataWindow(QWidget):

    def __init__(self, app, main_window, data_window):
        super().__init__()

        self.app = app
        self.main_window = main_window
        self.data_window = data_window

        self.initUI()

    def initUI(self):

        self.formatWindow()

    def formatWindow(self):

        dw_geom = self.data_window.geometry()

        dw_x0 = dw_geom.x()
        dw_y0 = dw_geom.y()
        dw_width = dw_geom.width()
        dw_height = dw_geom.height()

        screen = self.app.primaryScreen().availableGeometry()

        x0 = dw_x0
        y0 = dw_y0 + dw_height + 10
        width = screen.width() - x0
        height = screen.height() / 3

        self.setGeometry(x0, y0, width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
