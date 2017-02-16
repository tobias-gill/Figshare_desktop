import os
import math
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QAbstractItemView, QMessageBox, QMainWindow,
                             QFileDialog, QTreeWidgetItem, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidget)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.projects_windows.articles_window import ProjectsArticlesWindow

from figshare_interface import (Groups, Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class DataWindow(QWidget):

    def __init__(self, app, main_window):
        super().__init__()

        self.app = app
        self.main_window = main_window

        self.initUI()

    def initUI(self):

        self.formatWindow()

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        hbox.addLayout(self.set_root_layout())
        self.browser = self.set_file_browser()
        hbox.addWidget(self.browser)
        hbox.addLayout(self.selection_option_layout())

        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def formatWindow(self):
        main_window_loc = self.main_window.geometry()
        m_x0 = main_window_loc.x()
        m_y0 = main_window_loc.y()
        m_width = main_window_loc.width()
        m_height = main_window_loc.height()

        screen = self.app.primaryScreen().availableGeometry()

        x0 = m_x0 + m_width + 10
        y0 = m_y0
        self.w_width = screen.width() - x0
        self.w_height = screen.height() / 3

        self.setGeometry(x0, y0, self.w_width, self.w_height)

        self.setWindowFlags(Qt.FramelessWindowHint)

    def set_root_layout(self):
        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Preferred)

        btn_setRoot = QPushButton()
        btn_setRoot.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Folder-48.png')))
        btn_setRoot.setSizePolicy(sizepolicy)
        btn_setRoot.pressed.connect(self.on_set_root_pressed)

        layout = QVBoxLayout()
        layout.addWidget(btn_setRoot)
        return layout

    def on_set_root_pressed(self):

        dir_name = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        self.update_browser(dir_name)

    def set_file_browser(self):

        browser = QTreeWidget()
        header_lst = ['Name', 'Type', 'Size', 'Full Path']
        header = QTreeWidgetItem(header_lst)
        browser.setHeaderItem(header)
        browser.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for column in range(len(header_lst)):
            browser.resizeColumnToContents(column)
        return browser

    def update_browser(self, directory):

        header_lst = ['Name', 'Type', 'Size', 'Full Path']

        self.browser.clear()

        dirname = directory.split('/')[-1]
        tree_item = [directory, 'File Folder', '']
        parent = QTreeWidgetItem(tree_item)

        i = 0
        for dirname, dirnames, filenames in os.walk(directory):

            if i != 0:
                tree_item = [dirname, 'File Folder', '', '']
                child_dir = QTreeWidgetItem(tree_item)
                parent.addChild(child_dir)

                for subdirname in dirnames:
                    tree_item = [subdirname, 'File Folder', '', '']
                    child_sub_dir = QTreeWidgetItem(tree_item)
                    child_dir.addChild(child_sub_dir)

                for filename in filenames:
                    file_type = filename.split('.')[-1].upper() + ' File'
                    file_size = str(round(os.path.getsize(os.path.join(dirname, filename)) / 1000))
                    tree_item = [filename, file_type, file_size, os.path.abspath(dirname + '/' + filename)]
                    child_file = QTreeWidgetItem(tree_item)
                    child_dir.addChild(child_file)
            else:
                for filename in filenames:
                    file_type = filename.split('.')[-1].upper() + ' File'
                    file_size = str(round(os.path.getsize(os.path.join(dirname, filename)) / 1000)) + ' KB'
                    tree_item = [filename, file_type, file_size, os.path.abspath(dirname + '/' + filename)]
                    child_file = QTreeWidgetItem(tree_item)
                    parent.addChild(child_file)

            i = 1
            self.browser.addTopLevelItem(parent)
        self.browser.expandToDepth(0)
        for column in range(len(header_lst)):
            self.browser.resizeColumnToContents(column)

    def selection_option_layout(self):

        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Preferred)

        btn_selection = QPushButton()
        btn_selection.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Insert Row Below-48.png')))
        btn_selection.setSizePolicy(sizepolicy)

        btn_selection.pressed.connect(self.on_selection_pressed)
        if not self.main_window.centralWidget().selection_open:
            btn_selection.setEnabled(False)
        self.btn_selection = btn_selection
        vbox = QVBoxLayout()

        vbox.addWidget(btn_selection)

        return vbox

    def on_selection_pressed(self):

        items = self.article_tree.selectedItems()
        if len(items) != 0:
            self.selection_article_list = self.main_window.centralWidget().selection_window.selection_article_list
            for item in items:
                old_data = []
                for column in range(item.columnCount() + 1):
                    old_data.append(item.data(column, 0))
                new_data = ['Local', item.data(0, 0), '', '', '', item.data()]

                self.selection_article_list.append(QTreeWidgetItem(new_data))
            self.main_window.centralWidget().selection_window.update_article_list_layout()
