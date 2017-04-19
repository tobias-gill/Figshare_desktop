"""

"""

import os
from requests import HTTPError

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QScrollArea, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QTabWidget, QComboBox)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.formatting.formatting import (label_font)

from Figshare_desktop.custom_widgets.button_field import QButtonField

from Figshare_desktop.formatting.formatting import (grid_label, grid_edit, press_button, grid_title)

from figshare_interface import (Groups, Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ArticleEditWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent, project_id, article_ids):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent
        self.project_id = project_id
        self.article_ids = article_ids

        self.initFig()
        self.initUI()

    def initFig(self):
        """
        Initialises the figshare data
        :return:
        """
        # Get the number of articles
        n_articles = len(self.article_ids)

        # For more than one article
        if n_articles > 1:
            # Get the type of article for the first in the list
            article = self.parent.figshare_articles[str(self.article_ids[0])]
            initial_type = article.get_type()
            # Initially set all files as the same type
            self.same_type = True
            # Loop through all files and check to see if they are all the same
            for article_id in self.article_ids:
                article = self.parent.figshare_articles[str(article_id)]
                type = article.get_type()
                if type != initial_type:
                    self.same_type = False
                    break

            # Set the dictionary of metadata keys
            figshare_metadata = {}
            article = self.parent.figshare_articles[str(self.article_ids[0])]
            for d in article.input_dicts()[0:1]:
                figshare_metadata = {**figshare_metadata, **d}
            self.figshare_metadata = dict.fromkeys(figshare_metadata)

            # Set the dictionary of file specific metadata keys
            self.file_metadata = None
            if self.same_type:
                if len(article.input_dicts()) > 2:
                    file_dict = {}
                    for d in article.input_dicts()[2:]:
                        file_dict = {**file_dict, **d}
                    self.file_metadata = dict.fromkeys(file_dict)

        # For a single article
        else:

            # Set the dictionary of metadata keys and values
            figshare_metadata = {}
            article = self.parent.figshare_articles[str(self.article_ids[0])]
            for d in article.input_dicts()[0:1]:
                figshare_metadata = {**figshare_metadata, **d}
            self.figshare_metadata = figshare_metadata

            # Set the dictionary of file specific metadata keys and values
            self.file_metadata = None
            if len(article.input_dicts()) > 2:
                file_dict = {}
                for d in article.input_dicts()[2:]:
                    file_dict = {**file_dict, **d}
                self.file_metadata = file_dict

        # Metadata Dictionaries
        self.defined_type_dict = {'': 0, 'figure': 1, 'media': 2, 'dataset': 3, 'fileset': 4, 'poster': 5, 'paper': 6,
                                  'presentation': 7, 'thesis': 8, 'code': 9, 'metadata': 10}
        self.license_dict = {0: '', 1: 'CC BY', 2: 'CC-0', 3: 'MIT', 4: 'GPL', 5: 'GPL-2.0', 6: 'GPL-3.0',
                             7: 'Apache-2.0'}

    def initUI(self):

        # Format the geometry of the window
        self.format_window()

        # Create a horizontal layout
        self.hbox = QHBoxLayout()

        # Add the save and exit buttons
        self.hbox.addLayout(self.control_button_layout())

        # Add the tab widget
        self.tabs = self.metadata_tab_window()
        self.hbox.addWidget(self.tabs)

        # Create a central widget for the article edit window
        window_widget = QWidget()
        # Add the horizontal box layout
        window_widget.setLayout(self.hbox)
        # Set the projects window widget
        self.setWidget(window_widget)

    #####
    # Window Formatting
    #####

    def format_window(self):
        """
        Sets the window geometry
        :return:
        """
        # Gets the QRect of the main window
        geom = self.parent.geometry()
        # Gets the Qrect of the sections window
        section_geom = self.parent.section_geom
        # Define geometries for the projects window
        x0 = section_geom.x() + section_geom.width()
        y0 = section_geom.y()
        w = geom.width() - x0
        h = ((geom.height() - y0) * 0.375)
        self.setGeometry(x0, y0, w, h)
        # Remove frame from the window
        self.setWindowFlags(Qt.FramelessWindowHint)

    #####
    # Window Widgets
    #####

    def control_button_layout(self):
        """
        Creates a layout with the save and exit buttons
        :return: QVBoxLayout
        """
        # Create the layout
        vbox = QVBoxLayout()
        # Add the exit button
        exit_btn = self.exit_button()
        vbox.addWidget(exit_btn)
        # Add the save button
        save_btn = self.save_button()
        vbox.addWidget(save_btn)

        return vbox

    def exit_button(self):
        """
        Creates an exit button to close the article edit window without saving changes
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/exit.png')))
        press_button(self.app, btn)
        btn.pressed.connect(self.on_exit_pressed)

        return btn

    def save_button(self):
        """
        Creates a save button to push changes to Figshare
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.normpath(__file__ + '/../../img/figshare_upload.png')))
        press_button(self.app, btn)
        btn.pressed.connect(self.on_save_pressed)

        return btn

    def metadata_tab_window(self):
        """
        Creates a tab layout to hold the different metadata tabs
        :return:
        """
        # Create Tab Widget
        tab_wid = QTabWidget()

        # Add Figshare Metadata Tab
        self.figshare_tab = self.init_figshare_metadata_tab()
        tab_wid.addTab(self.figshare_tab, 'Figshare Metadata')

        if self.file_metadata is not None:
            self.filespecific_tab = self.init_filespecific_metadata_tab()
            tab_wid.addTab(self.filespecific_tab, 'File Specific Metadata')

        return tab_wid

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
        cat_lbl, cat_field = self.create_buttonfield('Categories', self.figshare_metadata['categories'])
        auth_lbl, auth_field = self.create_buttonfield('Authors', self.figshare_metadata['authors'])
        def_lbl, def_combo = self.create_combo('Defined Type', self.defined_type_dict,
                                               self.figshare_metadata['defined_type'])

        fund_tags = self.figshare_metadata['funding']
        if self.figshare_metadata['funding'] is not None:
            fund_tags = self.figshare_metadata['funding'].split(':_:')
            if '' in fund_tags:
                fund_tags.remove('')
            if ' ' in fund_tags:
                fund_tags.remove(' ')
        fund_lbl, fund_field = self.create_buttonfield('Funding', fund_tags)

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
        article = self.parent.figshare_articles[str(self.article_ids[0])]

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

    def create_label(self, label):
        """
        Creates and formats a QLabel
        :param label: String.
        :return: QLabel
        """
        lbl = QLabel(label)
        grid_label(self.app, lbl)
        lbl.setMaximumWidth(self.geometry().width() * 0.2)

        return lbl

    def create_lineedit(self, label, fill):
        """
        Creates and formats a QLabel and QlineEdit pair
        :param label: String.
        :param fill: String
        :return: QLabel, QLineEdit
        """
        lbl = self.create_label(label)

        edit = QLineEdit(fill)
        grid_edit(self.app, edit)

        return lbl, edit

    def create_textedit(self, label, fill):
        """
        Creates and formats a QLabel and QTextEdit pair
        :param label: String.
        :param fill: String.
        :return: QLabel, QTextEdit
        """
        lbl = self.create_label(label)

        edit = QTextEdit(fill)
        grid_edit(self.app, edit)

        return lbl, edit

    def create_buttonfield(self, label, fill_list):
        """
        Creates and formats a QLabel and QButtonfield pair
        :param label: String
        :param fill_list: List of Strings
        :return: QLabel, QButtonField
        """
        lbl = self.create_label(label)

        button_field = QButtonField()
        if fill_list is not None:
            for tag in fill_list:
                if type(tag) == dict:
                    button_field.add_tag(tag['id'])
                else:
                    button_field.add_tag(tag)

        return lbl, button_field

    def create_combo(self, label, metadata_dict, fill):
        """
        Creates and formats a QLabel and QComboBox pair
        :param label: String
        :param fill_list: list of strings.
        :return: QLabel, QComboBox
        """
        lbl = self.create_label(label)

        combo = QComboBox()
        for key, value in metadata_dict.items():
            if type(key) is str:
                combo.addItem(key)
            else:
                combo.addItem(value)
        if type(fill) is int:
            combo.setCurrentIndex(fill)
        elif type(fill) is str:
            try:
                fill = int(fill)
                combo.setCurrentIndex(metadata_dict[fill])
            except:
                combo.setCurrentIndex(0)
        return lbl, combo

    #####
    # Widget Actions
    #####

    def on_exit_pressed(self):
        """
        Called when the exit button is pressed. Closes the article edit window without saving any changes
        :return:
        """
        # Close article edit window
        self.parent.open_windows.remove('article_edit_window')
        self.parent.article_edit_window.close()

        # Open project articles window
        self.parent.project_info_window.on_articles_pressed()

    def on_save_pressed(self):
        """
        Called when the save button is pressed. Pushes changes to figshare and creates a confirmation dialog
        :return:
        """
        self.update_all_articles(self.article_ids)

    #####
    # Figshare Actions
    #####

    def update_all_articles(self, article_list):
        """
        Updates multiple articles
        :param article_list: list of int.
        :return:
        """
        all_errors = []
        for article_id in article_list:
            errors = self.update_single_article(article_id)
            if errors != []:
                for err in errors:
                    all_errors.append(err)

        if all_errors == []:
            msg = "All articles updated"
            resp = QMessageBox.information(self, "Update Confirmation", msg, QMessageBox.Ok)
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Error in update.")
            detailed_msg = ""
            for err in all_errors:
                for arg in err.args:
                    detailed_msg += arg + '\n'
            msg_box.setDetailedText(detailed_msg)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.show()

    def update_single_article(self, article_id):
        """
        Updates a single figshare article
        :param article_id:
        :return:
        """
        err_figshare = self.update_article_figshare_metadata(article_id)

        if self.file_metadata is not None:
            err_filespecific = self.update_article_file_metadata(article_id)

        errors = []
        if err_figshare is not None:
            errors.append(err_figshare)
        if self.file_metadata is not None and err_filespecific is not None:
            errors.append(err_filespecific)

        return errors

    def update_article_figshare_metadata(self, article_id):
        """
        Updates the figshare metadata of a single article
        :param article_id:
        :return:
        """
        # Get the current/old figshare metadata
        article = self.parent.figshare_articles[str(article_id)]
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
        categories = [int(i) for i in cat_list]
        new_figshare_metadata['categories'] = categories
        # Authors
        auth_list = figshare_grid.itemAtPosition(5, 1).widget().get_tags()
        authors = [{'id': int(i)} for i in auth_list]
        new_figshare_metadata['authors'] = authors
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
        new_figshare_metadata['license'] = license

        # Create an empty dictionary to add updates/edits
        update_dict = {}

        # Check for changes
        for key, value in new_figshare_metadata.items():

            if value != 'None' and value is not None and value != '':
                if value != old_figshare_metadata[key]:
                    update_dict[key] = value

        try:
            project = Projects(self.token)
            proj_info = project.update_article(self.token, article_id, update_dict)

            # Update local version of article
            article.update_info(update_dict)

            # Change up_to_date
            article.figshare_metadata['up_to_date'] = False

            return None
        except HTTPError as err:
            return err
        except TypeError as err:
            return err
        except ValueError as err:
            return err

    def update_article_file_metadata(self, article_id):
        """
        Updates an articles custom fields metadata
        :param article_id: int. Figshare article id number
        :return:
        """
        # Get the current/old file specific metadata
        article = self.parent.figshare_articles[str(article_id)]
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

        # Reformat update dictionary
        update_dict = {'custom_fields': update_dict}

        try:
            project = Projects(self.token)
            proj_info = project.update_article(self.token, article_id, update_dict)

            # Update local version of article
            article.update_info(update_dict)

            return None
        except HTTPError as err:
            return err
        except TypeError as err:
            return err
        except ValueError as err:
            return err

