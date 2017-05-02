"""

"""

# PyQt Imports
from PyQt5.Qt import (QStandardItemModel, QStandardItem)

# Figshare Desktop Imports
from Figshare_desktop.custom_widgets.extended_combo import ExtendedCombo

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class CategoriesCombo(ExtendedCombo):
    """
    A QComboBox widget specifically designed to work with Figshare categories.
    """

    def __init__(self, id_dict: dict, name_dict: dict, parent=None):
        """
        Supers QComboBox, but also creates class references to the categories dictionaries.

        Args:
            id_dict: Categories dictionary with id numbers as keys.
            name_dict: Categories dictionary with names as keys.
            parent: Widget parent.
        """
        super().__init__()
        self.id_dict = id_dict
        self.name_dict = name_dict
        cat_list = sorted(list(self.name_dict.keys()))
        self.fill_combo(cat_list)

        model = QStandardItemModel()
        for i, word in enumerate(cat_list):
            item = QStandardItem(word)
            model.setItem(i, 0, item)

        self.setModel(model)
        self.setModelColumn(0)

        if parent is not None:
            self.setParent(parent)

    def fill_combo(self, fill_list: list):
        """
        Fills the combo box with categories from the fill list.

        Args:
            fill_list: list of strings to put as items in the combo box.

        Returns:

        """
        self.clear()
        self.addItem('')
        self.addItems(fill_list)

