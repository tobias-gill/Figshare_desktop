"""

"""

import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QMessageBox, QFileDialog, QAbstractItemView,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidgetItem,
                             QInputDialog)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, pyqtSlot, pyqtSignal, QObject)

from Figshare_desktop.formatting.formatting import (press_button)
from figshare_interface.figshare_structures.projects import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ProjectButton(QWidget):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initUI()

    def initUI(self):

        vbox = QVBoxLayout()

        # Add project selection button
        vbox.addWidget(self.initButton())

        self.setLayout(vbox)

    def initButton(self):

        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Folder-48.png')))
        btn.setToolTip('Select Figshare Project for upload')
        btn.setToolTipDuration(2500)
        press_button(self.app, btn)

        btn.setStyleSheet("background-color: red")

        btn.pressed.connect(self.select_project)

        self.proj_button = btn
        return self.proj_button

    def select_project(self):
        """
        Called when the select project button is pressed
        :return:
        """
        projects = Projects(self.token)

        project_list = projects.get_list()

        titles = []
        for project in project_list:
            titles.append(project['title'])

        project_title, chosen = QInputDialog.getItem(self, 'Choose Figshare Project for upload',
                                                     'Choose Figshare Project for upload', titles, 0, editable=False)

        if chosen:
            for proj in project_list:
                if proj['title'] == project_title:
                    project_id = proj['id']
            self.parent.figshare_add_window.upload_project = project_id
            self.proj_button.setStyleSheet("background-color: green")

            # Enable to start upload button
            self.parent.figshare_add_window.control_widget.enable_start()
