import os
import math
from PyQt5.QtWidgets import (QMdiSubWindow, QWidget, QLabel, QPushButton, QAbstractItemView, QMessageBox, QMainWindow,
                             QFileDialog, QTreeWidgetItem, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidget,
                             QFileSystemModel, QTreeView)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QObject, QThread, pyqtSignal, pyqtSlot)

from Figshare_desktop.formatting.formatting import (press_button, checkable_button)

from Figshare_desktop.figshare_articles.determine_type import gen_local_article
from Figshare_desktop.data_window.data_articles_window import DataArticlesWindow
from Figshare_desktop.article_edit_window.local_metadata_window import LocalMetadataWindow

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

        self.__threads = []

        self.initUI()

    def initUI(self):

        # Format the window
        self.format_window()

        # Create a horizontal layout to hold the widgets
        hbox = QHBoxLayout()

        # Add the widgets
        hbox.addWidget(self.set_directory_btn())
        hbox.addWidget(self.create_file_browser())
        hbox.addWidget(self.add_to_selection_btn())

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
        home_dir = os.path.expanduser("~")  # Define the initial root directory
        self.model.setRootPath(home_dir)
        self.browser.setModel(self.model)

        # Resize the first column
        self.browser.setColumnWidth(0, self.geometry().width() / 3)

        # Control how selection of items works
        #self.browser.setSelectionBehavior(QAbstractItemView.SelectItems)  # Allow for only single item selection
        self.browser.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Alow for multiple rows to be selected

        return self.browser

    def add_to_selection_btn(self):
        """
        Creates a QPushButton that can be used to open the metadata window for the selected items in the file browser
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Insert Row Below-48.png')))
        press_button(self.app, btn)  # Format button
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        btn.setToolTip("Add selected items to articles list")
        btn.setToolTipDuration(1)

        btn.pressed.connect(self.on_open_selection_clicked)

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
        file_paths = self.get_selection_set()
        article_tree = self.parent.data_articles_window.article_tree

        article_tree.disable_fields()

        worker = ArticleCreationWorker(self.token, self.parent, file_paths)

        load_articles_thread = QThread()
        load_articles_thread.setObjectName('local_articles_thread')
        self.__threads.append((load_articles_thread, worker))

        worker.moveToThread(load_articles_thread)

        worker.sig_step.connect(article_tree.add_to_tree)
        worker.sig_done.connect(article_tree.enable_fields)
        worker.sig_done.connect(article_tree.update_search_field)
        worker.sig_done.connect(self.parent.data_articles_window.check_edit)

        load_articles_thread.started.connect(worker.work)
        load_articles_thread.start()

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

    @staticmethod
    def get_child_files(path):
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


class ArticleCreationWorker(QObject):

    sig_step = pyqtSignal(str)
    sig_done = pyqtSignal(bool)

    def __init__(self, OAuth_token, parent, file_paths: set):
        super().__init__()

        self.token = OAuth_token
        self.parent = parent
        self.file_paths = file_paths

    @pyqtSlot()
    def work(self):
        """

        :return:
        """
        while self.file_paths:
            path = self.file_paths.pop()
            print(path)
            local_id = self.create_local_article(path)
            self.sig_step.emit(local_id)
        self.sig_done.emit(True)

    def create_local_article(self, file_path):
        """
        Creates a local article of the given file
        :param file_path: string.
        :return:
        """
        # Check if an article does not already exist with the same title
        article_exists, local_id = self.does_local_article_exist(file_path)

        if not article_exists:

            # set the local file id number
            local_id = 'local_' + str(self.parent.next_local_id)
            # Create local article
            self.parent.local_articles[local_id] = gen_local_article(self.token, file_path)
            # Set id number
            self.parent.local_articles[local_id].figshare_metadata['id'] = local_id
            # Increment next local id counter
            self.parent.next_local_id += 1

            # locally define the local article index for convenience
            local_article_index = self.parent.local_article_index

            # Get the article type
            article = self.parent.local_articles[local_id]
            article_type = article.figshare_metadata['type']

            # Check to see if the article type has been added to the articles index
            # If not we will need to add new fields to the index for the new file type
            if article_type not in local_article_index.document_types:
                # Add the new file type to the set of types included in the index
                local_article_index.document_types.add(article_type)

                # Define the schema we wish to add fields to
                schema = 'local_articles'

                # From the article type created get the index dictionary and add fields to the index appropriately
                for field_name, field_type in article.index_schema().items():
                    if field_type[0] == 'id':
                        local_article_index.add_ID(schema=schema, field_name=field_name, stored=field_type[1],
                                                   unique=True)
                    elif field_type[0] == 'text':
                        local_article_index.add_TEXT(schema, field_name, field_type[1])
                    elif field_type[0] == 'keyword':
                        local_article_index.add_KEYWORD(schema, field_name, field_type[1])
                    elif field_type[0] == 'numeric':
                        local_article_index.add_NUMERIC(schema, field_name, field_type[1])
                    elif field_type[0] == 'datetime':
                        local_article_index.add_DATETIME(schema, field_name, field_type[1])
                    elif field_type[0] == 'boolean':
                        local_article_index.add_BOOLEAN(schema, field_name, field_type[1])
                    elif field_type[0] == 'ngram':
                        local_article_index.add_NGRAM(schema, field_name, field_type[1])

            # Get a single dictionary of all fields associated to the article
            document_dict = {}
            for d in article.input_dicts():
                document_dict = {**document_dict, **d}

            # Add document to Index
            local_article_index.addDocument(schema='local_articles', data_dict=document_dict)

            return local_id

        # Else if an existing article:
        else:
            return local_id


    def does_local_article_exist(self, file_path: str):
        """
        Checks to see if an article already exists with the same title
        :param file_path:
        :return:
        """
        # Get the file name from the full path
        file_name = os.path.split(file_path)[-1]

        # locally define the local article index for convenience
        local_article_index = self.parent.local_article_index

        # If there is the local article schema present
        if 'local_articles' in local_article_index.list_schema():

            # Initially set article exists as False
            exists = False

            # Search for articles with the same title as the current file name
            results = local_article_index.perform_search(schema='local_articles', field='title', query=file_name)

            # Check in the results given if there is a document with the same title as the file name
            for doc_num, val_dict in results.items():
                # If one is found return true
                if 'title' in val_dict:
                    if val_dict['title'] == file_name:
                        exists = True
                        local_id = val_dict['id']
                        break
            if exists:
                return True, local_id
            # If we get here then no results had the same title (within the top ten hits) so return false
            else:
                return False, None
