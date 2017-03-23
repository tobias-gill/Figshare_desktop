"""

"""

import os
import math
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QToolTip, QMessageBox, QMainWindow,
                             QWidget, qApp, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from ..formatting.formatting import scaling_ratio
from ..formatting.formatting import checkable_button
from Figshare_desktop.projects_windows.project_info_window import ProjectInfoWindow

from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ProjectsWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initFig()
        self.initUI()

    def initFig(self):
        """
        Initialize Figshare information
        """
        self.project_list = self.get_project_list(self.token)

    def initUI(self):

        self.format_window()

        # Create a horizontal box layout to hold the project buttons
        self.project_buttons_box = QHBoxLayout()
        # Create a vertical box layout to hold the project window widgets and layouts
        self.vbox = QVBoxLayout()

        # Add the scroll bar to the vertical box layout
        self.s_bar = self.scroll_bar()
        self.vbox.addWidget(self.s_bar)

        self.create_project_bar(0, 4)

        self.vbox.addLayout(self.project_buttons_box)

        window_widget = QWidget()
        window_widget.setLayout(self.vbox)
        self.setWidget(window_widget)

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

    def closeEvent(self):
        """
        Ensures that the project info window is closed if it is open
        """
        pass

    def scroll_bar(self):
        """
        Creates a scroll bar set to the size of the projects list
        :return: QScrollBar Object
        """
        s_bar = QScrollBar(Qt.Horizontal)
        s_bar.setMaximum(len(self.project_list) - 4)
        s_bar.sliderMoved.connect(self.slider_val)
        s_bar.valueChanged.connect(self.slider_val)
        return s_bar

    def slider_val(self):
        """

        :return:
        """
        while self.project_buttons_box.count():
            item = self.project_buttons_box.takeAt(0)
            item.widget().deleteLater()

        s_bar_pos = self.s_bar.value()

        self.create_project_bar(s_bar_pos, s_bar_pos + 4)

    def create_proj_thumb(self, title, published_date, id):
        """
        Creates a large pushbutton for a project
        :param title: string. Project title
        :param published_date: string. project published date
        :param id: int. figshare project id number
        :return: QPushButton object
        """
        geom = self.geometry()

        # Get the scalig ratios for the current window
        w_ratio, f_ratio = scaling_ratio(self.app)
        # Scale the font sizes
        title_fnt_size = 14 * f_ratio
        date_ftn_size = 12 * f_ratio

        # Create the title label
        title_lbl = QLabel()
        title_lbl.setText("{}".format(title))
        title_lbl_fnt = QFont('SansSerif', title_fnt_size)
        title_lbl_fnt.setBold(True)
        title_lbl.setFont(title_lbl_fnt)
        title_lbl.setWordWrap(True)

        # Create the date label
        date_lbl = QLabel()
        date_lbl.setText("{}".format(published_date))
        date_lbl_fnt = QFont('SansSerif', date_ftn_size)
        date_lbl.setFont(date_lbl_fnt)
        date_lbl.setStyleSheet('color: gray')
        date_lbl.setWordWrap(True)

        # Create a layout to hold the labels
        lbl_box = QVBoxLayout()
        # Add labels to layout
        lbl_box.addWidget(title_lbl)
        lbl_box.addWidget(date_lbl)

        # Create a button for the project
        btn = QPushButton(self)
        checkable_button(self.app, btn)
        btn.setLayout(lbl_box)
        #btn.clicked[bool].connect()

        self.project_buttons_box.addWidget(btn)

    def create_project_bar(self, start, finish):
        """
        Creates a series of Project push buttons
        :param start: start position in projects list
        :param finish: finish position in projects list
        """
        self.buttons = {}
        i = 0

        for project_pos in range(start, finish):
            title = self.project_list[project_pos]['title']
            pub_date = self.project_list[project_pos]['published_date']
            id = self.project_list[project_pos]['id']
            self.buttons[str(id)] = i
            i += 1
            self.create_proj_thumb(title, pub_date, id)

    def get_project_list(self, token):
        """
        Returns the users private project list
        :param token: Figshare OAuth token
        :return: array of project
        """
        projects = Projects(token)
        return projects.get_list()
