"""

"""

import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QToolTip, QMessageBox, QMainWindow,
                             QAction, qApp, QHBoxLayout, QVBoxLayout, QSizePolicy, QShortcut)
from PyQt5.QtGui import (QIcon, QFont, QKeySequence)
from PyQt5.QtCore import (Qt)

from Figshare_desktop.projects_windows.projects_window import ProjectsWindow
from Figshare_desktop.data_window.data_window import DataWindow
from Figshare_desktop.selection_window.selection_window import SelectionWindow

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class MainWindow(QMainWindow):

    def __init__(self, app, OAuth_token):
        super().__init__()

        self.app = app
        self.token = OAuth_token

        self.articles = {}
        self.next_local_id = 0
        self.local_articles = {}

        self.initUI()

    def initUI(self):

        self.statusbar = self.statusBar()
        self.exitAction()

        self.place_menuBar()

        QToolTip.setFont(QFont('SansSerif', 10))

        self.setWindowTitle('Figshare Desktop')
        self.setWindowIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_logo.png')))

        self.setCentralWidget(Board(self.app, self.token, self))

        self.format_window()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            qApp.quit()
        else:
            event.ignore()

    def exitAction(self):
        self.exit_action = QAction(QIcon(os.path.abspath(__file__ + '/../..' + '/img/exit.png')), '&Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit Application')
        self.exit_action.triggered.connect(qApp.quit)

    def place_menuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.exit_action)

    def format_window(self):
        screen = self.app.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.setGeometry(0, 45, screen_rect.width() / 10, screen_rect.height()-45)


class Board(QWidget):

    def __init__(self, app, OAuth_token, main_window):
        super().__init__()

        self.app = app
        self.token = OAuth_token

        self.main_window = main_window

        self.projectsShortcut()

        self.initUI()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignCenter)

        self.place_projects_button()
        self.place_collections_button()
        self.place_data_button()
        self.place_selection_button()

        self.hbox = QHBoxLayout()
        self.hbox.addLayout(self.vbox)

        self.projects_open = False
        self.data_open = False
        self.selection_open = False

        self.setLayout(self.hbox)


    def place_projects_button(self):
        projects_btn = QPushButton('Projects', self)
        projects_btn.setCheckable(True)
        projects_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        projects_btn.setStatusTip('Toggle Projects Window')

        projects_btn.clicked[bool].connect(self.on_projects_btn_pressed)
        self.vbox.addWidget(projects_btn)

    def place_collections_button(self):
        collections_btn = QPushButton('Collections', self)
        collections_btn.setCheckable(True)
        collections_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        collections_btn.setStatusTip('Toggle Collections Window')

        collections_btn.clicked[bool].connect(self.on_collections_btn_pressed)

        self.vbox.addWidget(collections_btn)

    def place_data_button(self):
        data_btn = QPushButton('Data', self)
        data_btn.setCheckable(True)
        data_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        data_btn.setStatusTip('Toggle Data Window')

        data_btn.clicked[bool].connect(self.on_data_btn_pressed)

        self.vbox.addWidget(data_btn)

    def place_selection_button(self):
        selection_btn = QPushButton('Selection', self)
        selection_btn.setCheckable(True)
        selection_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        selection_btn.setStatusTip('Toggle Selection Window')

        selection_btn.clicked[bool].connect(self.on_selection_btn_pressed)

        self.vbox.addWidget(selection_btn)

    def on_projects_btn_pressed(self):
        if self.projects_open:
            self.projects_open = False
            self.projects_window.close()
        else:
            self.projects_open = True
            self.projects_window = ProjectsWindow(self.app, self.token, self.geometry(), self.main_window)
            self.projects_window.show()

    def projectsShortcut(self):
        self.projects_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.projects_shortcut.activated.connect(self.on_projects_btn_pressed)

    def on_collections_btn_pressed(self):
        print('collections')

    def on_data_btn_pressed(self):
        if self.data_open:
            self.data_open = False
            self.data_window.close()
        else:
            self.data_open = True
            self.data_window = DataWindow(self.app, self.token, self.main_window)
            self.data_window.show()

    def on_selection_btn_pressed(self):
        if self.selection_open:
            self.selection_open = False
            self.selection_window.deactivate_project_article_selection_btn()
            self.selection_window.deactivate_data_save_btn()
            self.selection_window.close()
        else:
            self.selection_open = True
            self.selection_window = SelectionWindow(self.app, self.token, self.main_window)
            self.selection_window.show()
