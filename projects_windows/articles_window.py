"""

"""

import os
import math
from requests import HTTPError

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.custom_widgets.article_list import ArticleList

from Figshare_desktop.formatting.formatting import (grid_label, grid_edit, press_button)

from Figshare_desktop.article_edit_window.article_edit_window import ArticleEditWindow

from figshare_interface import (Groups, Projects)
from figshare_interface.http_requests.figshare_requests import (download_file)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"

class ProjectsArticlesWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent, project_id):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.project_id = project_id

        self.open_windows = self.parent.open_windows

        self.initFig(self.project_id)
        self.initUI()

    def initFig(self, project_id):
        """
        Initilizes Figshare information for the given project
        :param project_id: int. Figshare project id number
        :return:
        """
        projects = Projects(self.token)
        self.project_info = projects.get_info(project_id)
        self.article_list = projects.list_articles(project_id)

    def initUI(self):
        """
        Initilizes the GUI
        :return:
        """

        # Encompassing horizontal layout
        horizontal_layout = QHBoxLayout()

        # Create left vertical layout
        left_vertical_layout = QVBoxLayout()

        # Create a central vertical layout
        central_vertical_layout = QVBoxLayout()
        # Add search bar to central layout
        # central_vertical_layout.addLayout()
        # Add article tree to central layout
        self.article_list_widget = ArticleList(self.app, self.token, self.project_id, self.parent)
        central_vertical_layout.addWidget(self.article_list_widget)

        # Create right vertical layout
        right_vertical_layout = QVBoxLayout()
        # Add Figsahre command buttons to the right layout
        right_vertical_layout.addWidget(self.publish_article_button())
        right_vertical_layout.addWidget(self.edit_article_button())
        right_vertical_layout.addWidget(self.download_article_button())

        # Add left, central, and right layouts to the horizontal layout
        horizontal_layout.addLayout(left_vertical_layout)
        horizontal_layout.addLayout(central_vertical_layout)
        horizontal_layout.addLayout(right_vertical_layout)

        self.format_window()

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(horizontal_layout)
        # Set the projects window widget
        self.setWidget(window_widget)

    #####
    # Window Formatting
    #####

    def format_window(self):
        """
        Sets the window geometry
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
        # Remove frame from the window
        self.setWindowFlags(Qt.FramelessWindowHint)

    #####
    # Window Widgets
    #####

    def edit_article_button(self):
        """
        Creates a QPush button that opens the article edit window
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Pencil-52.png')))
        press_button(self.app, btn)
        btn.setToolTip('Open article edit window')
        btn.setToolTipDuration(1)
        btn.pressed.connect(self.on_edit_article_pressed)
        return btn

    def publish_article_button(self):
        """
        Creates a QPushButton that will publish the selected articles
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/figshare_upload.png')))
        press_button(self.app, btn)
        btn.setToolTip('Publish selected articles')
        btn.setToolTipDuration(1)
        btn.pressed.connect(self.on_publish_article_pressed)
        return btn

    def download_article_button(self):
        """
        Creates a QPushButton that will download the selected articles
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/figshare_download.png')))
        press_button(self.app, btn)
        btn.setToolTip('Download selected articles')
        btn.setToolTipDuration(1)
        btn.pressed.connect(self.on_download_article_pressed)
        return btn

    #####
    # Widgets Actions
    #####

    def on_edit_article_pressed(self):
        """
        Called when the edit article button is pressed. Opens the edit window
        :return:
        """

        # Get the list of article id numbers from the selected items in the article list widget
        article_ids = list(self.article_list_widget.get_selection())

        self.parent.open_windows.remove('project_articles_window')
        self.parent.project_articles_window.close()

        self.parent.open_windows.add('article_edit_window')
        self.parent.article_edit_window = ArticleEditWindow(self.app, self.token, self.parent, self.project_id,
                                                            article_ids)
        self.parent.mdi.addSubWindow(self.parent.article_edit_window)
        self.parent.article_edit_window.show()

    def on_publish_article_pressed(self):
        """
        Called when the publish article button is pressed. Asks for confirmation.
        :return:
        """
        pass

    def on_download_article_pressed(self):
        """
        Called when the download article button is pressed.
        :return:
        """
        # Get the list of article id numbers from the selected items in the article list widget
        article_ids = self.article_list_widget.get_selection()

        # Ask if all articles are desired if there is no selection
        if article_ids == []:
            reply = QMessageBox.question(self, "Download Confirmation", "Download All Articles?", QMessageBox.Yes,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                article_ids = self.article_list_widget.get_all()
            else:
                article_ids = None

        # If there are articles to download
        if article_ids is not None:

            # Get a list of files from all articles
            # keep the file names and the file download urls
            downloads = []
            for article in article_ids:
                file_list = Projects(self.token).list_files(article)
                for f in file_list:
                    if f['name'][-4:] != '.png':
                        downloads.append([f['name'], f['download_url']])

            # Ask the user to choose a download directory
            download_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

            # An empty list to record any download errors
            download_statuses = []

            # Download all files in the list
            for f in downloads:
                local_path = os.path.abspath(download_dir + '/' + f[0])
                url = f[1]
                status = download_file(url, local_path, self.token)

                # If there is an error in any of the downloads record the file name
                if status != 200:
                    download_statuses.append(f[0])

            # If there are any errors display a message that lists the affected files
            if download_statuses != []:

                msg = 'There was an error in downloading the following files.\n'
                for f in download_statuses:
                    msg += f + '\n'

                reply = QMessageBox.warning(self, "Download Error", msg, QMessageBox.Ok)

                if reply == QMessageBox.Ok:
                    pass
                else:
                    pass

            # Otherwise confirm that the downloads have been successful
            else:
                reply = QMessageBox.information(self, 'Download Confirmation', "All files downloaded", QMessageBox.Ok)

                if reply == QMessageBox.Ok:
                    pass
                else:
                    pass
