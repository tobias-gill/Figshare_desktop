"""

"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QMdiArea, QAction, qApp)
from PyQt5.QtGui import (QIcon, QFont, QKeySequence)

# Figshare API Imports
from figshare_interface.http_requests.figshare_requests import issue_request

from ..formatting.formatting import scaling_ratio
from .section_window import sectionWindow

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class MainWindow(QMainWindow):
    """

    """

    def __init__(self, app, OAuth_token):
        """
        Initialization of the Main window
        :param app:
        :param OAuth_token:
        """
        super().__init__()

        self.app = app
        self.token = OAuth_token

        self.open_windows = set()

        # Menu window
        self.section_window = None

        # Projects Windows
        self.projects_window = None
        self.new_project_window = None
        self.project_info_window = None
        self.project_articles_window = None
        self.article_edit_window = None

        # Collection Windows
        self.collections_window = None
        self.new_collection_window = None
        self.collection_info_window = None
        self.collection_aticles_window = None

        # Local Data Windows
        self.local_data_window = None
        self.data_articles_window = None
        self.local_article_edit_window = None

        self.local_article_index = None

        self.initFig()
        self.initUI()

    def initFig(self):
        """
        Initialization of Figshare data
        :return:
        """
        self.figshare_articles = {}

        self.local_articles = {}
        self.next_local_id = 0

        self.categories = self.get_figshare_cats()

    def initUI(self):
        """
        User Interface initialization
        """
        # Create a multiple document interface object
        self.mdi = QMdiArea()
        # Set the main window central widget as the MDI area
        self.setCentralWidget(self.mdi)

        self.format_window()
        self.setWindowTitle('Figshare Desktop')
        self.setWindowIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_logo.png')))

        self.menu_bar()

        # Add Section Window
        self.section_window = sectionWindow(self.app, self.token, parent=self)
        self.mdi.addSubWindow(self.section_window)
        self.section_window.show()

    def format_window(self):
        """
        Maximizes the main window
        """
        self.showMaximized()
        geom = self.geometry()
        x0 = geom.x()
        y0 = geom.y()

        geom = self.app.primaryScreen().availableGeometry()
        w = geom.width() - x0
        h = geom.height() - y0

        self.setGeometry(x0, y0, w, h)

    def menu_bar(self):
        """

        """
        bar = self.menuBar()

        file = bar.addMenu('&File')
        file.addAction(self.exitAction())

    def exitAction(self):
        """

        :return: QAction
        """
        self.exit_action = QAction(QIcon(os.path.abspath(__file__ + '/../..' + '/img/exit.png')), '&Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(qApp.quit)
        return self.exit_action

    # Figshare API Functions
    # ======================

    def get_figshare_cats(self):
        """
        Creates a dictionary object with collection id: name pairs.
        Returns:
            cat_dict (dict): Figshare categories dictionary.
        """
        # Get a dictionary of categories from Figshare with id and name pairs
        allowed_cats = issue_request(method='GET', endpoint='categories', token=self.token)
        cat_dict = {}
        for cat in allowed_cats:
            cat_dict[cat['id']] = cat['title']

        return cat_dict
