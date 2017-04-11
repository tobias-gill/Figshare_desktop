"""

"""

import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QMessageBox, QFileDialog, QAbstractItemView,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidgetItem,
                             QTreeWidget)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, pyqtSlot, pyqtSignal, QObject)

from Figshare_desktop.formatting.formatting import (press_button)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ArticleList(QWidget):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initLocal()
        self.initTree()
        self.initUI()

    def initThreads(self):
        """
        Intialises variable for threads
        :return:
        """
        self.__threads = []


    def initLocal(self):
        """
        Intialises the local article variables
        :return:
        """
        self.local_ids = set()

    def initUI(self):
        """
        Initialised the user interface
        :return:
        """
        hbox = QHBoxLayout()

        # Add the tree widget to the layout
        hbox.addWidget(self.initTree())

        self.setLayout(hbox)

    #####
    # Widgets
    #####

    def initTree(self):
        """
        Initialises the QTreeWidget to hold the articles prior to their upload to figshare
        :return:
        """
        tree = QTreeWidget()
        # Format the tree to allow for multiple items to be selected
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Allow for sorting of columns
        tree.setSortingEnabled(True)

        # Create the tree column headers
        headers = ['id', 'title']
        header_item = QTreeWidgetItem(headers)
        tree.setHeaderItem(header_item)

        self.tree = tree

        self.tree.itemDoubleClicked.connect(self.item_double_clicked)

        return self.tree

    #####
    # Widget Actions
    #####
    @pyqtSlot(bool)
    def fill_tree(self):
        """
        Clears and then re-fills the tree from the given set of local id numbers
        :param article_id_set: set of article id numbers
        :return:
        """
        self.tree.clear()
        for a_id in self.local_ids:
            # Create a tree widget item from the article id and title
            title = self.parent.local_articles[a_id].figshare_metadata['title']
            tree_item = QTreeWidgetItem([a_id, title])

            # Add to the tree
            self.tree.addTopLevelItem(tree_item)

            # Resize columns to contents
            for column in range(self.tree.columnCount()):
                self.tree.resizeColumnToContents(column)

    @pyqtSlot(str)
    def add_to_tree(self, local_article_id: str):
        """
        Adds a local article to the tree
        :param local_article_id: string containing the local article id number
        :return:
        """
        if local_article_id not in self.local_ids:
            # Add the id to the local set
            self.local_ids.add(local_article_id )

            # Create a tree widget item from the article id and title
            title = self.parent.local_articles[local_article_id].figshare_metadata['title']
            tree_item = QTreeWidgetItem([local_article_id, title])

            # Add to the tree
            self.tree.addTopLevelItem(tree_item)

            # Resize columns to contents
            for column in range(self.tree.columnCount()):
                self.tree.resizeColumnToContents(column)


    def item_double_clicked(self, item, column):

        article_id = item.text(0)
        self.remove_from_tree(article_id)

    @pyqtSlot(str)
    def remove_from_tree(self, local_article_id):
        """
        Attempts to remove an article from the tree
        :param local_article_id: string containing the local article id number
        :return:
        """
        self.local_ids.remove(local_article_id)
        self.fill_tree()


class TreeAddWorker(QObject):

    sig_step = pyqtSignal(str)
    sig_done = pyqtSignal(bool)

    def __init__(self, article_id_set):
        super().__init__()

        self.article_id_set = article_id_set

    @pyqtSlot()
    def work(self):
        """
        Adds articles to the tree
        :return:
        """
        while self.article_id_set:
            article_id = self.article_id_set.pop()
            self.sig_step.emit(article_id)

        self.sig_done.emit(True)