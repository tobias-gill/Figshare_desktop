"""

"""

import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QMessageBox, QFileDialog, QAbstractItemView,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QTreeWidgetItem,
                             QInputDialog)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, pyqtSlot, pyqtSignal, QObject)

from Figshare_desktop.formatting.formatting import (press_button)
from figshare_interface.figshare_structures.collections import Collections

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class CollectionButton(QWidget):

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
        btn.setToolTip('Select Figshare Collection for upload')
        btn.setToolTipDuration(1)
        press_button(self.app, btn)

        btn.pressed.connect(self.select_collection)

        self.coll_button = btn
        return self.coll_button

    def select_collection(self):
        """
        Called when the select project button is pressed
        :return:
        """
        collection = Collections(self.token)

        collection_list = collection.get_list()

        titles = ['']
        for collection in collection_list:
            titles.append(collection['title'])

        collection_title, chosen = QInputDialog.getItem(self, 'Choose Figshare Collection for upload',
                                                        'Choose Figshare Collection for upload', titles, 0,
                                                        editable=False)

        if chosen:
            for coll in collection_list:
                if coll['title'] == collection_title:
                    collection_id = coll['id']
            self.parent.figshare_add_window.upload_collection = collection_id
            self.coll_button.setText(collection_title)
