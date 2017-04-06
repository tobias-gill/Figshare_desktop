import os
import math
from PyQt5.QtWidgets import (QMdiSubWindow, QWidget, QLabel, QPushButton, QAbstractItemView, QMessageBox, QMainWindow,
                             QFileDialog, QTreeWidgetItem, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidget,
                             QFileSystemModel, QTreeView)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.formatting.formatting import (press_button, checkable_button)

from Figshare_desktop.figshare_articles.determine_type import gen_local_article
from Figshare_desktop.article_edit_window.local_article_edit_window import LocalMetadataWindow

from figshare_interface import (Groups, Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class DataWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initUI()

    def initUI(self):

        # Format the window
        self.format_window()

        # Create a horizontal layout to hold the widgets
        hbox = QHBoxLayout()

        # Add the widgets
        hbox.addWidget(self.set_directory_btn())
        hbox.addWidget(self.create_file_browser())
        hbox.addWidget(self.open_selection_btn())

        # Create a central widget for the local data window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(hbox)
        # Set the projects window widget
        self.setWidget(window_widget)

    def format_window(self):
        """
        Form the local data window
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
        # Remove frame from projects window
        self.setWindowFlags(Qt.FramelessWindowHint)

    #####
    # Window Widgets
    #####

    def set_directory_btn(self):
        """
        Creates a QPushButton that can be used to set the current root directory
        :return: QPushButton
        """

        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Folder-48.png')))
        press_button(self.app, btn)  # Format button
        btn.setToolTip("Select local directory")
        btn.setToolTipDuration(1)

        btn.pressed.connect(self.on_set_directory_pressed)

        return btn

    def create_file_browser(self):
        """
        Creates a QTreeView with a QFileSystemModel that is used as a file browser
        :return: QTreeview
        """

        self.browser = QTreeView()

        # Set the model of the QTreeView
        self.model = QFileSystemModel()
        self.model.setRootPath('')  # Define the initial root directory
        self.browser.setModel(self.model)

        # Control how selection of items works
        #self.browser.setSelectionBehavior(QAbstractItemView.SelectItems)  # Allow for only single item selection
        self.browser.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Alow for multiple rows to be selected

        return self.browser

    def open_selection_btn(self):
        """
        Creates a QPushButton that can be used to open the metadata window for the selected items in the file browser
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Insert Row Below-48.png')))
        checkable_button(self.app, btn)  # Format button
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        btn.setToolTip("Open metadata window for selection")
        btn.setToolTipDuration(1)

        btn.clicked[bool].connect(self.on_open_selection_clicked)

        return btn

    #####
    # Widget Actions
    #####

    def on_set_directory_pressed(self):
        """
        Called when the set root directory button is pressed
        :return:
        """
        dir_name = self.user_set_dir()
        self.browser.setRootIndex(self.model.index(dir_name))

    def user_set_dir(self):
        """
        Creates a QFileDialog that prompts the user to choose a root directory
        :return: Sting. directory path
        """
        return str(QFileDialog.getExistingDirectory(self, "Select Directory"))

    def on_open_selection_clicked(self):
        """
        Called when the open selection button is clicked. Either open or closes the metadata window
        :return:
        """
        if 'local_metadata_window' in self.parent.open_windows:
            self.parent.open_windows.remove('local_metadata_window')
            self.parent.local_metadata_window.close()

        else:
            file_paths = self.get_selection_set()

            self.parent.open_windows.add('local_metadata_window')
            self.parent.local_metadata_window = LocalMetadataWindow(self.app, self.token, self.parent, file_paths)
            self.parent.mdi.addSubWindow(self.parent.local_metadata_window)
            self.parent.local_metadata_window.show()

    def get_selection_set(self):
        """
        Creates a set of selected item file paths.
        :return:
        """
        # Get a list of selected items from the QTreeview
        items = self.browser.selectedIndexes()

        # Create an empty set to add file paths to
        file_paths = set()
        for item in items:
            # For items that are not directories
            if not self.model.isDir(item):
                file_paths.add(self.model.filePath(item))  # Add the item file path
            else:
                # Combine the current set with a set of files contained within the directory. Does not recursively
                # open contained directories
                contained_files = self.get_child_files(self.model.filePath(item))
                if contained_files is not None:
                    file_paths |= contained_files

        return file_paths

    def get_child_files(self, path):
        """
        given a path to a directory will return a set of file paths contained within. Does not recursively open internal
        directories
        :param path: string. path to directory
        :return: set. Containing file paths
        """
        dir = os.path.normpath(path)
        if os.path.isdir(dir):
            dir_contents = os.listdir(dir)

            file_set = set()
            for item in dir_contents:
                if not os.path.isdir(item):
                    file_set.add(os.path.join(dir, item))
            return file_set
        else:
            return None