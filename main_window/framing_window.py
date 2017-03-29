"""

"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QMdiArea, QAction, qApp)
from PyQt5.QtGui import (QIcon, QFont, QKeySequence)

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
        self.project_article_window = None

        self.initUI()

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
