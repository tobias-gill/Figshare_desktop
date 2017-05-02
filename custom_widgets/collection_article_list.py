"""

"""
import collections
import time

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QProgressBar, QAbstractItemView, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QHBoxLayout, QComboBox, QPushButton, QDialog, QGridLayout, QSizePolicy,
                             QCheckBox)
from PyQt5.QtCore import (QThread, pyqtSignal, pyqtSlot, QObject)

from Figshare_desktop.formatting.formatting import (search_bar, search_combo, press_button)

from Figshare_desktop.figshare_articles.determine_type import gen_article
from figshare_interface import Collections

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ArticleList(QWidget):

    def __init__(self, app, OAuth_token, collection_id, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.collection_id = collection_id
        self.parent = parent

        self.__threads = []

        self.initFig()
        self.initUI()

    def initFig(self, show_progress=True):
        """
        Initial data load from Figshare
        :return:
        """
        # Get the list of articles from
        collections = Collections(self.token)
        articles = collections.get_articles(self.collection_id)
        n_articles = len(articles)

        worker = ArticleLoadWorker(self.app, self.token, self.parent, self.collection_id, articles)

        thread = QThread()
        thread.setObjectName('thread_article_load')

        self.__threads.append((thread, worker))
        worker.moveToThread(thread)

        worker.sig_step.connect(self.add_to_tree)
        worker.sig_done.connect(self.update_search_field)
        worker.sig_done.connect(self.enable_fields)

        thread.started.connect(worker.work)
        thread.start()

        self.articles = articles
        self.article_ids = set()
        for article in articles:
            self.article_ids.add(article['id'])

    def initUI(self):

        # Initialise the article QTree
        self.initTree()

        # Create horizontal layout for the search bar and fields
        search_layout = QHBoxLayout()

        # Add field search to search layout
        search_layout.addWidget(self.search_field())
        # Add search bar to search layout
        search_layout.addWidget(self.search_bar())
        # Add headers selection button to search layout
        search_layout.addWidget(self.headers_selection_button())

        # Create a Vertical layout
        vbox = QVBoxLayout()

        # Add the search layout to the vertical layout
        vbox.addLayout(search_layout)
        # Add the Article tree to the layout
        vbox.addWidget(self.tree)

        # Set Widget layout
        self.setLayout(vbox)

    #####
    # Window Widgets
    #####

    def initTree(self):
        """
        Called to initilize the QTree widget
        :return:
        """

        # Create instance of QTreeWidget
        tree = QTreeWidget()
        # Format tree to allow for multiple items to be selected
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Allow for sorting by clicking on headers
        tree.setSortingEnabled(True)

        # Create the initial set of column headers
        headers = ['id', 'title', 'created_date', 'up_to_date', 'type', 'tags']
        header_item = QTreeWidgetItem(headers)
        tree.setHeaderItem(header_item)

        self.tree = tree

        self.tree_headers = headers

    def search_bar(self):
        """
        Creates a QLineEdit object for the user to enter a search query
        :return: QLineEdit
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
        edit.setToolTipDuration(2000)
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
        combo.setToolTipDuration(2000)

        self.search_field_combo = combo
        self.update_search_field()
        self.search_field_combo.setEnabled(False)

        return self.search_field_combo

    def headers_selection_button(self):
        """
        Button pressed to open the headers selectionw window
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
    # Widgets Actions
    #####

    @pyqtSlot(bool)
    def update_search_field(self):
        """
        Updates the items in the search field combobox.

        Returns:
            None
        """
        # Clear combo and add empty first item
        self.search_field_combo.clear()
        self.search_field_combo.addItem('')

        # Get list of fields in Figshare article search index
        fields = self.parent.figshare_article_index.get_fields(schema='figshare_articles')
        self.search_field_combo.addItems(fields)

    @pyqtSlot(bool)
    def enable_fields(self):
        """
        Enables all fields
        :return:
        """
        self.search_edit.setEnabled(True)
        self.search_field_combo.setEnabled(True)
        self.headers_btn.setEnabled(True)

    def disable_fields(self):
        """
        Disables all fields.

        Returns:
            None
        """
        self.search_edit.setEnabled(False)
        self.search_field_combo.setEnabled(False)
        self.headers_btn.setEnabled(False)

    def fill_tree(self, headers: list, article_ids: set):
        """
        Called to fill the QTree with articles

        Args:
            headers: Metadata key names in order to which appear in the QTreeWidget.
            article_ids: Set of Figshare article ID numbers from to fill tree with.

        Returns:
            None
        """
        self.tree.clear()
        for article_id in article_ids:
            self.add_to_tree(article_id, headers=headers)

    @pyqtSlot(int)
    def add_to_tree(self, article_id: int, headers: list=None):
        """
        Adds a single article to the QTree
        :param article_id: int. or str. figshare article id
        :return:
        """
        if headers is None:
            headers = self.tree_headers

        article_id = str(article_id)

        local_article = self.parent.figshare_articles[article_id]
        local_article.gen_qtree_item(headers, local_article.input_dicts())
        self.tree.addTopLevelItem(local_article.qtreeitem)

        # Adjust the size of the columns to the contents
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
        self.fill_tree(headers, self.article_ids)
        # Adjust the size of the columns to the contents
        for column in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(column)

    def search_on_return(self):
        """
        Called when return is pressed in the search bar.
        :return:
        """
        field = self.search_field_combo.currentText()
        query = self.search_edit.text()

        if query == '':
            self.search_on_clear()
        else:

            article_index = self.parent.figshare_article_index

            results = article_index.perform_search(schema='figshare_articles', field=field, query=query)

            self.result_ids = set()

            for docnum, val_dict in results.items():
                if 'id' in val_dict:
                    self.result_ids.add(val_dict['id'])

            self.fill_tree(self.tree_headers, self.result_ids)

    def search_on_clear(self):
        """
        Called when the search bar is cleared
        :param search_text: search bar text
        :return:
        """
        self.fill_tree(self.tree_headers, self.article_ids)

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
        fields = OrderedSet()
        for f in self.get_fields():
            fields.add(f)

        # Define how many columns of check boxes to create
        columns = 3

        # Empty the tree headers list
        #self.tree_headers = []

        # Start at row zero
        row = 0
        # While we still have a field in the ordered set
        while fields:
            for i in range(columns):
                # Here we have to use the exec fundtion to programatically name each box variable otherwise the connect
                # function only ever calls the last button.
                # Further complication from having to remember that the stateChanged signal passes a bool int to the
                # lambda function.
                if len(fields) == 0:
                    break
                lbl = fields.popitem(False)[0]
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

    def get_selection(self):
        """
        Can be called to return a list of the article id numbers of all selected articles
        :return:
        """
        items = self.tree.selectedItems()

        article_ids = set()
        for item in items:
            article_ids.add(int(item.text(0)))

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
            article_ids.add(int(item.text(0)))

        return article_ids

    #####
    # Figshare API Functions
    #####

    def get_fields(self):
        """
        Called to return a list of custom metadata fields
        :return: list of strings
        """

        if len(self.articles) > 0:
            collections = Collections(self.token)
            article_id = self.articles[0]['id']
            result = collections.get_article(article_id)

            keys = set()
            for key in result.keys():
                if key != 'custom_fields':
                    keys.add(key)

            for d in result['custom_fields']:
                keys.add(d['name'])
            return sorted(list(keys))
        else:
            return []


class ArticleLoadWorker(QObject):

    sig_step = pyqtSignal(int)
    sig_done = pyqtSignal(bool)

    def __init__(self, app, OAuth_token: str, parent, collection_id: int, articles: list):
        super().__init__()
        self.__abort = False

        self.app = app
        self.token = OAuth_token
        self.parent = parent
        self.collection_id = collection_id
        self.articles = articles

        self.n_articles = len(articles)

    @pyqtSlot()
    def work(self):
        """

        :return:
        """
        if self.n_articles > 0:
            for article in self.articles:
                self.create_local_article(article)
                self.sig_step.emit(article['id'])

            self.sig_done.emit(True)

    def abort(self):
        self.__abort = True

    def create_local_article(self, article):
        """
        Given a Figshare article id number this function will create a local version if one does not already exist
        :param article: Dict. Figshare article returned from Projects.list_articles()
        :return:
        """
        # Get the article id number and title
        article_id = str(article['id'])  # Convert int to str
        article_title = article['title']

        # If article is not already stored locally create a
        if not self.does_article_exist_locally(article_id):
            article = gen_article(article_title, self.token, None, article_id)
            self.parent.figshare_articles[article_id] = article

            # Locally reference the Figshare Article Index
            article_index = self.parent.figshare_article_index

            # Get the type of the article
            article_type = article.get_type()

            # Check to see if the article type has been added to the articles index.
            # If note we will need to create new fields in the schema.
            if article_type not in article_index.document_types:
                # Add the new file type to the index schema
                article_index.document_types.add(article_type)

                # Define the schema we wish to add fields to
                schema = 'figshare_articles'

                # From the article type created get the index dictionary and add fields to the index
                for field_name, field_type in article.index_schema().items():
                    if field_name not in article_index.get_fields(schema):
                        if field_type[0] == 'id':
                            article_index.add_ID(schema=schema, field_name=field_name, stored=field_type[1],
                                             unique=True)
                        elif field_type[0] == 'text':
                            article_index.add_TEXT(schema, field_name, field_type[1])
                        elif field_type[0] == 'keyword':
                            article_index.add_KEYWORD(schema, field_name, field_type[1])
                        elif field_type[0] == 'numeric':
                            article_index.add_NUMERIC(schema, field_name, field_type[1])
                        elif field_type[0] == 'datetime':
                            article_index.add_DATETIME(schema, field_name, field_type[1])
                        elif field_type[0] == 'boolean':
                            article_index.add_BOOLEAN(schema, field_name, field_type[1])
                        elif field_type[0] == 'ngram':
                            article_index.add_NGRAM(schema, field_name, field_type[1])

            # Get single dictionary of all fields associated to the article
            document_dict = {}
            for d in article.input_dicts():
                document_dict = {**document_dict, **d}

            # Add document to index
            article_index.addDocument(schema='figshare_articles', data_dict=document_dict)

    def does_article_exist_locally(self, article_id):
        """
        Checks to see if there is a local version of the article.
        :param article_id: int. Figshare article id number
        :return: Bool. Dependent on if local version of article exists or not
        """

        # Convert article id to a string. Should have already been done, but just in case we call it somewhere else
        a_id = str(article_id)

        if a_id in self.parent.figshare_articles:
            return True
        else:
            return False


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
