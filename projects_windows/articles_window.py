"""

"""

import os
import math
from requests import HTTPError

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QMainWindow, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.custom_widgets.button_field import QButtonField

from Figshare_desktop.formatting.formatting import (grid_label, grid_edit, checkable_button)

from figshare_interface import (Groups, Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"

class ProjectsArticlesWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent, project_id):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.project_id = project_id

        self.open_windows = self.parent.open_windows

        self.initFig(self.project_id)
        self.initUI()

    def initFig(self, project_id):
        """
        Initilizes Figshare information for the given project
        :param project_id: int. Figshare project id number
        :return:
        """
        projects = Projects(self.token)
        self.project_info = projects.get_info(project_id)
        self.article_list = projects.list_articles(project_id)

    def initUI(self):
        """
        Initilizes the GUI
        :return:
        """

        self.format_window()

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        #window_widget.setLayout()
        # Set the projects window widget
        self.setWidget(window_widget)

    #####
    # Window Formatting
    #####

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
