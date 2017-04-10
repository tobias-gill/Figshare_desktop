"""

"""
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.data_window.search_index import (ArticleIndex)
from Figshare_desktop.projects_windows.articles_window import ProjectsArticlesWindow
from Figshare_desktop.custom_widgets.local_article_list import LocalArticleList


__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class DataArticlesWindow(ProjectsArticlesWindow):

    def __init__(self, app, OAuth_token, parent):
        super(QMdiSubWindow, self).__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initIndex()
        self.initUI()

    def initIndex(self):
        """
        Initiates the Whoosh search index
        :return:
        """
        # Create the Article Index
        self.parent.local_article_index = ArticleIndex()

        # Create the default figshare metadata schema dictionary
        self.parent.local_article_index.create_schema('local_articles')

        self.parent.local_article_index.add_ID(schema='local_articles', field_name='id', stored=True)
        self.parent.local_article_index.add_TEXT('local_articles', 'title', True)
        self.parent.local_article_index.add_TEXT('local_articles', 'description')
        self.parent.local_article_index.add_KEYWORD('local_articles', 'tags', True)
        self.parent.local_article_index.add_ID('local_articles', 'references')
        self.parent.local_article_index.add_KEYWORD('local_articles', 'categories')
        self.parent.local_article_index.add_KEYWORD('local_articles', 'authors')
        self.parent.local_article_index.add_ID('local_articles', 'defined_type')
        self.parent.local_article_index.add_TEXT('local_articles', 'funding')
        self.parent.local_article_index.add_ID('local_articles', 'license')

        self.parent.local_article_index.document_types.add('article')

    def initUI(self):

        self.format_window()

        hbox = QHBoxLayout()
        self.article_tree = LocalArticleList(self.app, self.token, self.parent)
        hbox.addWidget(self.article_tree)

        window_widget = QWidget()
        window_widget.setLayout(hbox)
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

    ####
    # Local Article Index Functions
    ####


