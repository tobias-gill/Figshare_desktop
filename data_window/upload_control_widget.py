"""

"""

import os

from requests import HTTPError

from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QMessageBox, QFileDialog, QAbstractItemView,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidgetItem,
                             QInputDialog)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QThread, pyqtSlot, pyqtSignal, QObject)

from Figshare_desktop.formatting.formatting import (press_button)
from figshare_interface.figshare_structures.projects import Projects
from figshare_interface.figshare_structures.collections import Collections

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class UploadControl(QWidget):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.__threads = []

        self.initUI()

    #####
    # Widgets
    #####

    def initUI(self):

        vbox = QVBoxLayout()

        vbox.addWidget(self.start_upload_btn())
        vbox.addWidget(self.stop_upload_btn())

        self.setLayout(vbox)

    def start_upload_btn(self):
        """
        Creates a QPushButton that will start the upload process
        :return:
        """

        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/figshare_upload.png')))
        btn.setToolTip('Begin Upload')
        btn.setToolTipDuration(1)
        btn.setEnabled(False)

        btn.pressed.connect(self.start_upload)

        self.start_btn = btn

        return self.start_btn

    def stop_upload_btn(self):
        """
        Creates a QPushButton that will try to stop the upload process
        :return:
        """

        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/exit.png')))
        btn.setToolTip('Stop Upload')
        btn.setToolTipDuration(1)
        btn.setEnabled(False)

        #btn.pressed.connect(self.stop_upload)

        self.stop_btn = btn

        return self.stop_btn

    #####
    # Actions
    #####

    def enable_start(self):
        """
        Called to enable the start upload button
        :return:
        """
        self.start_btn.setEnabled(True)

    def start_upload(self):
        """
        Starts the upload of articles to the defined figshare project
        :return:
        """

        # Locally define the upload queue
        figshare_add_window = self.parent.figshare_add_window
        upload_queue = figshare_add_window.upload_queue

        # Locally define the upload log
        upload_log = figshare_add_window.upload_log

        # Setup the Upload Worker Thread
        worker = UploadWorker(self.token, self.parent)

        upload_thread = QThread()
        self.__threads.append((upload_thread, worker))

        worker.moveToThread(upload_thread)

        # Remove local articles from the queue as they are uploaded
        worker.sig_step.connect(lambda local_article_id, figshare_article_id,
                                       aritcle_title: upload_queue.fill_tree())
        # Log the upload
        worker.sig_step.connect(upload_log.add_success_log)

        # Log errors
        worker.sig_error.connect(upload_log.add_error_log)
        worker.sig_error.connect(lambda local_id, title, errs: upload_queue.fill_tree())

        upload_thread.started.connect(worker.work)
        upload_thread.start()


class UploadWorker(QObject):

    sig_step = pyqtSignal(str, int, str)
    sig_done = pyqtSignal(bool)
    sig_error = pyqtSignal(str, str, tuple)
    sig_abort = pyqtSignal(bool)

    def __init__(self, OAuth_token, parent):
        super().__init__()

        self.token = OAuth_token
        self.parent = parent

    @pyqtSlot()
    def work(self):
        """

        :return:
        """
        # Locally define some windows and widgets
        figshare_add_window = self.parent.figshare_add_window
        upload_queue = figshare_add_window.upload_queue
        self.project_id = figshare_add_window.upload_project
        self.collection_id = figshare_add_window.upload_collection

        # Get the upload project id
        if self.project_id is not None:
            projects = Projects(self.token)
        else:
            return self.sig_done.emit(True)

        if self.collection_id is not None and self.collection_id != '':
            collections = Collections(self.token)

        while upload_queue.local_ids:
            local_article_id = upload_queue.local_ids.pop()
            self.project_upload(projects, local_article_id)

    def project_upload(self, projects_instance, local_article_id: str):
        """
        Creates a new figshare article and uploads the file associated with it
        :param projects_instance: Instance of the Figshare_API_Interface Projects Class
        :param local_article_id: local id number of the article to be uploaded
        :return:
        """

        # Get the local article
        local_article = self.parent.local_articles[local_article_id]
        # Article Title
        article_title = local_article.figshare_metadata['title']
        # Generate the Figshare upload dictionary
        upload_dict = local_article.get_upload_dict()

        # Get the local file location
        local_location = local_article.figshare_desktop_metadata['location']

        # Upload file to the figshare project
        try:
            # Create a new figshare article in the given project
            figshare_article_id = projects_instance.create_article(self.project_id, upload_dict)
            # Upload files to the new article
            projects_instance.upload_file(figshare_article_id, local_location)

            # Signal that the article has been created and uploaded
            self.sig_step.emit(local_article_id, figshare_article_id, article_title)

        except FileExistsError as err:
            err_args = err.args
            self.sig_error.emit(local_article_id, article_title, err_args)
        except HTTPError as err:
            err_args = err.args
            self.sig_error.emit(local_article_id, article_title, err_args)
