"""

"""
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QThread, pyqtSlot)

from Figshare_desktop.formatting.formatting import (press_button)
from Figshare_desktop.data_window.search_index import (ArticleIndex)
from Figshare_desktop.article_edit_window.local_metadata_window import LocalMetadataWindow
from Figshare_desktop.custom_widgets.local_article_list import LocalArticleList
from Figshare_desktop.data_window.figshare_add_article_list import TreeAddWorker


__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class DataArticlesWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.__threads = []

        self.initIndex()
        self.initUI()

    def initIndex(self):
        """
        Initiates the Whoosh search index
        :return:
        """

        if self.parent.local_article_index is None:

            # Create the Article Index
            self.parent.local_article_index = ArticleIndex()

            # Create the default figshare metadata schema dictionary
            self.parent.local_article_index.create_schema('local_articles')

            self.parent.local_article_index.add_ID(schema='local_articles', field_name='id', stored=True, unique=True)
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

        # Create layout for the control buttons
        control_btns_layout = QVBoxLayout()
        # Add control buttons
        control_btns_layout.addWidget(self.delete_btn())
        control_btns_layout.addWidget(self.project_btn())

        # Create the article tree
        self.article_tree = LocalArticleList(self.app, self.token, self.parent)

        # Create edit button layout
        edit_layout = QVBoxLayout()
        # Add the edit button
        edit_layout.addWidget(self.edit_btn())

        # Create encompassing horizontal layout
        hbox = QHBoxLayout()

        # Add the control buttons layout
        hbox.addLayout(control_btns_layout)
        # Add the article tree
        hbox.addWidget(self.article_tree)
        # Add the edit button layout
        hbox.addLayout(edit_layout)

        # Set the widget and layout of the sub window
        window_widget = QWidget()
        window_widget.setLayout(hbox)
        self.setWidget(window_widget)

        self.check_edit()

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
    # Window Widgets
    ####

    def delete_btn(self):
        """
        Creates a QPushButton that can be used to remove local articles from the list and memory
        :return:
        """

        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/delete.png')))
        btn.setToolTip('Delete selected articles')
        btn.setToolTipDuration(1)
        press_button(self.app, btn)

        btn.pressed.connect(self.on_delete_pressed)

        return btn

    def project_btn(self):
        """
        Creates a QPushButton than can be used to add selected articles to an existing figshare project
        :return:
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Insert Row Below-48.png')))
        btn.setToolTip('Add selection to upload queue')
        btn.setToolTipDuration(1)
        press_button(self.app, btn)

        btn.pressed.connect(self.on_project_pressed)

        self.proj_btn = btn
        return self.proj_btn

    def edit_btn(self):
        """
        Creates a QPushButton that opens the metadata edit window for the selected articles.
        :return:
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Pencil-52.png')))
        btn.setToolTip('Edit metadata of selected articles')
        btn.setToolTipDuration(1)
        press_button(self.app, btn)

        btn.pressed.connect(self.on_edit_pressed)

        btn.setEnabled(False)
        self.edit_btn = btn
        return self.edit_btn

    #####
    # Widget Actions
    #####

    @pyqtSlot(bool)
    def check_edit(self):
        """

        :return:
        """
        if self.article_tree.tree.topLevelItemCount() == 0:
            self.disable_edit()
        else:
            self.enable_edit()

    def enable_edit(self):
        """
        Enables the edit QPushButton
        :return:
        """
        self.edit_btn.setEnabled(True)

    def disable_edit(self):
        """
        Disables the edit QPushButton
        :return:
        """
        self.edit_btn.setEnabled(False)

    def on_delete_pressed(self):
        """
        Called when the delete article button is pressed
        :return:
        """
        selection_ids = self.article_tree.get_selection()

        for article_id in selection_ids:
            # Remove article from the set of tree articles
            self.article_tree.article_ids.remove(article_id)
            # Remove article from the dictionary of local articles
            del(self.parent.local_articles[article_id])

            # Get the doc num for the article in the index
            results = self.parent.local_article_index.perform_search(schema='local_articles', field='id',
                                                                     query=article_id)

            # Check that returned results explicitly match the article id. If so them remove the document from the index
            for doc_num, val_dict in results.items():
                if val_dict['id'] == article_id:
                    self.parent.local_article_index.removeDocument(schema='local_articles', docnum=doc_num)

        # Re-fill the tree
        self.article_tree.fill_tree(self.article_tree.tree_headers, self.article_tree.articles_ids)
        self.check_edit()

    def on_edit_pressed(self):
        """
        Called when the edit article button is pressed. Opens the local article edit window
        :return:
        """
        # Get the list of selected articles
        selected_articles = list(self.article_tree.get_selection())

        if selected_articles != []:
            # Close the article list window
            self.parent.open_windows.remove('data_articles_window')
            self.parent.data_articles_window.close()

            # Create and open the article edit window
            self.parent.open_windows.add('local_article_edit_window')
            self.parent.local_article_edit_window = LocalMetadataWindow(self.app, self.token, self.parent,
                                                                        selected_articles)
            self.parent.mdi.addSubWindow(self.parent.local_article_edit_window)
            self.parent.local_article_edit_window.show()

    def on_project_pressed(self):
        """
        Called when the add to upload queue button is pressed
        :return:
        """
        article_id_set = self.article_tree.get_selection()
        upload_queue = self.parent.figshare_add_window.upload_queue

        worker = TreeAddWorker(article_id_set)
        worker.sig_step.connect(upload_queue.add_to_tree)

        queue_add_thread = QThread()
        self.__threads.append((queue_add_thread, worker))

        worker.moveToThread(queue_add_thread)

        queue_add_thread.started.connect(worker.work)
        queue_add_thread.start()
