"""
New Object Window

This module attempts to abstract the creation of a new Figshare object, e.g. a collection or project.
SubClasses should use this class as their parent, but the class itself is not meant to be used directly.

Notes:
    The NewObjectWindow Class is to be SubClassed with the following variables and functions redefined.

    Functions:
        create_object_info_layout()
        on_save_pressed()
        on_cancel_pressed()
        create_object()

"""

# Standard Imports
import os
from requests import HTTPError

# PyQt Imports
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QTextEdit, QGridLayout, QMainWindow, QApplication,
                             QLineEdit, QVBoxLayout, QSizePolicy, QMessageBox)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import (Qt)

# Figshare Desktop Imports
from Figshare_desktop.formatting.formatting import (scaling_ratio, press_button, grid_label, label_font, grid_edit)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class NewObjectWindow(QMdiSubWindow):
    """
    An abstract class for creating a window that facilitates the creation of a new Figshare object.
    """

    def __init__(self, app: QApplication, OAuth_token: str, parent: QMainWindow):
        """
        Initialise the window.

        Args:
            app: main thread application object
            OAuth_token: Figshare authentication token obtained at login.
            parent:
        """
        super().__init__()

        # Create class variables of init args
        self.app = app
        self.token = OAuth_token
        self.parent = parent

        # Create shortned path to open windows set
        self.open_windows = self.parent.open_windows

        # Initialise the UI
        self.initUI()

    def initUI(self):
        """
        Formats, and creates the window.
        Returns:
            None
        """
        # Format the Window to the Primary Screen
        self.format_window()

    # Window Formatting
    # =================

    def format_window(self):
        """
        Format the current window to the available space in primary screen.
        Returns:
            None
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
        # Remove frame from projects window
        self.setWindowFlags(Qt.FramelessWindowHint)

    # Window Widgets
    # ==============

    def create_lineedit(self, label: str):
        """
        Creates a QLabel and QLineEdit pair.

        Args:
            label: Name of field to be associated to the line edit.

        Returns:
            lbl (QLabel): Formatted label widget.
            edit (QLineEdit): Formatted line edit widget.
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
        Creates a QLabel and QTextEdit pair.
        Args:
            label: Name of field to be associated to the text edit.

        Returns:
            lbl (QLabel): Formatted label widget.
            edit (QLineEdit): Formatted text edit widget.
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
        Create a layout containing two buttons. One to create a new object and the second to cancel.

        Returns:
            vbox (QVBoxLayout): Layout containing the create and cancel buttons.
        """

        # Create save button
        sv_btn = QPushButton()
        press_button(self.app, sv_btn)  # Format button
        sv_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_upload.png')))
        sv_btn.setToolTip('Save new object.')
        sv_btn.setToolTipDuration(1000)
        sv_btn.pressed.connect(self.on_save_pressed)

        # Create cancel button
        cl_btn = QPushButton()
        press_button(self.app, cl_btn)  # Format button
        cl_btn.setIcon((QIcon(os.path.abspath(__file__ + '/../..' + '/img/exit.png'))))
        cl_btn.setToolTip('Exit without saving.')
        cl_btn.setToolTipDuration(1000)
        cl_btn.pressed.connect(self.on_cancel_pressed)

        # Create Layout
        vbox = QVBoxLayout()
        vbox.addWidget(sv_btn)
        vbox.addWidget(cl_btn)

        return vbox

    def create_object_info_layout(self):
        """
        Creates a layout with label and edit fields for creating a new figshare object.

        MUST BE OVERWRITTEN BY CHILDREN

        Examples:
               Example of code is given for creating a new project info layout.

               # Title
                title_lbl, self.title_field = self.create_lineedit('Title')
                self.title_field.setPlaceholderText('Enter Project Title Here.')

                # Description
                description_lbl, self.description_field = self.create_edit('Description')
                self.description_field.setPlaceholderText('Enter meaningful project description here.')

                # Funding
                funding_lbl, self.funding_field = self.create_lineedit('Funding')
                self.funding_field = QButtonField()

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

        Returns:
            grid (QGridLayout): grid layout containing the different info fields and labels.
        """
        pass

    # Widget Actions
    # ==============

    def on_save_pressed(self):
        """
        Called when the save button is pressed. Will upload the new object to Figshare.

        MUST BE OVERWRITTEN BY CHILDREN

        Examples:
            Example of code is given for creating a new project info layout.

            title = self.title_field.text()
            description = self.description_field.toPlainText()
            funding = self.funding_field.get_tags()
            fund_text = ''
            for fund in funding:
                fund_text += ':_:{}'.format(fund)

            try:
                group_id = self.group_field.text()
                group_id = int(group_id)
                available_groups = [i['id'] for i in Groups(self.token).get_list()]
                if group_id not in available_groups:
                    raise ValueError('Not a valid group id.')
                else:
                    project_info = self.create_project(title, description, fund_text, group_id)
                    msgBox = QMessageBox()
                    msgBox.setIcon(QMessageBox.Information)
                    msgBox.setText("New Project Created\n{}".format(project_info['title']))
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox, exit_parent=True))
                    msgBox.show()

            except ValueError as err:
                err_args = err.args
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setText(err_args[0])
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
                msgBox.show()

            except TypeError as err:
                err_args = err.args
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
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

        Returns:
            None

        Raises:
            ValueError:

            TypeError:

            HTTPError:
        """
        pass

    def on_cancel_pressed(self):
        """
        Called when the cancel button is pressed. Will return to the objects window without creating a new object.

        Examples:
            Example of code is given for creating a new project info layout.

            self.open_windows.remove('new_project_window')
            self.close()
            self.parent.section_window.on_projects_btn_pressed()

        Returns:
            None
        """
        pass

    def on_msgbtn_pressed(self, box: QMessageBox, exit_parent=False):
        """
        Called when an error message button is pressed.
        Args:
            box: Error message box created by error in save process.
            exit_parent: Should the new object window be closed.

        Returns:
            None
        """
        box.close()
        if exit_parent:
            self.on_cancel_pressed()

    # Figshare API Functions
    # ======================

    def create_object(self, info_dict: dict):
        """
        Creates a new figshare object from the information dictionary passed to the function.

        MUST BE OVERWRITTEN BY CHILDREN

        Examples:
            Example of code is given for creating a new project info layout.

            projects = Projects(self.token)
            required_fields = ['title', 'description', 'funding', 'group_id']
            for field in required_fields:
                if field not in info_dict:
                    return
            object_info = projects.create(**info_dict)

            return project_info

        Args:
            info_dict:

        Returns:
            object_info (dict): Dictionary containing information on the newly created object.
        """
        pass
