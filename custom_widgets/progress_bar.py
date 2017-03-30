"""

"""

from PyQt5.QtWidgets import (QWidget, QProgressBar, QMdiSubWindow, QScrollArea)
from PyQt5.QtGui import (QFont, QColor, QPainter)
from PyQt5.QtCore import (Qt, QRect)

from Figshare_desktop.custom_widgets.tag_button import QTagButton

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ArticleLoadBar(QMdiSubWindow):

    def __init__(self, maximum, parent):
        super().__init__()
        self.maximum = maximum
        self.parent = parent
        self.initUI(self.maximum)

    def initUI(self, maximum):

        pbar = QProgressBar()
        pbar.setMaximum(maximum)

        self.pbar = pbar

        self.setWidget(self.pbar)
        self.format_window()
        self.parent.progress_bar = self
        self.parent.mdi.addSubWindow(self.parent.progress_bar)
        self.parent.progress_bar.show()

    def format_window(self):
        """
        Sets the window geometry
        :return:
        """
        # Gets the QRect of the main window
        geom = self.parent.geometry()
        # Gets the Qrect of the sections window
        section_geom = self.parent.section_geom
        # Define geometries for the projects window
        x0 = section_geom.x() + section_geom.width()
        y0 = section_geom.y()
        w = geom.width() - x0
        h = ((geom.height() - y0) / 3)
        self.setGeometry(x0, y0, w, h)
        # Remove frame from the window
        self.setWindowFlags(Qt.FramelessWindowHint)

    def update_progress(self, step):
        """
        Called when the progress bar is to be updated
        :param step: int.
        :return:
        """
        self.pbar.setValue(step)
        if step == (self.maximum - 1):
            self.parent.progress_bar.close()
