"""

"""

from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QScrollArea, QSizePolicy)
from PyQt5.QtGui import (QFont, QColor, QPainter)
from PyQt5.QtCore import (Qt, QRect)

from Figshare_desktop.custom_widgets.tag_button import QTagButton

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class QButtonField(QWidget):
    """
    A custom class that creates an empty QLineEdit looking text field where upon return being pressed the current
    text is saved as a button/tag.
    """

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # Create layout to hold the tags
        self.tag_box = QHBoxLayout()
        self.tag_box.setAlignment(Qt.AlignLeft)

        # Create a Widget to hold the tag box
        self.tag_widget = QWidget()
        self.tag_widget.setLayout(self.tag_box)

        # Create Scroll area to put the tag box widget
        self.tag_scroll = QScrollArea()
        self.tag_scroll.setWidget(self.tag_widget)
        self.tag_scroll.setWidgetResizable(True)
        self.tag_scroll.setMinimumWidth(self.geometry().width() * (2 / 3))
        self.tag_scroll.setMaximumWidth(self.geometry().width() * (2 / 3))
        self.tag_scroll.setToolTip('Right click to remove')

        # Create layout to hold tag layout and line edit
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.tag_scroll)
        self.hbox.addWidget(self.create_linedit())

        # Create a set to hold all the existing tags
        self.tags = set()

        self.setLayout(self.hbox)

    def paintEvent(self, e):
        """
        Draws the widget
        :param e:
        :return:
        """
        paint_event = QPainter()
        paint_event.begin(self)
        self.drawWidget(paint_event)
        paint_event.end()

    def drawWidget(self, paint_event):
        """
        Constructs the individual components together
        :param paint_event: QPainter
        :return:
        """
        self.create_frame(paint_event)

    def create_frame(self, paint_event):
        """
        Creates and formats the encompassing frame
        :return:
        """

        offset = 0

        parent = self.parent()
        geom = parent.geometry()
        frame_w = geom.width() - offset
        frame_h = geom.height() - offset
        self.frame_geom = QRect(offset, offset, frame_w, frame_h)

        paint_event.setPen(QColor(255, 255, 255))
        paint_event.setBrush(QColor(255, 255, 255))
        paint_event.drawRect(offset, offset, frame_w, frame_h)

    def add_tag(self, label):
        """
        Adds a tag button to the frame
        :param label: String.
        :return:
        """

        btn = QTagButton(label, self.tags)
        self.tags.add(label)
        self.tag_box.addWidget(btn)

    def create_linedit(self):
        """
        Creates a formated line edit to create new tags with.
        :return:
        """
        edit = QLineEdit()
        edit.setPlaceholderText('Enter new tag here')
        edit.setToolTip('Press return to add tag')

        font = QFont('SansSerif', 11)
        edit.setFont(font)

        edit.returnPressed.connect(lambda: self.on_return_pressed(edit))

        return edit

    def on_return_pressed(self, edit):
        """
        Called when a new tag is to be created
        :param edit: QLineEdit from where to take text
        :return:
        """
        text = edit.text()

        if text != '' and text not in self.tags:
            self.add_tag(text)
            edit.clear()
        elif text in self.tags:
            edit.clear()

    def get_tags(self):
        """
        Returns the set of tags as a list object
        :return: list. Of tag strings
        """
        return list(self.tags)