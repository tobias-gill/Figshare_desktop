"""

"""

import os
import math
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QToolTip, QMessageBox, QMainWindow,
                             QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QObject)

from ..formatting.formatting import (scaling_ratio, checkable_button, search_bar)
from Figshare_desktop.projects_windows.project_info_window import ProjectInfoWindow

from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class NewProjectWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        #self.initFig()
        self.initUI()

    def initUI(self):

        self.format_window()

    #####
    # Window Formatting and Actions
    #####

    def format_window(self):
        """
        Formats the Projects window
        """
        # Get the scaling ratios for the window size and fonts
        w_scale, f_scale = scaling_ratio(self.app)

        # Gets the QRect of the main window
        geom = self.parent.geometry()
        # Gets the Qrect of the sections window
        section_geom = self.parent.section_geom

        # Define geometries for the projects window
        x0 = section_geom.x() + section_geom.width()
        y0 = section_geom.y()
        w = geom.width() - x0
        h = ((geom.height() - y0) / 6)
        self.setGeometry(x0, y0, w, h)
        # Remove frame from projects window
        self.setWindowFlags(Qt.FramelessWindowHint)
