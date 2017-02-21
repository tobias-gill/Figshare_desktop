"""

"""

import os
import itertools
from requests.exceptions import HTTPError

from PyQt5.QtWidgets import (QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QAbstractItemView,
                             QHBoxLayout, QVBoxLayout, QSizePolicy, QMessageBox)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import (Qt, QPoint)

from figshare_interface import (Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class SelectionWindow(QWidget):

    def __init__(self, app, OAuth_token, main_window):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.main_window = main_window

        self.selection_article_list = set()

        self.initUI()

    def initUI(self):

        self.formatWindow()

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        self.current_view = 'list'
        self.hbox.addLayout(self.view_options_layout())
        self.hbox.addWidget(self.create_article_layout(self.current_view))
        self.hbox.addLayout(self.upload_layout())

        self.selection_open = self.main_window.centralWidget().selection_open

        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

        self.activate_project_article_selection_btn()
        self.activate_data_save_btn()

    def formatWindow(self):

        mw_geom = self.main_window.geometry()

        mw_x0 = mw_geom.x()
        mw_y0 = mw_geom.y()
        mw_width = mw_geom.width()
        mw_height = mw_geom.height()

        screen = self.app.primaryScreen().availableGeometry()

        x0 = mw_x0 + mw_width + 10
        y0 = mw_y0 + 0.75 * screen.height()
        self.w_width = screen.width() - x0
        self.w_height = (mw_y0 + mw_height) - y0

        self.setGeometry(x0, y0, self.w_width, self.w_height)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def view_options_layout(self):

        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Preferred)

        btn_list = QPushButton()
        btn_list.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Bulleted List-50.png')))
        btn_list.setCheckable(True)
        btn_list.toggle()
        btn_list.setSizePolicy(sizepolicy)
        btn_list.clicked[bool].connect(lambda: self.change_view('list'))
        self.list_view_btn = btn_list

        btn_thumb = QPushButton()
        btn_thumb.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + 'img/Picture-64.png')))
        btn_thumb.setCheckable(True)
        btn_thumb.setSizePolicy(sizepolicy)
        btn_thumb.clicked[bool].connect(lambda: self.change_view('thumb'))
        self.thumb_view_btn = btn_thumb

        layout = QVBoxLayout()

        layout.addWidget(self.list_view_btn)
        layout.addWidget(self.thumb_view_btn)

        return layout

    def change_view(self, view):
        if self.current_view == view:
            if view == 'list':
                self.list_view_btn.toggle()
                self.current_view = 'list'
            else:
                self.thumb_view_btn.toggle()
                self.current_view = 'thumb'
        else:
            if view == 'list':
                self.thumb_view_btn.toggle()
                self.current_view = 'list'
            else:
                self.list_view_btn.toggle()
                self.current_view = 'thumb'

    def create_article_layout(self, view):

        if view == 'list':
            return self.article_list_layout()

        elif view == 'thumb':
            return self.create_article_layout('list')

    def article_list_layout(self):

        lst = QTreeWidget()
        header_lst = ["Location", "Title", "id", "Status", "Tags"]
        header = QTreeWidgetItem(header_lst)
        lst.setHeaderItem(header)
        lst.setSelectionMode(QAbstractItemView.ExtendedSelection)

        for article in self.selection_article_list:
            lst.addTopLevelItem(article)

        for column in range(len(header_lst)):
            lst.resizeColumnToContents(column)

        self.article_tree = lst

        return self.article_tree

    def update_article_list_layout(self, headers=None):
        """
        Re-formats the selection window QTreeWidget by a given set of column headers.
        :param headers: List of strings containing metadata field names.
        :return:
        """
        # Set headers to default if none are given.
        if headers is None:
            headers = ["location", "title", "id", "status", "tags"]

        self.article_tree.clear()

        # Iterate through the article ids.
        for article_id in self.selection_article_list:

            # Get the type of the article
            article_type = type(article_id)
            if article_type is not str:
                # If the article id is not a string it is likely an integer id for a figshare article. If so make it a
                # string.
                if article_type is int:
                    article_id = str(article_id)
                # Otherwise it is an unrecognised format and should be ignored.
                else:
                    article_id = None

            # From the string value of the article_id determine if it is a local file.
            # Local ids are prepended by an 'L'.
            if article_id is not None:
                if article_id[0] == 'L':
                    # Get article from local articles
                    article = self.main_window.local_articles[article_id]
                else:
                    # Get article from figshare articles
                    article = self.main_window.articles[article_id]

                # generate a qtreewidgetitem from the article and headers list.
                article.gen_qtree_item(headers)
                # Add qtreeitem as top level item in the tree.
                self.article_tree.addTopLevelItem(article.qtreeitem)

        # Format the Qtreewidget
        for column in range(len(headers)):
            # Set the width of the columns to the data.
            self.article_tree.resizeColumnToContents(column)
        # sort the list by local or figshare.
        self.article_tree.sortItems(0, Qt.AscendingOrder)

    def upload_layout(self):

        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Preferred)

        btn_upload = QPushButton()
        btn_upload.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_upload.png')))
        btn_upload.setSizePolicy(sizepolicy)
        btn_upload.pressed.connect(self.upload_selection)
        self.upload_btn = btn_upload

        layout = QVBoxLayout()

        layout.addWidget(self.upload_btn)

        return layout

    def upload_selection(self):

        header_item = self.article_tree.headerItem()
        for column in range(header_item.columnCount()):
            if header_item.data(column, 0) == 'id':
                id_element = column
                break

        tree_items = self.article_tree.selectedItems()

        article_ids = []
        for item in tree_items:
            article_ids.append(item.data(id_element, 0))

        if tree_items == []:
            reply = QMessageBox.question(self, 'Message', "Upload all files?",
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                article_ids = []
                for row in range(self.article_tree.topLevelItemCount()):
                    article_item = self.article_tree.topLevelItem(row)
                    article_ids.append(article_item.data(id_element, 0))
            else:
                article_ids = None

        if article_ids != None:
            upload_type, upload_id = self.projects_or_collections_upload()
            if upload_type == 'project':
                # Can only upload new files to a project. Cannot move figshare_articles between existing projects.
                #Iterate through the selected articles.
                for article in article_ids:
                    # Check that the article is a local file.
                    if article[0] == 'L':
                        self.upload_to_project(article, upload_id)
                    else:
                        pass
            elif upload_type == 'collection':
                # Can only add exsiting figshare_articles to a collection.
                pass

    def projects_or_collections_upload(self):

        if self.main_window.centralWidget().projects_open:
            projects_window = self.main_window.centralWidget().projects_window
            if projects_window.projects_info_open:
                projects_info_window = projects_window.projects_info_window
                if projects_info_window.articles_window_open:
                    return 'project', projects_info_window.project_id

        else:
            return 'collection', 'collection_id'

    def upload_to_project(self, local_article_id,  project_id):
        """
        Uploads a local file to a given figshare project.
        :param local_article_id: str. ID of local file to be uploaded.
        :param project_id: int. Project ID for file to be uploaded to.
        :return:
        """
        # Get the local article
        local_article = self.main_window.local_articles[local_article_id]
        # Generate the upload dictionary.
        upload_dict = local_article.get_upload_dict()

        local_file_location = local_article.figshare_desktop_metadata['location']
        # Upload file to project.
        projects = Projects(self.token)
        try:
            figshare_article_id = projects.create_article(project_id, upload_dict)
            projects.upload_file(figshare_article_id, local_file_location)
        except FileExistsError as err:
            print(err)
        except HTTPError as err:
            print(err)

    def activate_project_article_selection_btn(self):
        if self.main_window.centralWidget().projects_open:
            if self.main_window.centralWidget().projects_window.projects_info_open:
                if self.main_window.centralWidget().projects_window.projects_info_window.articles_window_open:
                    window = self.main_window.centralWidget().projects_window.projects_info_window
                    window.articles_window.btn_selection.setEnabled(True)

    def deactivate_project_article_selection_btn(self):
        if self.main_window.centralWidget().projects_open:
            if self.main_window.centralWidget().projects_window.projects_info_open:
                if self.main_window.centralWidget().projects_window.projects_info_window.articles_window_open:
                    window = self.main_window.centralWidget().projects_window.projects_info_window
                    window.articles_window.btn_selection.setEnabled(False)

    def activate_data_save_btn(self):
        if self.main_window.centralWidget().data_open:
            if self.main_window.centralWidget().data_window.local_article_edit_window_open:
                window = self.main_window.centralWidget().data_window.local_metadata_window
                window.btn_save.setEnabled(True)

    def deactivate_data_save_btn(self):
        if self.main_window.centralWidget().data_open:
            if self.main_window.centralWidget().data_window.local_article_edit_window_open:
                window = self.main_window.centralWidget().data_window.local_metadata_window
                window.btn_save.setEnabled(False)
