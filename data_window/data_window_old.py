import os
import math
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QAbstractItemView, QMessageBox, QMainWindow,
                             QFileDialog, QTreeWidgetItem, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidget)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.figshare_articles.determine_type import gen_local_article
from Figshare_desktop.article_edit_window.local_article_edit_window import LocalArticleEditWindow

from figshare_interface import (Groups, Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class DataWindow(QWidget):

    def __init__(self, app, OAuth_token, main_window):
        super().__init__()

        self.app = app
        self.token = OAuth_token
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

        self.local_article_edit_window_open = False

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

    def closeEvent(self, event):
        """
        When window is closed checks to see if the local_article_edit_window is open. If so, it too will be closed.
        :param event: Close event.
        :return:
        """

        # Check to see if local_article_edit_window is open
        if self.local_article_edit_window_open:
            self.local_metadata_window.close()

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
        btn_selection.setCheckable(True)
        btn_selection.clicked[bool].connect(self.on_selection_pressed)
        self.btn_selection = btn_selection
        vbox = QVBoxLayout()

        vbox.addWidget(self.btn_selection)

        return vbox

    def on_selection_pressed(self):
        """
        Actions to perform when the selected files are to be
        :return:
        """

        if self.local_article_edit_window_open:
            self.local_article_edit_window_open = False
            self.local_metadata_window.close()
        else:
            self.local_article_edit_window_open = True
            items = self.browser.selectedItems()

            header_item = self.browser.headerItem()
            for column in range(header_item.columnCount()):
                if header_item.data(column, 0) == 'Full Path':
                    filename_element = column
                elif header_item.data(column, 0) == 'Type':
                    type_element = column

            local_articles = self.main_window.local_articles
            next_local_id = self.main_window.next_local_id

            if items != []:
                articles_set = set()
                for article in items:
                    if article.data(type_element, 0) != 'File Folder':
                        local_id = 'L' + str(next_local_id)
                        local_articles[local_id] = gen_local_article(self.token, article.data(filename_element, 0))
                        local_articles[local_id].figshare_metadata['id'] = local_id
                        articles_set.add(local_id)
                        next_local_id += 1

                self.local_metadata_window = LocalArticleEditWindow(self.app, self.token, self.main_window,
                                                                    self.geometry(), articles_set)
                self.local_metadata_window.show()
