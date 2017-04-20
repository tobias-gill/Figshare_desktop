"""Project Articles Window

This window is used to display the existing articles in a Figshare project and allow for the user to manage article
publishing, metadata editing, and allows for the article files to be downloaded locally. To aid with article
classification searching is possible by making use of the Figshare Elastic search API calls. All metadata fields can be
searched explicitly or all field general searches can be performed.

Todo:
    * Add a button to allow for articles to be deleted.

"""

import os
import math
from requests import HTTPError

from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QMainWindow, QMessageBox, QFileDialog, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt)

from Figshare_desktop.custom_widgets.article_list import ArticleList

from Figshare_desktop.formatting.formatting import (grid_label, grid_edit, press_button)

from Figshare_desktop.article_edit_window.article_edit_window import ArticleEditWindow

from Figshare_desktop.figshare_articles.determine_type import gen_article

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
    """
    SubWindow of the Projects Section
    =================================

    This window is used to display a list of articles within a given project and allow for the searching,publishing,
    editing, deleting, and downloading of their files.

    Searching is performed using the Fighshare elastic search engine.

    Editing of article metadata is performed in a separate window that replaces this one.
    """

    def __init__(self, app: QApplication, OAuth_token: str, parent: QMainWindow, project_id: int):
        """
        Initialise the various components needed to form the articles window.

        Args:
            app: QApplication object of the current program. Is passed from window to window upon opening.
            OAuth_token: Authentication token created at login to allow for interaction with the Figshare API.
            parent: Reference to the programs parent window (framming window) where various global variables are kept.
            project_id: Integer object, containing the Figshare project ID number for the currently open project.

        Returns:
            None
        """
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.project_id = project_id

        self.initFig(self.project_id)
        self.initUI()

    def initFig(self, project_id: int):
        """
        Initilizes Figshare information for the given project by retrieving the list of articles in the project.

        Args:
            project_id: Figshare project ID number.

        Returns:
            None
        """
        projects = Projects(self.token)
        self.project_info = projects.get_info(project_id)
        self.article_list = projects.list_articles(project_id)

    def initUI(self):
        """
        Initilizes the window GUI.

        Returns:
            None
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
        right_vertical_layout.addWidget(self.download_article_button())
        right_vertical_layout.addWidget(self.edit_article_button())
        right_vertical_layout.addWidget(self.delete_article_button())

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

    # Window Formatting
    # =================

    def format_window(self):
        """
        Sets the window geometry

        Returns:
            None
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

    # Window Widgets
    # ==============

    def edit_article_button(self):
        """
        Create a QPushButton that is used to open the article edit window for the selected articles.

        Returns:
            QPushButton Widget connected to the on_edit_article_pressed function
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/Pencil-52.png')))
        press_button(self.app, btn)
        btn.setToolTip('Open article edit window')
        btn.setToolTipDuration(1000)
        btn.pressed.connect(self.on_edit_article_pressed)
        return btn

    def delete_article_button(self):
        """
        Creates a QPushButton that can be used to deleted selected articles.

        Returns:
            QPushButton Widget connected to the on_delete_article_pressed function
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/delete.png')))
        press_button(self.app, btn)
        btn.setToolTip('Delete selected articles')
        btn.setToolTipDuration(1000)
        btn.pressed.connect(self.on_delete_article_pressed)
        return btn

    def publish_article_button(self):
        """
        Creates a QPushButton that will publish the selected articles.

        Returns:
            QPushButton: Connected to the on_publish_article_pressed function.
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/figshare_upload.png')))
        press_button(self.app, btn)
        btn.setToolTip('Publish selected articles')
        btn.setToolTipDuration(1000)
        btn.pressed.connect(self.on_publish_article_pressed)
        return btn

    def download_article_button(self):
        """
        Creates a QPushButton that will download the selected articles.

        Returns:
            QPushButton: Connected to the on_download_article_pressed function.
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/figshare_download.png')))
        press_button(self.app, btn)
        btn.setToolTip('Download selected articles')
        btn.setToolTipDuration(1000)
        btn.pressed.connect(self.on_download_article_pressed)
        return btn

    # Widgets Actions
    # ===============

    def on_edit_article_pressed(self):
        """
        Called when the edit article button is pressed. Closes the current window and opens the article edit window in
        its place.

        Returns:
            None
        """

        # Get the list of article id numbers from the selected items in the article list widget
        article_ids = list(self.article_list_widget.get_selection())

        # Close the current project ariticles window and remove from the set of open windows
        self.parent.open_windows.remove('project_articles_window')
        self.parent.project_articles_window.close()

        # Create and open the article edit window, adding it to the list of open windows
        self.parent.open_windows.add('article_edit_window')
        self.parent.article_edit_window = ArticleEditWindow(self.app, self.token, self.parent, self.project_id,
                                                            article_ids)
        self.parent.mdi.addSubWindow(self.parent.article_edit_window)
        self.parent.article_edit_window.show()

    def on_delete_article_pressed(self):
        """
        Called when the delete articles button is pressed. Will ask for user confirmation, prior to deleting articles.

        Returns:
            None
        """
        # Get a set of the articles currently selected
        article_ids = self.article_list_widget.get_selection()

        # If there is no selection then do nothing
        if article_ids == set():
            return
        # If there is a selection create a dialog window to ask for deletion confirmation
        else:
            n_articles = len(article_ids)
            msg = "Are you sure you want to permanently DELETE {} articles?".format(n_articles)
            reply = QMessageBox.question(self, "Deletion Confirmation", msg, QMessageBox.Yes, QMessageBox.No)

            # Upon a reply of Yes call the delete articles function
            if reply == QMessageBox.Yes:
                all_errors = self.delete_multiple_articles(self.project_id, article_ids)

                # If any errors occured create a new dialog to notify the user
                if all_errors != []:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setWindowIcon(QIcon(os.path.normpath(__file__ + '/../../img/figshare_logo.png')))
                    msg_box.setWindowTitle("Article Delete Errors")
                    msg_box.setText("Error occurred while trying to delete articles.")
                    detailed_msg = ""
                    for err in all_errors:
                        detailed_msg += err + '\n'
                    msg_box.setDetailedText(detailed_msg)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    self.delete_msg_box = msg_box
                    self.delete_msg_box.show()

                    self.delete_msg_box.buttonClicked.connect(self.reopen_window)

                # If no errors occured then create a new dialog to notify the user
                else:
                    msg = "All articles deleted"
                    reply = QMessageBox.information(self, "Articles Deleted", msg, QMessageBox.Ok)
                    if reply == QMessageBox.Ok:
                        self.reopen_window()
                    else:
                        self.reopen_window()

    def on_publish_article_pressed(self):
        """
        Called when the publish article button is pressed. Will ask user confirmation for if they want to make all
        selected articles publicly available.

        Returns:
            None
        """
        # Get a set of the articles currently selected
        article_ids = self.article_list_widget.get_selection()

        # If there is no selection made then select all the articles in the project
        if article_ids == set():
            article_ids = self.article_list_widget.get_all()
            n_article = 'All' # Define the number of articles as All
        else:
            n_article = len(article_ids)  # Define the number of articles to be published

        # Ask user for publish confirmation
        msg = "Are you sure you want to make {} articles public?".format(n_article)
        reply = QMessageBox.question(self, "Publish Confirmation", msg, QMessageBox.Yes, QMessageBox.No)

        # If the reply confirmation is Yes then publish the selection
        if reply == QMessageBox.Yes:
            # Passes the set of article id numbers to the publish
            errors = self.publish_articles(article_ids)

            if errors is not None:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText("Error occurred when publishing.")
                detailed_msg = ""
                for err in errors:
                    for arg in err.args:
                        detailed_msg += arg + '\n'
                        detailed_msg += str(err.response.content)
                    detailed_msg += '\n'
                msg_box.setDetailedText(detailed_msg)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self.publish_msg_box = msg_box
                self.publish_msg_box.show()

                self.publish_msg_box.buttonClicked.connect(self.reopen_window)

            else:
                msg = "All articles published"
                reply = QMessageBox.information(self, "Articles Published", msg, QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    self.reopen_window()
                else:
                    self.reopen_window()

        else:
            pass

    def reopen_window(self):
        """
        Closes and reopens the article window
        :return:
        """
        for i in range(2):
            self.parent.project_info_window.on_articles_pressed()

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
    def publish_articles(self, article_ids):
        """
        Publishes all articles given
        :param article_ids: list of int. Figshare article id numbers.
        :return:
        """
        errors = []
        for article in article_ids:
            error = self.publish_article(article)
            if error is not None:
                errors.append(error)

        if errors != []:
            return errors
        else:
            return None

    def publish_article(self, article_id):
        """
        Publishes a single article
        :param article_id: int. Figshare article id number
        :return:
        """
        try:
            Projects.publish_article(self.token, article_id)
            self.create_local_article(article_id)
            return None
        except HTTPError as err:
            return err

    def create_local_article(self, article_id):
        """
        Given a Figshare article id number this function will create a local version if one does not already exist
        :param figshare_article: Dict. Figshare article returned from Projects.list_articles()
        :return:
        """
        # Get the article id number and title
        article_id = str(article_id)  # Convert int to str
        article_title = self.parent.figshare_articles[article_id].figshare_metadata['title']

        article = gen_article(article_title, self.token, self.project_id, article_id)
        self.parent.figshare_articles[article_id] = article

    def delete_multiple_articles(self, project_id: int, article_ids: set):
        """
        Used to delete multiple articles from a given Figshare project.

        Args:
            project_id: Figshare project ID number article is within.
            article_ids: Figshare article ID number.

        Returns:
            error_msgs (list of str): List of error messages returned during deletion process.
        """
        # Empty list to hold error messages if returned
        error_msgs = []

        # Go though set and attempt to delete each article
        while article_ids:
            article_id = article_ids.pop()
            err_msg = self.delete_article(project_id, article_id)
            if err_msg != '':
                error_msgs.append(str(article_id) + ': ' + err_msg)

        return error_msgs

    def delete_article(self, project_id: int, article_id: int):
        """
        Uses the Figshare API Interface package to delete the given article from Figshare.

        Args:
            project_id: Figshare project ID number, article is within.
            article_id: Figshare article ID number.

        Returns:
            err_msg (str): Either an empty string or contains an error message that occurred during deletion process.
        """
        projects = Projects(self.token)
        err_msg = projects.article_delete(project_id, article_id)
        return err_msg
