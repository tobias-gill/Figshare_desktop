"""

"""
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog, QMdiSubWindow,
                             QPlainTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QThread, pyqtSlot)

from Figshare_desktop.formatting.formatting import (press_button, log_edit)
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


class UploadLog(QWidget):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.initUI()

    def initUI(self):

        vbox = QVBoxLayout()

        vbox.addWidget(self.initLog())
        vbox.addWidget(self.clear_btn())

        self.setLayout(vbox)

    #####
    # Widgets
    #####

    def initLog(self):

        edit = QPlainTextEdit()
        edit.setEnabled(False)
        log_edit(self.app, edit)

        self.log = edit
        return self.log

    def clear_btn(self):
        """
        QPushButton to clear the log
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/delete.png')))
        press_button(self.app, btn)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        btn.pressed.connect(self.clear_log)

        return btn

    #####
    # Actions
    #####

    def clear_log(self):
        """
        Called to clear the log text
        :return:
        """
        self.log.clear()

    @pyqtSlot(str, int, str)
    def add_success_log(self, local_id: str, figshare_id: int, article_title: str):
        """
        Called to add a success log to the edit
        :param local_id: local article id
        :param figshare_id: new figshare article id
        :param article_title: article title
        :return:
        """
        msg = "[UPLOAD] local article {local} uploaded to Figshare article {fig} with title {title}\n"
        msg = msg.format(local=local_id, fig=figshare_id, title=article_title)

        log = self.log.toPlainText() + msg

        self.log.setPlainText(log)

    @pyqtSlot(str, str, tuple)
    def add_error_log(self, local_id, article_title, error_args):
        """
        Called to add an error log to the edit
        :param local_id: local article id
        :param article_title: article title
        :param error_args: error arguments
        :return:
        """
        msg = "[ERROR] local article {local} : {title}\n"
        msg = msg.format(local=local_id, title=article_title)

        for arg in error_args:
            msg += '\t{}\n'.format(arg)

        log = self.log.toPlainText() + msg

        self.log.setPlainText(log)
