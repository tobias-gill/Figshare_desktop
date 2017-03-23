"""

"""

import os
import math
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QToolTip, QMessageBox, QMainWindow,
                             QAction, qApp, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.projects_windows.project_info_window import ProjectInfoWindow

from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ProjectsWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initUI()

    def initUI(self):

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

        self.formatWindow()

        self.get_proj_list(self.token)

        self.create_proj_bar(0, 4)

        self.scrollBar()

        self.projects_info_open = False
        self.projects_info_id = None

    def formatWindow(self):
        """
        Formats the Projects window
        """
        geom = self.parent.geometry()
        section_geom = self.parent.section_geom

        x0 = section_geom.x() + section_geom.width()
        y0 = section_geom.y()
        w = geom.width() - x0
        h = geom.height() - y0

        self.setGeometry(x0, y0, w, h)

        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):

        if self.projects_info_open:
            self.projects_info_window.close()

    def scrollBar(self):
        self.scroll_bar = QScrollBar(Qt.Horizontal)
        self.scroll_bar.setMaximum(len(self.project_list) - 4)
        self.scroll_bar.sliderMoved.connect(self.slider_val)
        self.scroll_bar.valueChanged.connect(self.slider_val)
        self.vbox.addWidget(self.scroll_bar)

    def slider_val(self):

        while self.hbox.count():
            item = self.hbox.takeAt(0)
            item.widget().deleteLater()

        scroll_bar_pos = self.scroll_bar.value()

        self.create_proj_bar(scroll_bar_pos, scroll_bar_pos + 4)

    def create_proj_thumb(self, title, published_date, id):

        window_size = self.geometry()

        title_fnt_size = window_size.height() / 20
        date_fnt_size = window_size.height() / 30

        btn_box = QVBoxLayout()

        title_lbl = QLabel()
        title_lbl.setText("{title}".format(title=title))
        title_lbl_fnt = QFont('SansSerif', title_fnt_size)
        title_lbl_fnt.setBold(True)
        title_lbl.setFont(title_lbl_fnt)
        title_lbl.setWordWrap(True)

        date_lbl = QLabel()
        date_lbl.setText("published: {date}".format(date=published_date))
        date_lbl_fnt = QFont('SansSerif', date_fnt_size)
        date_lbl.setFont(date_lbl_fnt)
        date_lbl.setStyleSheet('color: gray')
        date_lbl.setWordWrap(True)

        btn_box.addWidget(title_lbl)
        btn_box.addWidget(date_lbl)

        btn = QPushButton(self)
        btn.setLayout(btn_box)
        btn.setCheckable(True)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setStatusTip('Open Project Info')

        btn.clicked[bool].connect(lambda: self.on_proj_btn_pressed(id))

        self.hbox.addWidget(btn)

    def create_proj_bar(self, list_start, list_finish):

        self.buttons = {}
        i = 0
        for project_pos in range(list_start, list_finish):
            title = self.project_list[project_pos]['title']
            pub_date = self.project_list[project_pos]['published_date']
            id = self.project_list[project_pos]['id']
            self.buttons[str(id)] = i
            i += 1
            self.create_proj_thumb(title, pub_date, id)

    def on_proj_btn_pressed(self, id):

        btns = [self.hbox.itemAt(i).widget() for i in range(self.hbox.count())]

        btn_n = self.buttons[str(id)]
        for btn in btns:
            if btns[btn_n] is btn:
                pass
            elif btn.isChecked():
                btn.toggle()



        if self.projects_info_id is None:
            self.projects_info_open = True
            self.projects_info_id = id
            self.projects_info_window = ProjectInfoWindow(self.app, self.token, self.geometry(), self.main_window, id)
            self.projects_info_window.show()

        elif self.projects_info_id == id:
            if self.projects_info_open:
                self.projects_info_open = False
                self.projects_info_window.close()
            else:
                self.projects_info_open = True
                self.projects_info_window = ProjectInfoWindow(self.app, self.token, self.geometry(), self.main_window,
                                                              id)
                self.projects_info_window.show()
        else:
            if self.projects_info_open:
                self.projects_info_open = True
                self.projects_info_id = id
                self.projects_info_window.close()
                self.projects_info_window = ProjectInfoWindow(self.app, self.token, self.geometry(), self.main_window,
                                                              id)
                self.projects_info_window.show()
            else:
                self.projects_info_open = True
                self.projects_info_id = id
                self.projects_info_window = ProjectInfoWindow(self.app, self.token, self.geometry(), self.main_window,
                                                              id)
                self.projects_info_window.show()

    def get_proj_list(self, token):

        projects = Projects(token)

        self.project_list = projects.get_list()
