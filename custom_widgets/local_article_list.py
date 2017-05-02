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

from Figshare_desktop.custom_widgets.article_list import ArticleList
from Figshare_desktop.figshare_articles.determine_type import gen_article
from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class LocalArticleList(ArticleList):

    def __init__(self, app, OAuth_token, parent):
        super(QWidget, self).__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.articles_ids = set()

        self.initUI()

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

    def search_field(self):
        """
        Creates a QComboBox with the different search fields to choose from
        :return: QComboBox
        """

        combo = QComboBox()
        combo.setMaximumWidth(self.geometry().width() / 4)
        search_combo(self.app, combo)
        combo.setToolTip('Set search field parameter. Leave blank for general search.')
        combo.setToolTipDuration(1000)

        self.search_field_combo = combo

        # Initialise the combobox fields
        self.update_search_field()

        self.search_field_combo.setEnabled(False)

        return self.search_field_combo


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
        self.search_field_combo.addItem('')
        self.search_field_combo.addItems(self.parent.local_article_index.get_fields(schema='local_articles'))

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

    def update_headers(self, headers):
        """
        Called to update the column headers in the QTree
        :param headers: list of strings. in Order for the different column headers
        :return:
        """
        header_item = QTreeWidgetItem(headers)
        self.tree.setHeaderItem(header_item)
        self.tree.clear()
        self.fill_tree(headers, self.articles_ids)
        # Adjust the size of the columns to the contents
        for column in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(column)

    def fill_tree(self, headers, article_ids):
        """
        Called to fill the QTree
        :param headers:
        :return:
        """
        self.tree.clear()
        for article_id in article_ids:
            local_article = self.parent.local_articles[article_id]
            local_article.gen_qtree_item(headers, local_article.input_dicts())
            self.tree.addTopLevelItem(local_article.qtreeitem)

    def search_on_return(self):
        """
        Called when the return key is pressed within the search bar
        :return:
        """
        field = self.search_field_combo.currentText()
        query = self.search_edit.text()

        local_article_index = self.parent.local_article_index
        results = local_article_index.perform_search(schema='local_articles', field=field, query=query)

        self.result_ids = set()
        for docnum, val_dict in results.items():
            if 'id' in val_dict:
                self.result_ids.add(val_dict['id'])
        self.fill_tree(self.tree_headers, self.result_ids)
        self.parent.data_articles_window.check_edit()

    def search_on_clear(self):
        """
        Called when the clear button is pressed within the search bar
        :return:
        """
        self.fill_tree(self.tree_headers, self.articles_ids)
        self.parent.data_articles_window.check_edit()

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
        #self.tree_headers = []

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
                lbl = fields.pop(False)
                exec("chk_box_{}_{} = QCheckBox(lbl)".format(row, i))  # Create a checkbox
                if lbl in self.tree_headers:
                    eval("chk_box_{}_{}".format(row, i)).toggle()
                eval("chk_box_{}_{}".format(row, i)).stateChanged.connect(lambda state, r=row,
                                                                                 c=i: self.check_box_clicked(r, c))
                grid.addWidget(eval("chk_box_{}_{}".format(row, i)), row, i)  # add the checkbox to the grid

            row += 1  # increase the row counter

        self.dlg = dlg
        self.headers_box_layout = grid
        self.dlg.show()

    def get_selection(self):
        """
        Can be called to return a list of the article id numbers of all selected articles
        :return:
        """
        items = self.tree.selectedItems()

        article_ids = set()
        for item in items:
            article_ids.add(item.text(0))

        return article_ids

    def get_all(self):
        """
        Can be called to return the article id numbers of all articles in the tree
        :return:
        """
        self.tree.selectAll()
        items = self.tree.selectedItems()

        article_ids = set()
        for item in items:
            article_ids.add(item.text(0))

        return article_ids


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