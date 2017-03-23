"""

"""

import os
import math
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QMainWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
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


class ProjectInfoWindow(QWidget):

    def __init__(self, app, OAuth_token, projects_window_loc, main_window, project_id):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.projects_window_loc = projects_window_loc
        self.main_window = main_window
        self.project_id = project_id

        self.initFigshare()
        self.initUI()

    def initFigshare(self):

        self.get_project_info(self.token, self.project_id)

    def initUI(self):

        self.formatWindow()

        btn_show_articles = self.create_show_articles_btn()

        self.info_panel = QGridLayout()
        self.create_info_panel()

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        self.hbox.addWidget(btn_show_articles)
        self.hbox.addLayout(self.info_panel)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)

        self.editing_title = False
        self.editing_description = False

        self.articles_window_open = False
        self.aew = None
        self.article_edit_open = False


    def formatWindow(self):

        pw_x0 = self.projects_window_loc.x()
        pw_y0 = self.projects_window_loc.y()
        pw_width = self.projects_window_loc.width()
        pw_height = self.projects_window_loc.height()

        screen = self.app.primaryScreen().availableGeometry()

        x0 = pw_x0
        y0 = pw_y0 + pw_height + 10
        self.w_width = screen.width() - x0
        self.w_height = screen.height() / 4

        self.setGeometry(x0, y0, self.w_width, self.w_height)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):

        if self.articles_window_open:
            self.articles_window.close()
        if self.article_edit_open:
            self.aew.close()

    def get_project_info(self, token, project_id):

        projects = Projects(token)

        self.project_info = projects.get_info(project_id)

    def create_info_panel(self):

        # Title
        self.lbl_title = self.create_view_title()

        window_size = self.geometry()

        title_fnt_size = window_size.height() / 25

        lbl_fnt_size = window_size.height() / 30
        lbl_fnt = QFont('SansSerif', lbl_fnt_size)
        lbl_fnt.setBold(True)

        view_fnt_size = window_size.height() / 40
        view_fnt = QFont('SansSerif', view_fnt_size)

        # Project id Label
        lbl_project_id = QLabel("id")
        lbl_project_id.setFont(lbl_fnt)
        lbl_project_id.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_project_id.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Project-id view
        view_project_id = QLabel()
        view_project_id.setText("{id}".format(id=self.project_id))
        view_project_id.setFont(view_fnt)
        view_project_id.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        view_project_id.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Project ID Layout
        project_id_layout = QHBoxLayout()
        project_id_layout.addWidget(lbl_project_id)
        project_id_layout.addWidget(view_project_id)
        project_id_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Published Label
        lbl_published = QLabel("Published")
        lbl_published.setFont(lbl_fnt)
        lbl_published.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_published.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Published View
        view_published = QLabel()
        if self.project_info['published_date'] is None:
            view_published.setText("Private")
            view_published.setStyleSheet('color: gray')
        else:
            view_published.setText("{date}".format(self.project_info['published_date']))
            if self.project_info['modified_date'] != self.project_info['published_date']:
                view_published.setStyleSheet('color: red')
                view_published.setToolTip("There are unpublished changes to this project.")
        view_published.setFont(view_fnt)
        view_published.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        view_published.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Published Layout
        published_layout = QHBoxLayout()
        published_layout.addWidget(lbl_published)
        published_layout.addWidget(view_published)
        published_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Description Label
        lbl_description = QLabel("Description")
        lbl_description.setFont(lbl_fnt)
        lbl_description.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Description view
        self.view_description = self.create_view_description()

        # Collaborators Label
        lbl_collaborators = QLabel("Collaborators")
        lbl_collaborators.setFont(lbl_fnt)
        lbl_collaborators.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_collaborators.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Collaborators View
        collaborator_hbox = QHBoxLayout()
        collaborator_hbox.addWidget(lbl_collaborators)
        for collaborator in self.project_info['collaborators']:
            collaborator_lbl = QLabel("{name}".format(name=collaborator['name']))
            collaborator_lbl.setFont(view_fnt)
            collaborator_lbl.setToolTip("user_id: <b>{id}</b>".format(id=collaborator['user_id']))
            collaborator_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            collaborator_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            collaborator_hbox.addWidget(collaborator_lbl)
            collaborator_hbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Storage Label
        lbl_storage_used = QLabel("Storage")
        lbl_storage_used.setFont(lbl_fnt)
        lbl_storage_used.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_storage_used.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Storage view
        figshare_quota = self.project_info['quota']
        if figshare_quota == 0:
            figshare_quota = 1
        if self.project_info['group_id'] != 0:
            figshare_used_quota = self.project_info['used_quota_public']
        else:
            figshare_used_quota = self.project_info['used_quota_private']
        figshare_quota_percentage = round(100 * figshare_used_quota / figshare_quota, 2)

        view_storage_used = QLabel()
        view_storage_used.setText("{percentage} %".format(percentage=figshare_quota_percentage))
        view_storage_used.setFont(view_fnt)
        view_storage_used.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        view_storage_used.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Storage Type Label
        lbl_storage_type = QLabel("Storage Type")
        lbl_storage_type.setFont(lbl_fnt)
        lbl_storage_type.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        lbl_storage_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Storage Type View
        if self.project_info['group_id'] != 0:
            group_list = Groups(self.token).get_list()
            for group in group_list:
                if group['id'] == self.project_info['group_id']:
                    group_name = group['name']
                    group_id = self.project_info['group_id']
        else:
            group_name = 'Private'
            group_id = 'None'

        view_storage_type = QLabel()
        view_storage_type.setText(group_name)
        view_storage_type.setFont(view_fnt)
        view_storage_type.setToolTip("group_id: <b>{id}</b>".format(id=group_id))
        view_storage_type.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        view_storage_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Funding Label
        lbl_funding = QLabel("Funding")
        lbl_funding.setFont(lbl_fnt)
        lbl_funding.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_funding.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Funding View
        funding = self.project_info['funding']
        view_funding = QLabel()
        view_funding.setText(funding)
        view_funding.setFont(view_fnt)
        view_funding.setWordWrap(True)
        view_funding.setAlignment(Qt.AlignJustify | Qt.AlignVCenter)
        view_funding.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view_funding = view_funding

        # Edit Buttons
        edit_btn_description = QPushButton()
        edit_btn_description.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        edit_btn_description.setCheckable(True)
        edit_btn_description.clicked[bool].connect(self.on_edit_description)

        edit_btn_title = QPushButton()
        edit_btn_title.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        edit_btn_title.setCheckable(True)
        edit_btn_title.clicked[bool].connect(self.on_edit_title)

        # Add Widgets to Grid
        self.info_panel.addWidget(self.lbl_title, 0, 0)
        self.info_panel.addWidget(edit_btn_title, 0, 1)

        self.info_panel.addLayout(project_id_layout, 1, 0)

        self.info_panel.addLayout(published_layout, 2, 0)

        self.info_panel.addWidget(lbl_description, 3, 0)
        self.info_panel.addWidget(self.view_description, 4, 0)
        self.info_panel.addWidget(edit_btn_description, 3, 1)

        self.info_panel.addLayout(collaborator_hbox, 5, 0)

        self.info_panel.addWidget(lbl_storage_used, 3, 3)
        self.info_panel.addWidget(view_storage_used, 3, 4)

        self.info_panel.addWidget(lbl_storage_type, 4, 3)
        self.info_panel.addWidget(view_storage_type, 4, 4)

        self.info_panel.addWidget(lbl_funding, 5, 3)
        self.info_panel.addWidget(view_funding, 5, 4)

    def create_view_title(self):
        lbl_title = QLabel()
        lbl_title.setText("{title}".format(title=self.project_info['title']))
        lbl_title_fnt = QFont('SansSerif', 16)
        lbl_title_fnt.setBold(True)
        lbl_title.setFont(lbl_title_fnt)
        lbl_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return lbl_title

    def create_text_title(self):
        text_title = QLineEdit()
        text_title.setText("{title}".format(title=self.project_info['title']))
        text_title.setFont(QFont('SansSerif', 16))
        text_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return text_title

    def create_view_description(self):
        view_description = QLabel()
        view_description.setText("{description}".format(description=self.project_info['description']))
        view_description.setFont(QFont('SansSerif', 11))
        view_description.setWordWrap(True)
        view_description.setAlignment(Qt.AlignJustify | Qt.AlignVCenter)
        view_description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return view_description

    def create_text_decription(self):
        text_description = QTextEdit()
        text_description.setText("{description}".format(description=self.project_info['description']))
        text_description.setAcceptRichText(False)
        text_description.setAcceptDrops(True)
        text_description.setFont(QFont('SansSerif', 11))
        text_description.setAlignment(Qt.AlignJustify | Qt.AlignVCenter)
        text_description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return text_description

    def on_edit_title(self):
        if self.editing_title:
            update_data = {'title': self.text_title.text()}
            project_id = self.project_info['id']
            Projects(self.token).update(project_id, **update_data)
            self.project_info = Projects(self.token).get_info(project_id)

            self.info_panel.removeWidget(self.text_title)
            self.text_title.deleteLater()
            self.lbl_title = self.create_view_title()
            self.info_panel.addWidget(self.lbl_title, 0, 0)
            self.editing_title = False
        else:
            self.info_panel.removeWidget(self.lbl_title)
            self.lbl_title.deleteLater()
            self.text_title = self.create_text_title()
            self.info_panel.addWidget(self.text_title, 0, 0)
            self.editing_title = True

    def on_edit_description(self):
        if self.editing_description:
            update_data = {'description': self.text_description.toPlainText()}
            Projects(self.token).update(self.project_info['id'], **update_data)
            project_id = self.project_info['id']
            self.project_info = Projects(self.token).get_info(project_id)

            self.info_panel.removeWidget(self.text_description)
            self.text_description.deleteLater()
            self.view_description = self.create_view_description()
            self.info_panel.addWidget(self.view_description, 4, 0)
            self.editing_description = False
        else:
            self.info_panel.removeWidget(self.view_description)
            self.view_description.deleteLater()
            self.text_description = self.create_text_decription()
            self.info_panel.addWidget(self.text_description, 4, 0)
            self.editing_description = True

    def create_show_articles_btn(self):
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Magazine-50.png')))
        btn.setCheckable(True)
        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setHorizontalPolicy(QSizePolicy.Preferred)
        btn.setSizePolicy(sizepolicy)

        btn.clicked[bool].connect(self.on_show_articles_pressed)
        return btn

    def on_show_articles_pressed(self):

        if self.articles_window_open:
            self.articles_window_open = False
            self.articles_window.close()
        else:
            self.articles_window_open = True
            self.articles_window = ProjectsArticlesWindow(self.app, self.token, self.geometry(), self.main_window,
                                                          self.project_id)
            self.articles_window.show()
