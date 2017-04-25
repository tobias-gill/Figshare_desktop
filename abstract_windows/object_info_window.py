"""


"""

# Standard Imports
import os
from requests import HTTPError

# PyQt Imports
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QTextEdit, QGridLayout, QMainWindow, QApplication,
                             QLineEdit, QVBoxLayout, QSizePolicy, QMessageBox, QHBoxLayout, QWidget, QFrame)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import (Qt)

# Figshare Desktop Imports
from Figshare_desktop.formatting.formatting import (grid_title, press_button, grid_label, label_font, grid_edit,
                                                    checkable_button)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ObjectInfoWindow(QMdiSubWindow):
    """
    Abstract class for viewing information on a figshare object.
    """

    def __init__(self, app: QApplication, OAuth_token: str, parent: QMainWindow, object_id: int):
        """

        Args:
            app: Application instance of the program.
            OAuth_token: Authentication token obtained at login.
            parent: Reference to the framing window where useful variables are kept.
        """
        super().__init__()

        # Create class variables of init args
        self.app = app
        self.token = OAuth_token
        self.parent = parent
        self.object_id = object_id

        # Create shortned path to open windows set
        self.open_windows = self.parent.open_windows

        self.object_info = self.initFig()

        # Initialise the UI
        self.initUI()

    def initFig(self):
        """
        Initilizes Fighsare information for the given project
        :return:
        """
        pass

    def initUI(self):
        """
        Initilizes the GUI
        :return:
        """

        self.format_window()

        # Create a Horizontal and Vertical Box layout
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(self.vbox)
        # Set the projects window widget
        self.setWidget(window_widget)

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

    def create_label(self, label: str):
        """
        Creates a QLabel with a default formatting

        Args:
            label: String to be displayed in the label

        Return:
            lbl (QLabel): label widget.
        """
        lbl = QLabel(label)
        grid_label(self.app, lbl)
        return lbl

    def create_lineedit(self):
        """
        Creates a QLineEdit with a default formatting

        Args:

        Returns:
             edit (QLineEdit): Line edit widget.
        """
        edit = QLineEdit()
        grid_edit(self.app, edit)
        return edit

    def create_textedit(self):
        """
        Creates a QTextEdit with a default formatting

        Args:

        Returns:
            edit (QTextEdit): Text edit widget.
        """
        edit = QTextEdit()
        grid_edit(self.app, edit)
        return edit

    def title_hbox(self, title: str):
        """
        Creates a Horizontal box layout containing the title lineedit and an edit button
        :return: QHBoxLayout
        """
        # Create Edit/Label
        title_edit = QLineEdit(title)
        grid_title(self.app, title_edit)
        title_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_edit.setEnabled(False)
        self.title_wid = title_edit

        # Create Edit Button
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        edit_btn.setMaximumWidth(self.geometry().width() / 50)
        edit_btn.setMaximumHeight(self.geometry().width() / 50)
        checkable_button(self.app, edit_btn)

        # Add an action to the edit button
        edit_btn.clicked[bool].connect(lambda: self.on_edit_pressed(title_edit))

        # Create Layout
        hbox = QHBoxLayout()
        hbox.addWidget(title_edit)
        hbox.addWidget(edit_btn)

        return hbox

    def textedit_vbox(self, label: str, text: str):
        """
        Creates a Vertical box layout containing the description label and edit button and a textedit field
        :return: QVBoxLayout
        """

        # Create the Description Label
        lbl = self.create_label(label)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Create Edit Button
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        edit_btn.setMaximumWidth(self.geometry().width() / 50)
        edit_btn.setMaximumHeight(self.geometry().width() / 50)
        checkable_button(self.app, edit_btn)

        # Create TextEdit
        text_edit = QTextEdit()
        if text is not None and text != '':
            text_edit.setText(text)
        grid_edit(self.app, text_edit)
        text_edit.setEnabled(False)
        self.desc_wid = text_edit

        # Add an action to the edit button
        edit_btn.clicked[bool].connect(lambda: self.on_edit_pressed(text_edit))

        # Create a horizontal layout for the label and edit button
        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(edit_btn)

        # Create a Vertical layout to hold the label layout and the edit field
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(text_edit)

        return vbox

    def articles_button(self):
        """
        Creates a click button to open and close the project articles window
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Magazine-50.png')))
        checkable_button(self.app, btn)
        btn.setMaximumWidth(self.geometry().width() / 20)
        btn.setMinimumWidth(self.geometry().width() / 20)
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        btn.setToolTip('Open Articles Window')
        btn.setToolTipDuration(1000)
        btn.clicked[bool].connect(self.on_articles_pressed)
        return btn

    def save_changes_button(self):
        """
        Creates a save changes button to push edits to Figshare
        :return: QMessageWindow
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.abspath(__file__ + '/../../img/figshare_upload.png')))
        btn.setMaximumWidth(self.geometry().width() / 20)
        btn.setMinimumWidth(self.geometry().width() / 20)
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        btn.setToolTip('Save Changes to Figshare')
        btn.setToolTipDuration(1000)
        btn.pressed.connect(self.on_save_pressed)
        return btn

    @staticmethod
    def v_separator():
        """
        Creates a vertical sepearator.
        :return: QFrame
        """

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        return sep

    @staticmethod
    def h_separator():
        """
        Creates a horizontal separator widget.
        Returns:
            sep (QFrame):
        """
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        return sep

    # Widget Actions
    # ==============

    def on_articles_pressed(self):
        """
        Called when the articles button is pressed. This will open or close the articles window.
        :return:
        """
        pass

    @staticmethod
    def on_edit_pressed(edit_field):
        """
        Called when a edit button is pressed. This will activate or deactivate the passed edit field
        :param edit_field: QLineEdit or QTextEdit
        :return:
        """

        if edit_field.isEnabled():
            edit_field.setEnabled(False)
        else:
            edit_field.setEnabled(True)

    def on_save_pressed(self):
        """
        Called when the save button is pressed.
        :return:
        """
        pass

    def reopen_object_window(self):
        """
        Closes and reopens the current object window.
        Returns:

        """
        pass

    def on_msgbtn_pressed(self, box: QMessageBox):
        """
        Called when an error message button is pressed.
        Args:
            box: Error message box created by error in save process.
            exit_parent: Should the new object window be closed.

        Returns:
            None
        """
        box.close()
        self.reopen_object_window()

    # Figshare API Functions
    # ======================

    def update_object(self, object_id: int, update_dict: dict):
        """
        Uploads changes to the Figshare object.
        Args:
            object_id: Figshare object ID number.
            update_dict: Dictionary with key, value pairs for info to update.

        Returns:

        """
        pass

    def invite_collaborators(self, object_id: int, collaborators: list):
        """
        Invites collaborators to a figshare project
        :param project_id: int. Figshare project id number
        :param token: OAuth token
        :param collaborators: List of Dict. Containing either user ids or email addresses
        :return:
        """
        pass
