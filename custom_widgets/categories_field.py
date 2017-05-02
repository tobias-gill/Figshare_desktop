"""

"""

# PyQt Imports
from PyQt5.QtWidgets import (QWidget)
from PyQt5.QtGui import (QFont)

# Figshare Desktop Imports
from Figshare_desktop.custom_widgets.button_field import QButtonField
from Figshare_desktop.custom_widgets.cat_tag_button import CategoryTagButton
from Figshare_desktop.custom_widgets.categories_combo import CategoriesCombo

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class CategoriesField(QButtonField):
    """
    Subclass of the QButton field widget that is customised visualise and return Figshare author metadata.
    """

    def __init__(self, id_dict: dict, name_dict: dict, parent=None):
        super(QWidget, self).__init__()
        if parent is not None:
            self.setParent(parent)
        self.id_dict = id_dict
        self.name_dict = name_dict
        self.initUI()

    def create_linedit(self):
        """
        Creates a formated line edit to create new tags with.
        :return:
        """
        edit = CategoriesCombo(self.id_dict, self.name_dict)
        edit.setToolTip('Press return to add category')

        font = QFont('SansSerif', 11)
        edit.setFont(font)

        edit.lineEdit().returnPressed.connect(lambda: self.on_return_pressed(edit))
        edit.setMaximumWidth(self.width * (1 / 4))
        return edit

    def add_tag(self, cat_lbl):
        """
        Adds an author tag button to the frame.

        Args:
            cat_lbl: category label.

        Returns:

        """
        add_tag = False

        if type(cat_lbl) is dict:
            cat_id = cat_lbl['id']
            lbl = cat_lbl['title']
            add_tag = True
        else:
            try:
                cat_id = int(cat_lbl)
                lbl = self.id_dict[cat_id]
                add_tag = True
            except:
                if cat_lbl in self.name_dict:
                    cat_id = self.name_dict[cat_lbl]
                    lbl = cat_lbl
                    add_tag = True
        if add_tag:
            if cat_id not in self.tags:
                btn = CategoryTagButton(lbl, self.tags, tooltip_lbl=str(cat_id))
                self.tags.add(cat_id)
                self.tag_box.addWidget(btn)

    def on_return_pressed(self, edit):
        """
        Called when a new tag is to be created
        :param edit: QLineEdit from where to take text
        :return:
        """
        text = edit.currentText()
        edit.lineEdit().setText('')

        if text != '' and text not in self.tags:
            self.add_tag(text)
