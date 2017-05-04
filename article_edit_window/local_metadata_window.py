"""

"""

# PyQt Imports
from PyQt5.QtWidgets import (QMdiSubWindow, QScrollArea,
                             QWidget, QGridLayout)

# Figshare Desktop Imports
from Figshare_desktop.article_edit_window.article_edit_window import ArticleEditWindow

# Figshare API Imports
from figshare_interface.http_requests.figshare_requests import issue_request

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class LocalMetadataWindow(ArticleEditWindow):

    def __init__(self, app, OAuth_token, parent, article_ids):
        super(QMdiSubWindow, self).__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent
        self.article_ids = article_ids

        self.initFig()
        self.initUI()

    def initFig(self):
        """
        Initialises the figshare data
        :return:
        """
        n_articles = len(self.article_ids)

        # For more than one files
        if n_articles > 1:

            # First generate an empty dictionary for the default figshare metadata
            figshare_metadata = {}
            article = self.parent.local_articles[self.article_ids[0]]
            for d in article.input_dicts()[0:1]:
                figshare_metadata = {**figshare_metadata, **d}
            self.figshare_metadata = dict.fromkeys(figshare_metadata)

            # Get the type of the first article
            article = self.parent.local_articles[self.article_ids[0]]
            initial_type = article.get_type()

            # Initially set all files as the same type
            self.same_type = True

            for article_id, article in self.parent.local_articles.items():
                article_type = article.get_type()
                if article_type != initial_type:
                    self.same_type = False
                    break

            # Set the file specific metdata dictionary as None by default
            self.file_metadata = None

            # If all files are of the same kind then generate an empty dictionary from the file specific metadata
            if self.same_type:
                if len(article.input_dicts()) > 2:
                    file_dict = {}
                    for d in article.input_dicts()[2:]:
                        file_dict = {**file_dict, **d}
                    self.file_metadata = dict.fromkeys(file_dict)

        # For a Single Article
        else:

            # First get dictionary for the default figshare metadata
            self.figshare_metadata = self.parent.local_articles[self.article_ids[0]].figshare_metadata

            article = self.parent.local_articles[self.article_ids[0]]
            # Set the dictionary of file specific metadata keys and values
            self.file_metadata = None
            if len(article.input_dicts()) > 2:
                file_dict = {}
                for d in article.input_dicts()[2:]:
                    file_dict = {**file_dict, **d}
                self.file_metadata = file_dict

        # Metadata Dictionaries
        allowed_cats = issue_request(method='GET', endpoint='categories', token=self.token)
        self.cat_dict = {}
        for cat in allowed_cats:
            self.cat_dict[cat['id']] = cat['title']

        self.defined_type_dict = {'': 0, 'figure': 1, 'media': 2, 'dataset': 3, 'fileset': 4, 'poster': 5,
                                  'paper': 6,
                                  'presentation': 7, 'thesis': 8, 'code': 9, 'metadata': 10}
        self.license_dict = {0: '', 1: 'CC BY', 2: 'CC-0', 3: 'MIT', 4: 'GPL', 5: 'GPL-2.0', 6: 'GPL-3.0',
                             7: 'Apache-2.0'}

    #####
    # Window Formatting
    #####

    #####
    # Window Widgets
    #####

    def init_figshare_metadata_tab(self):
        """
        Creates a QWidget for the default Figshare metadata
        :return:
        """

        # Create widget object to fill with metadata
        tab = QScrollArea()
        scroll_wid = QWidget()

        # Create metadata labels and fields
        title_lbl, title_edit = self.create_lineedit('Title', self.figshare_metadata['title'])
        if len(self.article_ids) > 1:
            title_edit.setEnabled(False)
            title_edit.clear()
            title_edit.setPlaceholderText('Files will retain their individual titles')
        descr_lbl, descr_edit = self.create_textedit('Description', self.figshare_metadata['description'])
        ref_lbl, ref_field = self.create_buttonfield('References', self.figshare_metadata['references'])
        tags_lbl, tags_field = self.create_buttonfield('Tags', self.figshare_metadata['tags'])
        cat_lbl, cat_field = self.create_categories_field('Categories', self.figshare_metadata['categories'])
        auth_lbl, auth_field = self.create_author_field('Authors', self.figshare_metadata['authors'])
        def_lbl, def_combo = self.create_combo('Defined Type', self.defined_type_dict,
                                               self.figshare_metadata['defined_type'])
        fund_lbl, fund_field = self.create_buttonfield('Funding', self.figshare_metadata['funding'])
        lic_lbl, lic_combo = self.create_combo('License', self.license_dict, self.figshare_metadata['license'])

        # Create layout
        grid = QGridLayout()

        # Add widgets to layout
        grid.addWidget(title_lbl, 0, 0)
        grid.addWidget(title_edit, 0, 1)
        grid.addWidget(descr_lbl, 1, 0)
        grid.addWidget(descr_edit, 1, 1)
        grid.addWidget(ref_lbl, 2, 0)
        grid.addWidget(ref_field, 2, 1)
        grid.addWidget(tags_lbl, 3, 0)
        grid.addWidget(tags_field, 3, 1)
        grid.addWidget(cat_lbl, 4, 0)
        grid.addWidget(cat_field, 4, 1)
        grid.addWidget(auth_lbl, 5, 0)
        grid.addWidget(auth_field, 5, 1)
        grid.addWidget(def_lbl, 6, 0)
        grid.addWidget(def_combo, 6, 1)
        grid.addWidget(fund_lbl, 7, 0)
        grid.addWidget(fund_field, 7, 1)
        grid.addWidget(lic_lbl, 8, 0)
        grid.addWidget(lic_combo, 8, 1)

        scroll_wid.setLayout(grid)
        tab.setWidget(scroll_wid)

        return tab

    def init_filespecific_metadata_tab(self):
        """
        Creates a QTabWidget to add to the article edit window
        :return:
        """
        # Get the first article from the article is list
        article = self.parent.local_articles['local_0']

        # Check to see if the article is a known file format
        if self.file_metadata is not None:

            # Create widget object to fill with metadata
            tab = QScrollArea()
            scroll_wid = QWidget()

            grid = QGridLayout()

            row_number = 0

            for key, value in self.file_metadata.items():
                value = str(value)
                lbl, edit = self.create_lineedit(key, value)
                grid.addWidget(lbl, row_number, 0)
                grid.addWidget(edit, row_number, 1)
                row_number += 1

            scroll_wid.setLayout(grid)
            tab.setWidget(scroll_wid)

            return tab

    #####
    # Widget Actions
    #####

    def on_exit_pressed(self):
        """
        overrides parent
        :return:
        """
        # Close the article edit window
        self.parent.open_windows.remove('local_article_edit_window')
        self.parent.local_article_edit_window.close()

        # Open the local articles window
        self.parent.section_window.open_data_articles_window()
        article_tree = self.parent.data_articles_window.article_tree
        article_tree.article_ids = set(self.parent.local_articles.keys())
        article_tree.fill_tree(article_tree.tree_headers, article_tree.article_ids)
        article_tree.enable_fields()
        self.parent.data_articles_window.edit_btn.setEnabled(True)

    #####
    # Figshare Actions
    #####

    def update_article_figshare_metadata(self, local_article_id: str):
        """
        :param local_article_id: String containing the local article id, 'local_#'
        :return:
        """
        # Get the current/old figshare metadata
        article = self.parent.local_articles[local_article_id]
        old_figshare_metadata = article.figshare_metadata

        # Get the new/edited figshare metadata
        new_figshare_metadata = {}
        figshare_grid = self.figshare_tab.widget().layout()

        # Title
        title = figshare_grid.itemAtPosition(0, 1).widget().text()
        new_figshare_metadata['title'] = title
        # Description
        description = figshare_grid.itemAtPosition(1, 1).widget().toPlainText()
        new_figshare_metadata['description'] = description
        # References
        references = figshare_grid.itemAtPosition(2, 1).widget().get_tags()
        new_figshare_metadata['references'] = references
        # Tags
        tags = figshare_grid.itemAtPosition(3, 1).widget().get_tags()
        new_figshare_metadata['tags'] = tags
        # Categories
        cat_list = figshare_grid.itemAtPosition(4, 1).widget().get_tags()
        new_figshare_metadata['categories'] = cat_list
        # Authors
        auth_list = figshare_grid.itemAtPosition(5, 1).widget().get_tags()
        new_figshare_metadata['authors'] = auth_list
        # Defined Type
        defined_type = figshare_grid.itemAtPosition(6, 1).widget().currentText()
        new_figshare_metadata['defined_type'] = defined_type
        # Funding
        fund_tags = figshare_grid.itemAtPosition(7, 1).widget().get_tags()
        funding = ''
        for tag in fund_tags:
            funding += tag + ':_:'
        new_figshare_metadata['funding'] = funding
        # License
        license = figshare_grid.itemAtPosition(8, 1).widget().currentIndex()
        license = str(license)
        new_figshare_metadata['license'] = license

        # Create an empty dictionary to add updates/edits
        update_dict = {}

        # Check for changes
        for key, value in new_figshare_metadata.items():

            if value != 'None' and value is not None and value != '' and value != []:
                if value != old_figshare_metadata[key]:
                    update_dict[key] = value

        # Update the local article
        article.update_info(update_dict)

        # If there is no file specific metadata then update the Whoosh index document now
        if self.file_metadata is None:
            self.update_document(local_article_id)

    def update_article_file_metadata(self, local_article_id: str):
        """
        overrides parent
        :return:
        """
        # Get the current/old file specific metadata
        article = self.parent.local_articles[local_article_id]
        old_file_dicts = article.input_dicts()[2:]
        old_file_metadata = {}
        for d in old_file_dicts:
            for key, value in d.items():
                old_file_metadata[key] = value

        # Get the new/edited figshare metadata
        new_file_metadata = {}
        file_grid = self.filespecific_tab.widget().layout()

        # Get the number of rows in the grid layout
        n_rows = file_grid.rowCount()

        # Get the new file metadata
        for row in range(n_rows):
            lbl = file_grid.itemAtPosition(row, 0).widget().text()
            edit = file_grid.itemAtPosition(row, 1).widget().text()

            new_file_metadata[lbl] = edit

        # Check for changes
        update_dict = {}
        for key, value in new_file_metadata.items():
            if value != 'None':
                if value != old_file_metadata[key]:
                    update_dict[key] = value

        # Update local version of article
        article.update_info(update_dict)

        # Update the Whoosh index document
        self.update_document(local_article_id)

    def update_document(self, article_id):
        """
        Updates the Whoosh Index document of the given article
        :param article_id:
        :return:
        """
        update_dict = {}
        for d in self.parent.local_articles[article_id].input_dicts():
            update_dict = {**update_dict, **d}

        self.parent.local_article_index.updateDocument('local_articles', update_dict)
