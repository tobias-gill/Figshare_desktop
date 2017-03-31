"""

"""
import copy

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QProgressBar, QAbstractItemView, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QHBoxLayout, QComboBox, QPushButton, QDialog, QGridLayout, QSizePolicy,
                             QCheckBox)
from PyQt5.QtGui import (QFont, QColor, QPainter)
from PyQt5.QtCore import (Qt, QRect)

from Figshare_desktop.formatting.formatting import (search_bar, search_combo, press_button)

from Figshare_desktop.figshare_articles.determine_type import gen_article
from Figshare_desktop.custom_widgets.progress_bar import ArticleLoadBar
from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ArticleList(QWidget):

    def __init__(self, app, OAuth_token, project_id, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.project_id = project_id
        self.parent = parent

        self.initFig()
        self.initUI()

    def initFig(self, show_progress=True):
        """
        Initial data load from Figshare
        :return:
        """
        # Get the list of articles from
        projects = Projects(self.token)
        articles = projects.list_articles(self.project_id)
        n_articles = len(articles)

        if n_articles > 0 :

            if show_progress:
                # Create progress bar
                bar = ArticleLoadBar(n_articles, self.parent)

            # Create Local Versions of articles
            article_ids = set()
            if show_progress:
                step = 0  # Keep track of how many articles created for progress bar
            for article in articles:
                article_ids.add(article['id'])
                self.create_local_article(article)
                if show_progress:
                    bar.update_progress(step)  # Update progress par
                    step += 1  # Increase progress bar step

        self.article_ids = article_ids
        self.articles = articles

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

        # Create the initial set of column headers
        headers = ['title', 'id', 'created_date', 'up_to_date', 'type', 'tags']
        header_item = QTreeWidgetItem(headers)
        tree.setHeaderItem(header_item)

        self.tree = tree
        self.fill_tree(headers)

        # Adjust the size of the columns to the contents
        for column in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(column)

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
        edit.setToolTipDuration(1)
        # Connect search function to the return key
        edit.returnPressed.connect(self.search_on_return)
        edit.children()[2].triggered.connect(self.search_on_clear)

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

        combo.addItem('')
        combo.addItems(self.get_fields())
        self.search_field_combo = combo
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

        return btn


    #####
    # Widgets Actions
    #####

    def fill_tree(self, headers):
        """
        Called to fill the QTree with articles
        :param headers: list of strings. For article information keys to be filled into the columns of the tree
        :return:
        """

        for article in self.articles:
            article_id = str(article['id'])  # Get the article id number and convert to a string
            local_article = self.parent.figshare_articles[article_id] # Get the local version of the article
            local_article.gen_qtree_item(headers, local_article.input_dicts())  # Update the article qtreeitem
            self.tree.addTopLevelItem(local_article.qtreeitem)  # Add the article qtree item to the tree


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

    def search_on_return(self):
        """
        Called when return is pressed in the search bar.
        :param search_text: Search text
        :return:
        """
        search_field = self.search_field_combo.currentText()
        search_text = self.search_edit.text()
        self.articles = self.search_articles(search_field, search_text, self.token)
        self.tree.clear()
        self.fill_tree(self.tree_headers)

    def search_on_clear(self):
        """
        Called when the search bar is cleared
        :param search_text: search bar text
        :return:
        """
        self.initFig(show_progress=False)
        self.tree.clear()
        self.fill_tree(self.tree_headers)

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


        fields = OrderedSet()
        for f in self.get_fields():
            fields.add(f)

        columns = 3

        self.tree_headers = []

        row = 0
        while fields:
            for i in range(columns):
                exec("chk_box_{}_{} = QCheckBox(fields.popitem()[0])".format(row, i))
                eval("chk_box_{}_{}".format(row, i)).stateChanged.connect(lambda state, r=row, c=i: self.check_box_clicked(r, c))
                # chk_box = QCheckBox(fields.popitem()[0])
                # chk_box.stateChanged.connect(lambda: self.check_box_clicked(row, i))
                grid.addWidget(eval("chk_box_{}_{}".format(row, i)), row, i)
            row += 1

        self.dlg = dlg
        self.headers_box_layout = grid
        self.dlg.show()

    def check_box_clicked(self, row, column):
        """
        Called when a check box in the header selection dialog is clicked
        :return:
        """
        print('=====================')
        print(self.tree_headers)
        print(row, column)
        if self.headers_box_layout.itemAtPosition(row, column) is not None:
            field = self.headers_box_layout.itemAtPosition(row, column).widget().text()
            if field in self.tree_headers:
                self.tree_headers.remove(field)
            elif field not in self.tree_headers:
                self.tree_headers.append(field)
            print(field)
            print(self.tree_headers)


    def on_headers_ok_pressed(self):
        """
        Called when the headers dialog window ok button is pressed
        :return:
        """
        self.dlg.close()
        self.update_headers(self.tree_headers)

    #####
    # Figshare Article Functions
    #####

    def    does_article_exist_locally(self, article_id):
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

    def create_local_article(self, figshare_article):
        """
        Given a Figshare article id number this function will create a local version if one does not already exist
        :param figshare_article: Dict. Figshare article returned from Projects.list_articles()
        :return:
        """
        # Get the article id number and title
        article_id = str(figshare_article['id'])  # Convert int to str
        article_title = figshare_article['title']

        # If article is not already stored locally create a
        if not self.does_article_exist_locally(article_id):
            article = gen_article(article_title, self.token, self.project_id, article_id)
            self.parent.figshare_articles[article_id] = article

    def progress_bar(self, n_articles):
        """
        Called to indicate the progress of creating local version of figshare articles
        :param n_articles:
        :return:
        """

        pbar = QProgressBar()
        pbar.setMaximum(n_articles - 1)

        return pbar

    #####
    # Figshare API Functions
    #####

    def get_fields(self):
        """
        Called to return a list of custom metadata fields
        :return: list of strings
        """

        if len(self.articles) > 0:
            project = Projects(self.token)
            article_id = self.articles[0]['id']
            result = project.get_article(self.project_id, article_id)

            keys = set()
            for key in result.keys():
                if key != 'custom_fields':
                    keys.add(key)

            for d in result['custom_fields']:
                keys.add(d['name'])
            return sorted(list(keys))
        else:
            return []

    def search_articles(self, search_field, search_text, token):
        """
        Called to search the current project articles
        :param project_id: int. Figshare project id number
        :param search_field: string. metadata field
        :param search_text: string. elastic search parameters
        :param token: OAuth token
        :return:
        """

        project = Projects(token)

        if search_field != '':
            search_string = ":{}: {}".format(search_field, search_text)
        else:
            search_string = "{}".format(search_text)

        if len(search_string) >= 3:
            results = project.search_articles(search_string)
            project_results = []
            for result in results:
                if result['id'] in self.article_ids:
                    project_results.append(result)
            return project_results

        else:
            return []

import collections

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
