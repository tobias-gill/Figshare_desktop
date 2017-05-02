"""

"""

# PyQt Imports
from PyQt5.QtWidgets import (QWidget, QPushButton)
from PyQt5.QtGui import (QFont, QFontMetrics)
from PyQt5.QtCore import (Qt)

# Figshare Desktop Imports
from Figshare_desktop.custom_widgets.tag_button import QTagButton

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class CategoryTagButton(QTagButton):

    def mousePressEvent(self, event):
        """
        Overides existing mousepressevent. If a right click occurs the tag is deleted
        :param event:
        :return:
        """
        if event.button() == Qt.RightButton:
            cat_id = int(self.toolTip())
            self.tag_set.remove(cat_id)
            self.deleteLater()
        elif event.button() == Qt.LeftButton:
            return QWidget.mousePressEvent(self, event)
