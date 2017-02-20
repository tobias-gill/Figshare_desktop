"""

"""

import os
from PyQt5.QtWidgets import (QWidget, QAbstractItemView, QPushButton, QTreeWidget, QTreeWidgetItem, QFileDialog,
                             QHBoxLayout, QVBoxLayout, QSizePolicy, QMessageBox)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import (Qt, QPoint)


from Figshare_desktop.figshare_articles.determine_type import gen_article
from Figshare_desktop.article_edit_window.article_edit_window import ArticleEditWindow

from figshare_interface.http_requests.figshare_requests import download_file
from figshare_interface import (Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ProjectsArticlesWindow(QWidget):

    def __init__(self, app, OAuth_token, projects_info_window_loc, main_window, project_id):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.projects_info_window_loc = projects_info_window_loc
        self.main_window = main_window

        self.project_id = project_id

        self.initFigshare()
        self.initUI()

    def initFigshare(self):
        self.get_article_list()

    def initUI(self):

        self.formatWindow()

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        self.selection_open = self.main_window.centralWidget().selection_open

        self.current_view = 'list'
        hbox.addLayout(self.view_options_layout())
        hbox.addWidget(self.create_article_layout(self.current_view))
        hbox.addLayout(self.selection_option_layout())

        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def formatWindow(self):

        piw_x0 = self.projects_info_window_loc.x()
        piw_y0 = self.projects_info_window_loc.y()
        piw_width = self.projects_info_window_loc.width()
        piw_height = self.projects_info_window_loc.height()

        screen = self.app.primaryScreen().availableGeometry()

        x0 = piw_x0
        y0 = piw_y0 + piw_height + 10
        self.w_width = screen.width() - x0
        self.w_height = screen.height() / 3

        self.setGeometry(x0, y0, self.w_width, self.w_height)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def get_article_list(self):

        self.article_list = []
        projects = Projects(self.token)

        page_size = 100
        page = 1
        result_len = page_size
        while result_len == page_size:
            result = projects.list_articles(self.project_id, page_size=page_size, page=page)
            for article in result:
                self.article_list.append(article)
            result_len = len(result)
            page += 1

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
        header_list = ["Title", "id", "Created", "Up-To-Date", "Type", "Tags"]
        header = QTreeWidgetItem(header_list)
        lst.setHeaderItem(header)
        lst.setSelectionMode(QAbstractItemView.ExtendedSelection)

        input_list = ['title', 'id', 'created_date', 'up_to_date', 'type', 'tags']

        for article in self.article_list:
            if article['id'] in self.main_window.articles:
                temp_article = self.main_window.articles[article['id']]
                temp_article.gen_qtree_item(input_list, temp_article.input_dicts())
                lst.addTopLevelItem(temp_article.qtreeitem)

            else:
                temp_article = gen_article(article['title'], self.token, self.project_id, article['id'])
                temp_article.gen_qtree_item(input_list, temp_article.input_dicts())

                lst.addTopLevelItem(temp_article.qtreeitem)
                self.main_window.articles[article['id']] = temp_article

        for column in range(len(header_list)):
            lst.resizeColumnToContents(column)

        self.article_tree = lst

        return self.article_tree

    def selection_option_layout(self):

        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Preferred)

        btn_upload = QPushButton()
        btn_upload.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_upload.png')))
        btn_upload.setSizePolicy(sizepolicy)
        btn_upload.pressed.connect(self.on_upload_pressed)

        btn_download = QPushButton()
        btn_download.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_download.png')))
        btn_download.setSizePolicy(sizepolicy)
        btn_download.pressed.connect(self.on_download_pressed)

        btn_selection = QPushButton()
        btn_selection.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Insert Row Below-48.png')))
        btn_selection.setSizePolicy(sizepolicy)

        btn_selection.pressed.connect(self.on_selection_pressed)
        if not self.main_window.centralWidget().selection_open:
            btn_selection.setEnabled(False)
        self.btn_selection = btn_selection
        vbox = QVBoxLayout()

        vbox.addWidget(btn_upload)
        vbox.addWidget(btn_download)
        vbox.addWidget(btn_selection)

        btn_edit = QPushButton()
        btn_edit.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        btn_edit.setSizePolicy(sizepolicy)
        btn_edit.pressed.connect(self.on_edit_pressed)

        vbox_1 = QVBoxLayout()

        vbox_1.addWidget(btn_edit)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_1)
        hbox.addLayout(vbox)

        return hbox

    def on_upload_pressed(self):

        items = self.article_tree.selectedItems()
        if len(items) != 0:
            article_list = []
            for item in items:
                article_list.append(item.data(1, 0))

            articles = self.main_window.articles

            for article_id in article_list:
                a_id = int(article_id)
                if articles[a_id].figshare_metadata['up_to_date'] is False:
                    Projects.publish_article(self.token, a_id)
                    title = articles[a_id].figshare_metadata['title']
                    project = articles[a_id].project_id
                    articles[a_id] = gen_article(title, self.token, project, a_id)
            for i in range(2):
                self.main_window.centralWidget().projects_window.projects_info_window.on_show_articles_pressed()

    def on_download_pressed(self):

        items = self.article_tree.selectedItems()
        if len(items) != 0:
            article_list = []
            for item in items:
                article_list.append(item.data(1, 0))

            downloads = []
            for article in article_list:
                file_list = Projects(self.token).list_files(article)
                for file in file_list:
                    if file['name'][-4:] != '.png':
                        downloads.append([file['name'], file['download_url']])

            download_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

            for file in downloads:
                local_path = os.path.abspath(download_dir + '/' + file[0])
                url = file[1]
                download_file(url, local_path, self.token)

    def on_selection_pressed(self):

        items = self.article_tree.selectedItems()
        if len(items) != 0:
            self.selection_article_list = self.main_window.centralWidget().selection_window.selection_article_list
            for item in items:

                old_data = []
                for column in range(item.columnCount() + 1):
                    old_data.append(item.data(column, 0))
                new_data = ['Figshare']
                for column in range(len(old_data)):
                    new_data.append(old_data[column])
                self.selection_article_list.append(QTreeWidgetItem(new_data))
            self.main_window.centralWidget().selection_window.update_article_list_layout()

    def on_edit_pressed(self):
        items = self.article_tree.selectedItems()

        header_item = self.article_tree.headerItem()
        for column in range(header_item.columnCount()):
            if header_item.data(column, 0) == 'id':
                id_element = column
                break

        if len(items) > 1:
            reply = QMessageBox.question(self, 'Message', "Edit multiple files?",
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                article_ids = []
                for article in items:
                    article_ids.append(article.data(id_element, 0))
            else:
                article_ids = None

        elif len(items) == 1:
            article_ids = [items[0].data(id_element, 0)]

        elif items == []:
            reply = QMessageBox.question(self, 'Message', "Edit all files?",
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                article_ids = []
                for row in range(self.article_tree.topLevelItemCount()):
                    article_item = self.article_tree.topLevelItem(row)
                    article_ids.append(article_item.data(id_element, 0))
            else:
                article_ids = None

        if article_ids is not None:

            self.main_window.centralWidget().projects_window.projects_info_window.on_show_articles_pressed()
            self.article_edit_window = ArticleEditWindow(self.app, self.token, self.main_window,
                                                         self.projects_info_window_loc, article_ids,
                                                         project_id=self.project_id)
            self.article_edit_window.show()

