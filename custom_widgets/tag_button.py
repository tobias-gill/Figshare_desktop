"""

"""


from PyQt5.QtWidgets import (QWidget, QPushButton)
from PyQt5.QtGui import (QFont, QFontMetrics)
from PyQt5.QtCore import (Qt)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class QTagButton(QPushButton):

    def __init__(self, label: str, tag_set: set, tooltip_lbl: str=None):
        """
        Formats the tag button
        :param label: String of tag.
        :param tag_set: set of tag strings
        """
        super().__init__()

        self.label = label
        self.tag_set = tag_set

        self.setText(str(label))
        font = QFont('SansSerif', 9)
        font.setBold(False)
        self.setFont(font)
        font_metric = QFontMetrics(font)
        width = font_metric.width(str(label)) + 20

        if tooltip_lbl is not None:
            self.setToolTip(str(tooltip_lbl))
            self.setToolTipDuration(1000)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

    def mousePressEvent(self, event):
        """
        Overides existing mousepressevent. If a right click occurs the tag is deleted
        :param event:
        :return:
        """
        if event.button() == Qt.RightButton:
            self.tag_set.remove(self.label)
            self.deleteLater()
        elif event.button() == Qt.LeftButton:
            return QWidget.mousePressEvent(self, event)
