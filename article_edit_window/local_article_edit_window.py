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

        # Determine if file is of a known format to be able to read for additional metadata.
        self.file_specific_layout = self.decide_file_layout(self.local_article_ids)
        # If it is known then add an additional metadata tab.
        if self.file_specific_layout is not None:
            self.tab_layout.addTab(self.file_specific_layout, 'File Metadata')

        hbox.addWidget(self.tab_layout)
        self.setLayout(hbox)

    def confirmation_layout(self):
        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Preferred)

        btn_exit = QPushButton()
        btn_exit.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/exit.png')))
        btn_exit.setSizePolicy(sizepolicy)
        btn_exit.pressed.connect(self.on_exit_pressed)

        btn_save = QPushButton()
        btn_save.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Insert Row Below-48.png')))
        btn_save.setSizePolicy(sizepolicy)
        btn_save.pressed.connect(self.on_save_pressed)
        self.btn_save = btn_save
        if not self.main_window.centralWidget().selection_open:
            self.btn_save.setEnabled(False)

        vbox = QVBoxLayout()

        vbox.addWidget(btn_exit)
        vbox.addWidget(self.btn_save)

        return vbox

    def activate_save_btn(self):
        self.btn_save.setEnabled(True)
    def deactivate_save_btn(self):
        self.btn_save.setEnabled(False)

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

        tab_layout = self.tab_layout

        basic_info_dict = {}
        basic_info_layout = self.basic_info_widget.widget().layout()
        for widget_pos in range(0, basic_info_layout.count() - 1, 2):
            lbl = basic_info_layout.itemAt(widget_pos).widget().text()
            widget = basic_info_layout.itemAt(widget_pos + 1).widget()
            if widget is None:
                widget = basic_info_layout.itemAt(widget_pos + 1).layout()
            widget_type = type(widget)
            if widget_type is QLineEdit:
                if len(self.local_article_ids) > 1:
                    if lbl == 'title':
                        value = None
                    else:
                        value = widget.text()
                else:
                    value = widget.text()
            elif widget_type is QTextEdit:
                value = widget.toPlainText()
            elif widget_type is QHBoxLayout:
                value = []
                for btn_pos in range(0, widget.count() - 2, 1):
                    btn = widget.itemAt(btn_pos).widget()
                    value.append(btn.text())
            elif widget_type is QComboBox:
                value = widget.currentIndex()
            if value is not []:
                basic_info_dict[lbl] = value
            else:
                basic_info_dict[lbl] = None
        update_dict = {**basic_info_dict}

        if self.file_specific_layout is not None:
            file_specific_dict = {}
            file_specific_layout = self.file_specific_layout.widget().layout()
            for widget_pos in range(0, file_specific_layout.count() - 1, 2):
                lbl = file_specific_layout.itemAt(widget_pos).widget().text()
                widget = file_specific_layout.itemAt(widget_pos + 1).widget()
                widget_type = type(widget)
                if widget_type is QLineEdit:
                    value = widget.text()
                elif widget_type is QTextEdit:
                    value = widget.toPlainText()
                if value is not [] and value is not '':
                    file_specific_dict[lbl] = value
                else:
                    file_specific_dict[lbl] = None
            update_dict = {**update_dict, **file_specific_dict}

        if len(self.local_article_ids) > 1:
            local_articles = self.main_window.local_articles
            for local_article_id in self.local_article_ids:
                a_id = local_article_id
                article = local_articles[a_id]
                article.update_info(update_dict)
        else:
            a_id = next(iter(self.local_article_ids))
            article = self.main_window.local_articles[a_id]
            article.update_info(update_dict)

        selection_list = self.main_window.centralWidget().selection_window.selection_article_list
        # Add articles to selection window set.
        selection_list |= self.local_article_ids
        # Update selection qtree
        self.main_window.centralWidget().selection_window.update_article_list_layout()

    def decide_basic_layout(self, article_ids):

        article_id = next(iter(article_ids))
        article = self.main_window.local_articles[article_id]
        basic_info_dict = article.figshare_metadata
        basic_info_layout = self.basic_info_widget.widget().layout()
        for widget_pos in range(0, basic_info_layout.count() - 1, 2):
            lbl = basic_info_layout.itemAt(widget_pos).widget().text()
            edit_widget = basic_info_layout.itemAt(widget_pos + 1).widget()

            if edit_widget is None:
                edit_widget = basic_info_layout.itemAt(widget_pos + 1).layout()

            edit_widget_type = type(edit_widget)
            if edit_widget_type is QLineEdit:
                if len(article_ids) > 1:
                    if lbl == 'title':
                        edit_widget.setText('Multiple Files')
                        edit_widget.setReadOnly(True)
                else:
                    edit_widget.setText(basic_info_dict[lbl])

            elif edit_widget_type is QTextEdit:
                edit_widget.setText(basic_info_dict[lbl])

            elif edit_widget_type is QHBoxLayout:  # This is a button list
                info = basic_info_dict[lbl]
                button_group = self.button_groups[lbl]
                info_strings = []
                info_type = type(info)

                if info_type is list and info != []:
                    list_type = type(info[0])
                    if list_type is dict:
                        for item in info:
                            for value in item.values():
                                info_strings.append(str(value))
                    elif list_type is str:
                        info_strings = info
                    elif list_type is int:
                        for item in info:
                            info_strings.append(str(item))
                    else:
                        pass
                elif info_type is str:
                    info_strings = [info]
                for item in info_strings:
                    self.on_add_button_to_list(button_group, edit_widget, None, item)

            elif edit_widget_type is QComboBox:
                edit_widget.clear()

                if lbl == 'defined_type':
                    info_string = basic_info_dict[lbl]
                    type_dict = {1: 'figure', 2: 'media', 3: 'dataset', 4: 'fileset', 5: 'poster', 6: 'paper',
                                 7: 'presentation', 8: 'thesis', 9: 'code', 10: 'metadata'}
                    for info_pos in range(len(type_dict)):
                        item = type_dict[info_pos + 1]
                        edit_widget.addItem(item)

                    if type(info_string) is int:
                        edit_widget.setCurrentIndex(info_string)
                    elif type(info_string) is str:
                        for key, value in type_dict.items():
                            if value == info_string:
                                edit_widget.setCurrentIndex(key)
                                break

                elif lbl == 'license':
                    info_int = basic_info_dict[lbl]
                    type_list = [None, 'CC BY', 'CC-0', 'MIT', 'GPL', 'GPL-2.0', 'GPL-3.0', 'Apache']

                    for item in type_list:
                        edit_widget.addItem(item)
                    if info_int is None:
                        edit_widget.setCurrentIndex(0)
                    else:
                        edit_widget.setCurrentIndex(info_int)

    def known_file_type(self, article_id):
        article = self.main_window.local_articles[article_id]
        article_type = article.get_type()
        if article_type != 'article':
            return article.input_dicts()[2:]
        else:
            return None

    def decide_file_layout(self, articles_ids):

        # Local reference to the articles dictionary.
        articles = self.main_window.local_articles

        # If more than one article is to be edited check to see if all files are of the same type.
        if len(articles_ids) > 1:
            # Get the type of the first article.
            first_id = next(iter(articles_ids))
            first_type = articles[first_id].get_type()
            # Check that all other articles are the same.
            for article in articles_ids:
                article_type = articles[article].get_type()
                # If article is not the same type as the first return None. Else continue.
                if article_type != first_type:
                    return None
            # At this point we know all files are the same type, but will have different values for their metadata.
            # Here we create a new blank dictionary from the keys of the first article.

            article_dict = self.known_file_type(first_id)
            if article_dict is not None:
                blank_dict = dict.fromkeys(article_dict[0], '')
                return self.file_specific_info_layout([blank_dict])
            else:
                return None

        # If a single article id has been given.
        else:
            first_id = next(iter(articles_ids))
            # Find out if the file type is known.
            article_dicts = self.known_file_type(first_id)
            # If the file type is know generate a file specific metadata layout.
            if article_dicts is not None:
                return self.file_specific_info_layout(article_dicts)
            # Otherwise return nothing.
            else:
                return None
