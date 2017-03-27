"""

"""

import os
import math
from requests import HTTPError
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QTextEdit, QGridLayout, QMainWindow,
                             QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar, QMessageBox)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QObject)

from ..formatting.formatting import (scaling_ratio, press_button, grid_label, label_font, edit_font, grid_edit)

from figshare_interface import (Projects, Groups)

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
        self.open_windows = self.parent.open_windows  # Gets the set of open windows

        self.initUI()

    def initUI(self):

        self.format_window()

        self.hbox = QHBoxLayout()
        self.hbox.addLayout(self.create_command_buttons())
        self.hbox.addLayout(self.create_project_info_layout())

        window_widget = QWidget()
        window_widget.setLayout(self.hbox)
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

    #####
    # Window Widgets
    #####

    def create_lineedit(self, label):
        """
        Creates a label and lineedit
        :param label: String. Containing label name.
        :return: QLabel and QLineEdit
        """

        # Create Label
        lbl = QLabel(label)
        grid_label(self.app, lbl)

        # Create LineEdit
        edit = QLineEdit()
        edit.setClearButtonEnabled(True)
        grid_edit(self.app, edit)

        return lbl, edit

    def create_edit(self, label):
        """
        Creates a label and Textedit
        :param label: String. Containing label name.
        :return: QLabel and QTextEdit.
        """

        # Create Label
        lbl = QLabel(label)
        lbl.setFont(label_font(self.app))
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Create LineEdit
        edit = QTextEdit()
        grid_edit(self.app, edit)

        return lbl, edit

    def create_command_buttons(self):
        """
        Creates a layout containg two buttons. One to create the new project, the second to cancel.
        :return: QVBoxLayout containg the save and cancel buttons.
        """

        # Create save button
        sv_btn = QPushButton()
        press_button(self.app, sv_btn)  # Format button
        sv_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_upload.png')))
        sv_btn.setToolTip('Save new project.')
        sv_btn.setToolTipDuration(1)
        sv_btn.pressed.connect(self.on_save_pressed)

        # Create cancel button
        cl_btn = QPushButton()
        press_button(self.app, cl_btn)  # Format button
        cl_btn.setIcon((QIcon(os.path.abspath(__file__ + '/../..' + '/img/exit.png'))))
        cl_btn.setToolTip('Exit without saving.')
        cl_btn.setToolTipDuration(1)
        cl_btn.pressed.connect(self.on_cancel_pressed)

        # Create Layout
        vbox = QVBoxLayout()
        vbox.addWidget(sv_btn)
        vbox.addWidget(cl_btn)

        return vbox

    def create_project_info_layout(self):
        """
        Creates a layout with label and edit fields for creating a new project.
        :return: QVBoxLayout with fields to create a new project
        """

        # Title
        title_lbl, self.title_field = self.create_lineedit('Title')
        self.title_field.setPlaceholderText('Enter Project Title Here.')

        # Description
        description_lbl, self.description_field = self.create_edit('Description')
        self.description_field.setPlaceholderText('Enter meaningful project description here.')

        # Funding
        funding_lbl, self.funding_field = self.create_lineedit('Funding')
        self.funding_field.setPlaceholderText('Enter details of funding for this project.')

        # Group
        group_lbl, self.group_field = self.create_lineedit('Group ID')
        self.group_field.setText(str(self.get_group()))  # Auto fill with the users group id

        # Create Layout
        grid = QGridLayout()
        grid.addWidget(title_lbl, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.title_field, 0, 1)

        grid.addWidget(description_lbl, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.description_field, 1, 1)

        grid.addWidget(funding_lbl, 2, 0, Qt.AlignLeft)
        grid.addWidget(self.funding_field, 2, 1)

        grid.addWidget(group_lbl, 3, 0, Qt.AlignLeft)
        grid.addWidget(self.group_field, 3, 1)

        grid.setColumnStretch(1, 3)

        return grid

    #####
    # Button Actions
    #####

    def on_save_pressed(self):
        """
        Called when the save button is pressed. Will upload the new project to Figshare.
        :return:
        """
        title = self.title_field.text()
        description = self.description_field.toPlainText()
        funding = self.funding_field.text()
        try:
            group_id = self.group_field.text()
            group_id = int(group_id)
            available_groups = [i['id'] for i in Groups(self.token).get_list()]
            if group_id not in available_groups:
                raise ValueError('Not a valid group id.')
            else:
                self.create_project(title, description, funding, group_id)
                self.on_cancel_pressed()

        except ValueError as err:
            err_args = err.args
            msgBox = QMessageBox()
            msgBox.setText(err_args[0])
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
            msgBox.show()

        except TypeError as err:
            err_args = err.args
            msgBox = QMessageBox()
            msgBox.setText(err_args[0])
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
            msgBox.show()

        except HTTPError as err:
            err_args = err.args
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText(err_args[0])
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
            msgBox.show()

    def on_cancel_pressed(self):
        """
        Called when the cancel button is pressed. Will return to the projects window without creating new project.
        :return:
        """
        self.open_windows.remove('new_project_window')
        self.close()
        self.parent.section_window.on_projects_btn_pressed()

    def on_msgbtn_pressed(self, box):
        """
        Called when an error message button is pressed
        :return:
        """
        box.close()

    #####
    # Figshare API Interface Actions
    #####

    def get_group(self):
        """
        Gets the group ID for the current user
        :return: Int.
        """

        groups = Groups(self.token)

        group_list = groups.get_list()
        group_id = group_list[0]['id']
        return group_id

    def create_project(self, title, description, funding, group_id):
        """
        Creates a new private figshare project
        :param title:
        :param description:
        :param funding:
        :param group_id:
        :return: Dictionary with information on the new project
        """

        projects = Projects(self.token)
        project_info = projects.create(title, description, funding, group_id)

        return project_info