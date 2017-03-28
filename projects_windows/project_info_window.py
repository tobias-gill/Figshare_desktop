"""

"""

import os
import math
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QMainWindow, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.custom_widgets.button_field import QButtonField

from Figshare_desktop.formatting.formatting import (grid_label, grid_edit, checkable_button)

from Figshare_desktop.projects_windows.articles_window import ProjectsArticlesWindow

from figshare_interface import (Groups, Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ProjectInfoWindow(QMdiSubWindow):

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
        Initilizes Fighsare information for the given project
        :return:
        """
        projects = Projects(self.token)
        self.project_info = projects.get_info(project_id)

    def initUI(self):
        """
        Initilizes the GUI
        :return:
        """

        self.format_window()

        # Create a Horizontal and Vertical Box layout
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        # Add the title to the vertical layout
        self.vbox.addLayout(self.title_hbox())

        # Add the Open/Close Articles Button to the horizontal layout
        self.hbox.addWidget(self.articles_button())
        # Add the description layout to the horizontal layout
        self.hbox.addLayout(self.description_vbox())
        # Add the project info grid to the horizontal layout
        self.hbox.addLayout(self.info_grid())

        # Add the horizontal layout to the vertical layout
        self.vbox.addLayout(self.hbox)

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(self.vbox)
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
        h = ((geom.height() - y0) / 6)
        self.setGeometry(x0, y0, w, h)
        # Remove frame from the window
        self.setWindowFlags(Qt.FramelessWindowHint)

    #####
    # Window Widgets
    #####

    def articles_button(self):
        """
        Creates a click button to open and close the project articles window
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        checkable_button(self.app, btn)
        #btn.clicked[bool].connect()
        return btn

    def create_label(self, label):
        """
        Creates a QLabel with a default formatting
        :param label: String to be displayed in the label
        :return: QLabel
        """
        lbl = QLabel(label)
        grid_label(self.app, lbl)
        return lbl

    def create_lineedit(self):
        """
        Creates a QLineEdit with a default formatting
        :return: QLineEdit
        """
        edit = QLineEdit()
        grid_edit(self.app, edit)
        return edit

    def create_textedit(self):
        """
        Creates a QTextEdit with a default formatting
        :return: QTextEdit
        """
        edit = QTextEdit()
        grid_edit(self.app, edit)
        return edit

    def title_hbox(self):
        """
        Creates a Horizontal box layout containing the title lineedit and an edit button
        :return: QHBoxLayout
        """
        # Create Edit/Label
        title = self.project_info['title']
        title_edit = QLineEdit(title)
        grid_label(self.app, title_edit)
        title_edit.setEnabled(False)

        # Create Edit Button
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        checkable_button(self.app, edit_btn)
        #edit_btn.clicked[bool].connect()

        # Create Layout
        hbox = QHBoxLayout()
        hbox.addWidget(title_edit)
        hbox.addWidget(edit_btn)

        return hbox

    def description_vbox(self):
        """
        Creates a Vertical box layour containing the description label and edit button and a textedit field
        :return: QVBoxLayout
        """

        # Create the Description Label
        lbl = QLabel('Description')
        grid_label(self.app, lbl)

        # Create Edit Button
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        checkable_button(self.app, edit_btn)
        # edit_btn.clicked[bool].connect()

        # Create TextEdit
        description = self.project_info['description']
        text_edit = QTextEdit()
        grid_edit(self.app, text_edit)
        text_edit.setEnabled(False)

        # Create a horizontal layout for the label and edit button
        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(edit_btn)

        # Create a Vertical layout to hold the label layout and the edit field
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(text_edit)

        return vbox


    def info_grid(self):
        """
        Creates a grid layout containing more details on the project
        :return: QGridlayout
        """

        # Create Labels

        # Project ID Label
        id_lbl = QLabel('Project ID')
        grid_label(self.app, id_lbl)

        # Published Label
        pub_lbl = QLabel('Published')
        grid_label(self.app, pub_lbl)

        # Collaborators Label
        col_lbl = QLabel('Collaborators')
        grid_label(self.app, col_lbl)

        # Funding Label
        fund_lbl = QLabel('Funding')
        grid_label(self.app, fund_lbl)

        # Group Label
        group_lbl = QLabel('Group')
        grid_label(self.app, group_lbl)

        # Storage Label
        stor_lbl = QLabel('Storage')
        grid_label(self.app, stor_lbl)

        # Create Edit Fields

        # Project ID Field
        id_field = QLabel()
        grid_edit(self.app, id_field)
        id_field.setText(str(self.project_info['id']))

        # Published Field
        published_date = self.project_info['published_date']
        if published_date is None:
            published_date = 'Private'
        pub_field = QLabel()
        pub_field.setText(published_date)

        # Collaborators Field
        col_field = QButtonField()

        # Create and Populate grid
        grid = QGridLayout()
        grid.addWidget(col_field)

        return grid
