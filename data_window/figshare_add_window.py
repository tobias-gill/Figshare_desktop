"""

"""

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, pyqtSlot)

from Figshare_desktop.formatting.formatting import (press_button)
from Figshare_desktop.data_window.figshare_add_article_list import ArticleList
from Figshare_desktop.data_window.figshare_projects_button import ProjectButton
from Figshare_desktop.data_window.figshare_collections_button import CollectionButton
from Figshare_desktop.data_window.upload_control_widget import UploadControl
from Figshare_desktop.data_window.figsahre_upload_log import UploadLog

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class FigshareAddWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initFig()
        self.initUI()

    def initFig(self):

        self.upload_project = None
        self.upload_collection = None

    def initUI(self):
        """
        Initiates the user interface
        :return:
        """
        self.format_window()

        # Create a layout to hold all widgets
        hbox = QHBoxLayout()

        # Create the article list widget
        self.upload_queue = self.create_article_list()
        hbox.addWidget(self.upload_queue)

        hbox.addWidget(self.create_project_btn())
        hbox.addWidget(self.create_collections_btn())
        hbox.addWidget(self.create_control_btns())
        hbox.addWidget(self.create_log())

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

    def create_article_list(self):
        """
        Creates a QTreeWidget that hold articles until they have been added to figshare
        :return: QHBoxLayout
        """
        article_list = ArticleList(self.app, self.token, self.parent)

        return article_list

    def create_project_btn(self):
        """
        Creates a QPushButton that prompts the user to choose the figshare project to which to add the articles
        :return: QPushButton
        """
        project_btn = ProjectButton(self.app, self.token, self.parent)

        return project_btn

    def create_collections_btn(self):
        """
        Creates a QPushButton that prompts the user to choose a collection to directly add articles to
        :return: QPushButton
        """
        collection_btn = CollectionButton(self.app, self.token, self.parent)

        return collection_btn

    def create_control_btns(self):
        """
        Creates a Widget with buttons to control the upload process
        :return: QWidget
        """
        self.control_widget = UploadControl(self.app, self.token, self.parent)

        return self.control_widget

    def create_log(self):
        """
        Creates a QTextEdit that logs the interaction with Figshare
        :return: QTextEdit
        """
        self.upload_log = UploadLog(self.app, self.token, self.parent)

        return self.upload_log
