"""

"""

import os
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTabWidget,
                             QGridLayout, QTextEdit, QLineEdit, QScrollArea, QButtonGroup, QComboBox)
from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (Qt)

from Figshare_desktop.article_edit_window.article_edit_window import ArticleEditWindow

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class LocalArticleEditWindow(ArticleEditWindow):

    def __init__(self, app, OAuth_token, main_window, parent_window_loc, local_article_ids):
        super(QWidget, self).__init__()

        self.app = app
        self.token = OAuth_token
        self.main_window = main_window
        self.piw_loc = parent_window_loc
        self.local_article_ids = local_article_ids

        self.initUI()

    def initUI(self):
        """

        :return:
        """
        # Format the window
        self.formatWindow()

        # Create some default fonts
        self.label_font = self.article_label_font()
        self.edit_font = self.article_edit_font()

        # Create a dictionary to hold button groups as they are created.
        self.button_groups = {}

        # Create a Horizontal layout as the main layout in the window
        hbox = QHBoxLayout()
        # Crate a Tab Widget to fill later.
        self.tab_layout = QTabWidget()

        # Add the confirmation button layout to the main layout
        hbox.addLayout(self.confirmation_layout())

        # Add the basic figshare metadata tab unfilled.
        self.basic_info_widget = self.basic_info_layout()
        self.tab_layout.addTab(self.basic_info_widget, 'Figshare Metadata')

        # Fill in selected metadata from filenames.
        self.decide_basic_layout(self.local_article_ids)

        hbox.addWidget(self.tab_layout)
        self.setLayout(hbox)

    def on_exit_pressed(self):
        """
        Closes the window without saving any metadata.
        :return:
        """
        # Use the data window function to also control tracking.
        self.main_window.centralWidget().data_window.on_selection_pressed()
        # Toggle data window button to prevent out of sync behavior
        self.main_window.centralWidget().data_window.btn_selection.toggle()

    def on_save_pressed(self):

        pass

    def decide_basic_layout(self, local_article_ids):
        """
        From the selection decide how to present existing information in the metadata edit fields.
        :param local_article_ids: List of int. Ids of local_articles.
        :return:
        """

        # Define a local variable to the main window local_articles dictionary.
        local_articles = self.main_window.local_articles
        # Define a local variable to the basic info layout inside the Tab widget.
        basic_info_layout = self.basic_info_widget.widget().layout()
        # Get the local_article_dictionary for the first file in the selection.
        basic_info_dict = local_articles[local_article_ids[0]].figshare_metadata

        # Iterate through all the Label-Widget pairs in the layout.
        for widget_pos in range(0, basic_info_layout.count() - 1, 2):
            # Get the Label 'title' from the QLineEditWidgets
            lbl = basic_info_layout.itemAt(widget_pos).widget().text()
            # Get the editable widget below the label.
            edit_widget = basic_info_layout.itemAt(widget_pos + 1).widget()

            # If the editable widget is None. It is actually a QLayout object.
            if edit_widget is None:
                # Get the layout object, but call t the edit_widget.
                edit_widget = basic_info_layout.itemAt(widget_pos + 1).layout()

            # Find out the type of the editable widget or layout.
            edit_widget_type = type(edit_widget)

            # QLineEdit.
            if edit_widget_type is QLineEdit:
                # For now we only know the title so ignore other labels.
                if lbl == 'title':
                    # If multiple files are selected we will auto-generate the article titles from their file names.
                    if len(local_article_ids) > 1:
                        edit_widget.setText('Titles will be set from file names')
                        edit_widget.setReadOnly(True)

                    # If only a single file is selected initially fill the title from the file, but allow for edits.
                    else:
                        edit_widget.setText(basic_info_dict[lbl])

            # QComboBox
            elif edit_widget_type is QComboBox:
                # Remove all existing fields in the QComboBox. These will likely be blank anyway.
                edit_widget.clear()

                # DEFINED_TYPE
                if lbl == 'defined_type':
                    # There are a small set of allowed types. For now we will define them here.
                    # SHOULD MAKE THIS A SINGLE VARIABLE IN A CONFIG FILE AT SOME POINT.
                    type_dict = {1: 'figure', 2: 'media', 3: 'dataset', 4: 'fileset', 5: 'poster', 6: 'paper',
                                 7: 'presentation', 8: 'thesis', 9: 'code', 10: 'metadata'}

                    # Add all types to the QComboBox
                    for info_pos in range(len(type_dict)):
                        item = type_dict[info_pos + 1]
                        edit_widget.addItem(item)

                    # For now we will set a default value of fileset.
                    edit_widget.setCurrentIndex(3)

                # LICENSE
                elif lbl == 'license':
                    # There are a small set of allowed licenses. For now we will define them here.
                    # SHOULD MAKE THIS A SINGLE VARIABLE IN A CONFIG FILE AT SOME POINT.
                    type_list = [None, 'CC BY', 'CC-0', 'MIT', 'GPL', 'GPL-2.0', 'GPL-3.0', 'Apache']

                    # Add all types to the QComboBox.
                    for item in range(len(type_list)):
                        edit_widget.addItem(item)

                    # Set default value as None for now
                    edit_widget.setCurrentIndex(0)
