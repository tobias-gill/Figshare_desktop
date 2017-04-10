"""

"""
import collections
import time
from elasticsearch import Elasticsearch

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QProgressBar, QAbstractItemView, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QHBoxLayout, QComboBox, QPushButton, QDialog, QGridLayout, QSizePolicy,
                             QCheckBox)
from PyQt5.QtCore import (QThread, pyqtSignal, pyqtSlot, QObject)

from Figshare_desktop.formatting.formatting import (search_bar, search_combo, press_button)

from Figshare_desktop.figshare_articles.determine_type import gen_article
from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class LocalArticleList(QWidget):

    def __init__(self, app, OAuth_token, parent):
        super(QWidget, self).__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.__threads = []

        self.articles_ids = set()

        self.initUI()

    def initUI(self):

        # Initialise the article tree
        self.initTree()

        # Create a horizontal layout for the search bar and fields
        search_layout = QHBoxLayout()

        # Add field search to search layout
        search_layout.addWidget(self.search_field())
        # Add search bar to search layout
        search_layout.addWidget(self.search_bar())
        # Add headers selection button to search layout
        search_layout.addWidget(self.headers_selection_btn())

        # Create a vertical layout
        vbox = QVBoxLayout()

        # Add the search layout to the vertical layout
        vbox.addLayout(search_layout)
        # Add the article tree to the vertical layout
        vbox.addWidget(self.tree)

        self.setLayout(vbox)

    #####
    # Window Widgets
    #####

    def initTree(self):
        """
        Called to initalise the QTreeWidget
        :return:
        """

        tree = QTreeWidget()
        # Format tree to allow for multiple items to be selected
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Allow for sorting of columns
        tree.setSortingEnabled(True)

        # Create the initial set of column headers
        headers = ['id', 'title', 'type', 'tags']
        header_item = QTreeWidgetItem(headers)
        tree.setHeaderItem(header_item)

        self.tree = tree
        self.tree_headers = headers

    def search_bar(self):
        """
        Creates a QLineEdit object for user to enter search query
        :return:
        """
        # Create text box
        edit = QLineEdit()
        # Set font style
        search_bar(self.app, edit)
        # Set place holder text
        edit.setPlaceholderText('Search')
        # Add a clear button to the line edit
        edit.setClearButtonEnabled(True)
        # Add mouse over text
        edit.setToolTip('Search for specific Figshare Projects')
        edit.setToolTipDuration(1)
        # Connect search function to the return key
        edit.returnPressed.connect(self.search_on_return)
        # Connect the clear button to our own function
        edit.children()[2].triggered.connect(self.search_on_clear)

        edit.setEnabled(False)

        self.search_edit = edit
        return self.search_edit

    def search_field(self):
        """
        Creates a QComboBox with the different search fields to choose from
        :return: QComboBox
        """

        combo = QComboBox()
        combo.setMaximumWidth(self.geometry().width() / 4)
        search_combo(self.app, combo)
        combo.setToolTip('Set search field parameter. Leave blank for general search.')
        combo.setToolTipDuration(1)

        self.search_field_combo = combo

        # Initialise the combobox fields
        self.update_search_field()

        self.search_field_combo.setEnabled(False)

        return self.search_field_combo

    def headers_selection_btn(self):
        """
        Button pressed to open headers selection window
        :return: QPushButton
        """
        btn = QPushButton('Select Headers')
        press_button(self.app, btn)
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        btn.clicked[bool].connect(self.on_headers_set_pressed)
        btn.setEnabled(False)
        self.headers_btn = btn
        return self.headers_btn

    #####
    # Widget Actions
    #####

    @pyqtSlot(bool)
    def update_search_field(self):
        """
        Updates the items in the search field combobox
        :return:
        """
        self.search_field_combo.clear()
        self.search_field_combo.addItems(self.parent.local_article_index.get_fields(schema='local_articles'))

    def disable_fields(self):
        """
        Disables all fields
        :return:
        """
        self.search_edit.setEnabled(False)
        self.search_field_combo.setEnabled(False)
        self.headers_btn.setEnabled(False)

    @pyqtSlot(bool)
    def enable_fields(self):
        """
        Enables all fields
        :return:
        """
        self.search_edit.setEnabled(True)
        self.search_field_combo.setEnabled(True)
        self.headers_btn.setEnabled(True)

    @pyqtSlot(str)
    def add_to_tree(self, local_article_id: str):
        """
        Attempts to parse and
        :param local_article_id:
        :return:
        """
        if local_article_id not in self.articles_ids:
            self.articles_ids.add(local_article_id)
            local_article = self.parent.local_articles[local_article_id]
            local_article.gen_qtree_item(self.tree_headers, local_article.input_dicts())
            self.tree.addTopLevelItem(local_article.qtreeitem)

            for column in range(self.tree.columnCount()):
                self.tree.resizeColumnToContents(column)

    def fill_tree(self, headers):
        """
        Called to fill the QTree
        :param headers:
        :return:
        """
        for article_id in self.articles_ids:
            local_article = self.parent.local_articles[article_id]
            local_article.gen_qtree_item(headers, local_article.input_dicts())
            self.tree.addTopLevelItem(local_article.qtreeitem)


    def search_on_return(self):
        """
        Called when the return key is pressed within the search bar
        :return:
        """
        pass

    def search_on_clear(self):
        """
        Called when the clear button is pressed within the search bar
        :return:
        """
        pass

    def update_headers(self, headers):
        """
        Called to update the column headers in the QTree
        :param headers: list of strings. in Order for the different column headers
        :return:
        """
        header_item = QTreeWidgetItem(headers)
        self.tree.setHeaderItem(header_item)
        self.tree.clear()
        self.fill_tree(headers)
        # Adjust the size of the columns to the contents
        for column in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(column)

    def on_headers_set_pressed(self):
        """
        Called when the set headers button is pressed
        :return:
        """
        # Create a dialog window
        dlg = QDialog()

        # Create a vertical layout to hold header selections and confirmation buttons
        vbox = QVBoxLayout()

        # Create a grid layout to hold the QCheckboxes
        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(15)

        # Add the grid to the layout
        vbox.addLayout(grid)

        # Create a confirmation button
        btn = QPushButton('OK')
        btn.pressed.connect(self.on_headers_ok_pressed)

        # Add Button to layout
        vbox.addWidget(btn)

        # Set the dialog window layout
        dlg.setLayout(vbox)

        # Create an ordered set of field names
        fields = self.parent.local_article_index.get_fields('local_articles')

        # Define how many columns of check boxes to create
        columns = 3

        # Empty the tree headers list
        self.tree_headers = []

        # Start at row zero
        row = 0
        # While we still have a field in the ordered set
        while fields:
            for i in range(columns):
                # Here we have to use the exec function to programatically name each box variable otherwise the connect
                # function only ever calls the last button.
                # Further complication from having to remember that the stateChanged signal passes a bool int to the
                # lambda function.
                if len(fields) == 0:
                    break
                exec("chk_box_{}_{} = QCheckBox(fields.pop(False))".format(row, i))  # Create a checkbox
                eval("chk_box_{}_{}".format(row, i)).stateChanged.connect(lambda state, r=row,
                                                                                 c=i: self.check_box_clicked(r, c))
                grid.addWidget(eval("chk_box_{}_{}".format(row, i)), row, i)  # add the checkbox to the grid
            row += 1  # increase the row counter

        self.dlg = dlg
        self.headers_box_layout = grid
        self.dlg.show()

    def check_box_clicked(self, row, column):
        """
        Called when a check box in the header selection dialog is clicked
        :return:
        """
        if self.headers_box_layout.itemAtPosition(row, column) is not None:
            field = self.headers_box_layout.itemAtPosition(row, column).widget().text()
            if field in self.tree_headers:
                self.tree_headers.remove(field)
            elif field not in self.tree_headers:
                self.tree_headers.append(field)

    def on_headers_ok_pressed(self):
        """
        Called when the headers dialog window ok button is pressed
        :return:
        """
        self.dlg.close()

        # Ensure that id number is always the first column.
        if self.tree_headers[0] != 'id':
            self.tree_headers.insert(0, 'id')

        self.update_headers(self.tree_headers)


class OrderedSet(collections.OrderedDict, collections.MutableSet):

    def update(self, *args, **kwargs):
        if kwargs:
            raise TypeError("update() takes no keyword arguments")

        for s in args:
            for e in s:
                 self.add(e)

    def add(self, elem):
        self[elem] = None

    def discard(self, elem):
        self.pop(elem, None)

    def __le__(self, other):
        return all(e in other for e in self)

    def __lt__(self, other):
        return self <= other and self != other

    def __ge__(self, other):
        return all(e in self for e in other)

    def __gt__(self, other):
        return self >= other and self != other

    def __repr__(self):
        return 'OrderedSet([%s])' % (', '.join(map(repr, self.keys())))

    def __str__(self):
        return '{%s}' % (', '.join(map(repr, self.keys())))

    difference = property(lambda self: self.__sub__)
    difference_update = property(lambda self: self.__isub__)
    intersection = property(lambda self: self.__and__)
    intersection_update = property(lambda self: self.__iand__)
    issubset = property(lambda self: self.__le__)
    issuperset = property(lambda self: self.__ge__)
    symmetric_difference = property(lambda self: self.__xor__)
    symmetric_difference_update = property(lambda self: self.__ixor__)
    union = property(lambda self: self.__or__)