"""

"""

import os
import math
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QToolTip, QMessageBox, QMainWindow,
                             QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QObject)

from ..formatting.formatting import (scaling_ratio, checkable_button, search_bar)
from Figshare_desktop.projects_windows.new_project_window import NewProjectWindow
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

        self.open_windows = self.parent.open_windows

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

        # Add the Projects button to the vertical box layout
        self.create_project_bar(0, 4)
        self.vbox.addLayout(self.project_buttons_box)

        # Add the scroll bar to the vertical box layout
        self.s_bar = self.scroll_bar()
        self.vbox.addWidget(self.s_bar)

        self.hbox = QHBoxLayout()
        temp = QVBoxLayout()
        temp.addWidget(self.search_bar())
        temp.addLayout(self.management_buttons())
        self.hbox.addLayout(temp)
        self.hbox.addLayout(self.vbox)

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(self.hbox)
        # Set the projects window widget
        self.setWidget(window_widget)

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

    def closeEvent(self):
        """
        Ensures that the project info window is closed if it is open
        """
        pass

    #####
    # Window Widgets
    #####

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
        title_fnt_size = 12 * f_ratio
        date_ftn_size = 8 * f_ratio

        # Create the title label
        title_lbl = QLabel()
        title_lbl.setText("{}".format(title))
        title_lbl_fnt = QFont('SansSerif', title_fnt_size)
        title_lbl_fnt.setBold(True)
        title_lbl.setFont(title_lbl_fnt)
        title_lbl.setWordWrap(True)

        # Create the date label
        date_lbl = QLabel()
        if published_date is None:
            published_date = 'Private'
        date_lbl.setText("Published: {}".format(published_date))
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

    def management_buttons(self):
        """
        Creates a layout that holds buttons to be used for creating and deleting projects
        :return: QVBoxLayout holding the create, and delete projects buttons
        """

        # Create New Project Button
        np_btn = QPushButton()
        np_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        np_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Folder-48.png')))
        np_btn.setToolTip('Create a new Figshare Project')
        np_btn.setToolTipDuration(1)
        np_btn.pressed.connect(self.on_projects_btn_pressed)

        # Create layout to hold buttons
        vbox = QVBoxLayout()
        # Add Buttons to layout
        vbox.addWidget(np_btn)

        return vbox

    def search_bar(self):
        """
        Creates a QLineEdit object for the user to enter a search query
        :return: Edits the projects list object according to the filter
        """

        # Create text box
        edit = QLineEdit()
        # Set font style
        search_bar(self.app, edit)
        # Set place holder text
        edit.setPlaceholderText('Search')
        # Add a clear button to the line edit
        edit.setClearButtonEnabled(True)
        # Add mouse over text
        edit.setToolTip('Search for specific Figshare Projects')
        edit.setToolTipDuration(1)
        # Connect search function to the return key
        edit.returnPressed.connect(lambda: self.search_on_return(edit.text()))
        edit.textChanged.connect(lambda: self.search_on_clear(edit.text()))
        return edit

    #####
    # Widget Actions
    #####

    def slider_val(self):
        """
        Called when the projects button slider is changed.
        Removes all existing buttons and regenerates from the new position
        :return:
        """
        while self.project_buttons_box.count():
            item = self.project_buttons_box.takeAt(0)
            item.widget().deleteLater()

        s_bar_pos = self.s_bar.value()

        if 1 < len(self.project_list) < 4:
            number = len(self.project_list)
        else:
            number = 4
        self.s_bar.setMaximum(len(self.project_list) - number)

        self.create_project_bar(s_bar_pos, s_bar_pos + number)

    def search_init(self):
        """
        Called when the projects search bar is used.
        Removes all existing buttons and regenerates from new projects list
        :return:
        """
        while self.project_buttons_box.count():
            item = self.project_buttons_box.takeAt(0)
            item.widget().deleteLater()

        if 1 <= len(self.project_list) <= 4:
            number = len(self.project_list)
        else:
            number = 4

        self.s_bar.setMaximum(len(self.project_list) - number)

        self.create_project_bar(0, number)

    def search_on_return(self, search_text):
        """
        Called when return is pressed in the search bar.
        :return:
        """
        self.project_list = self.search_projects(search_text, self.token)
        self.search_init()

    def search_on_clear(self, lineedit_text):
        """
        Called when the search bar is cleared
        :return:
        """
        if lineedit_text == '':
            self.project_list = self.get_project_list(self.token)
            self.slider_val()

    def on_projects_btn_pressed(self):
        """
        Called when the create new project button is pressed
        """
        if 'new_project_window' in self.open_windows:
            self.open_windows.remove('new_project_window')
            self.parent.new_project_window.close()
        else:
            self.open_windows.remove('projects_window')
            self.close()
            self.open_windows.add('new_project_window')
            self.parent.new_project_window = NewProjectWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.new_project_window)
            self.parent.new_project_window.show()


    #####
    # Figshare API Interface Calls
    #####

    def get_project_list(self, token):
        """
        Returns the users private project list
        :param token: Figshare OAuth token
        :return: array of project
        """
        projects = Projects(token)
        return projects.get_list()

    def search_projects(self, search_text, token):
        """
        Returns a list of projects matching the users search criteria
        :param search_text: String. Figshare style elastic search string
        :param token: Figshare OAuth token
        :return:
        """
        projects = Projects(token)

        result = projects.search(search_text)
        if len(result) == 0:
            result = projects.get_list()

        return result
