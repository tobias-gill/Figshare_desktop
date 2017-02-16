"""

"""
import os
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QPushButton, QLabel, QHBoxLayout, QVBoxLayout,
                             QGridLayout, QTextEdit, QLineEdit, QScrollArea, QButtonGroup)
from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (Qt)

from figshare_interface.figshare_structures.projects import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ArticleEditWindow(QWidget):

    def __init__(self, app, OAuth_token, main_window, projects_info_window_loc, article_ids, project_id=None, collection_id=None):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.main_window = main_window
        self.piw_loc = projects_info_window_loc

        self.articles_ids = article_ids

        if project_id is not None:
            self.project_id = project_id
        if collection_id is not None:
            self.collection_id = collection_id

        self.initUI()

    def initUI(self):

        self.formatWindow()

        self.label_font = self.article_label_font()
        self.edit_font = self.article_edit_font()

        hbox = QHBoxLayout()

        hbox.addLayout(self.confirmation_layout())
        self.basic_info_widget = self.basic_info_layout()
        self.decide_basic_layout(self.articles_ids)
        hbox.addWidget(self.basic_info_widget)

        self.file_specific_layout = self.decide_file_layout(self.articles_ids)
        if self.file_specific_layout is not None:
            hbox.addWidget(self.file_specific_layout)

        self.setLayout(hbox)

    def formatWindow(self):

        piw_x0 = self.piw_loc.x()
        piw_y0 = self.piw_loc.y()
        piw_width = self.piw_loc.width()
        piw_height = self.piw_loc.height()

        screen = self.app.primaryScreen().availableGeometry()

        x0 = piw_x0
        y0 = piw_y0 + piw_height + 10
        w_width = screen.width() - x0
        w_height = screen.height() / 3

        self.setGeometry(x0, y0, w_width, w_height)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def confirmation_layout(self):
        sizepolicy = QSizePolicy()
        sizepolicy.setVerticalPolicy(QSizePolicy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Preferred)

        btn_exit = QPushButton()
        btn_exit.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/exit.png')))
        btn_exit.setSizePolicy(sizepolicy)
        btn_exit.pressed.connect(self.on_exit_pressed)

        btn_save = QPushButton()
        btn_save.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/figshare_upload.png')))
        btn_save.setSizePolicy(sizepolicy)
        btn_save.pressed.connect(self.on_save_pressed)

        vbox = QVBoxLayout()

        vbox.addWidget(btn_exit)
        vbox.addWidget(btn_save)

        return vbox

    def basic_info_layout(self):
        """
        Create a Layout containing editable fields for the basic figshare article metadata.
        :return:
        """

        # Size Policies
        # - Expand Vertically and Horizontally
        fullSizePolicy = QSizePolicy()
        fullSizePolicy.setVerticalPolicy(QSizePolicy.Expanding)
        fullSizePolicy.setHorizontalPolicy(QSizePolicy.Expanding)
        # - Expand Vertically
        vertSizePolicy = QSizePolicy()
        vertSizePolicy.setVerticalPolicy(QSizePolicy.Expanding)
        vertSizePolicy.setHorizontalPolicy(QSizePolicy.Preferred)
        # - Expand Horizontally
        horSizePolicy = QSizePolicy()
        horSizePolicy.setVerticalPolicy(QSizePolicy.Preferred)
        horSizePolicy.setHorizontalPolicy(QSizePolicy.Expanding)

        window_size = self.geometry()

        # Grid Layout
        basic_info_widget = QWidget()
        vbox = QVBoxLayout(basic_info_widget)

        # Fonts
        # - Label Font
        s = window_size.height() / 20
        max_s = 14
        min_s = 10
        if s < min_s:
            s = min_s
        elif max_s < s:
            s = max_s
        lbl_font = QFont('SansSerif', s)
        lbl_font.setBold(True)

        # - Edit Font
        s = window_size.height() / 25
        max_s = 12
        min_s = 7
        if s < min_s:
            s = min_s
        elif max_s < s:
            s = max_s
        edit_font = QFont('SansSerif', s)

        # Title Label
        lbl_title = QLabel('title')
        lbl_title.setFont(lbl_font)
        lbl_title.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_title)

        # Title Edit
        edit_title = QLineEdit()
        edit_title.setFont(edit_font)
        edit_title.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_title)

        # Description Label
        lbl_description = QLabel('description')
        lbl_description.setFont(lbl_font)
        lbl_description.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_description)

        # Description Edit
        edit_description = QTextEdit()
        edit_description.setFont(edit_font)
        edit_description.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_description)

        # Tags Label
        lbl_tags = QLabel('tags')
        lbl_tags.setFont(lbl_font)
        lbl_tags.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_tags)

        # Tags Edit
        edit_tags = QLineEdit()
        edit_tags.setFont(edit_font)
        edit_tags.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_tags)

        # Cateories Label
        lbl_categories = QLabel('categories')
        lbl_categories.setFont(lbl_font)
        lbl_categories.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_categories)

        # Categories Edit
        edit_categories = QLineEdit()
        edit_categories.setFont(edit_font)
        edit_categories.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_categories)

        # References Label
        lbl_references = QLabel('references')
        lbl_references.setFont(lbl_font)
        lbl_references.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_references)

        # References Edit
        edit_references = QLineEdit()
        edit_references.setFont(edit_font)
        edit_references.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_references)

        # Authors Label
        lbl_authors = QLabel('authors')
        lbl_authors.setFont(lbl_font)
        lbl_authors.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_authors)

        # Authors Edit
        edit_authors = QLineEdit()
        edit_authors.setFont(edit_font)
        edit_authors.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_authors)

        # Defined Type Label
        lbl_definedtype = QLabel('defined_type')
        lbl_definedtype.setFont(lbl_font)
        lbl_definedtype.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_definedtype)

        # Defined Type Edit
        edit_definedtype = QLineEdit()
        edit_definedtype.setFont(edit_font)
        edit_definedtype.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_definedtype)

        # Funding Label
        lbl_funding = QLabel('funding')
        lbl_funding.setFont(lbl_font)
        lbl_funding.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_funding)

        # Funding Edit
        edit_funding = QLineEdit()
        edit_funding.setFont(edit_font)
        edit_funding.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_funding)

        # License Label
        lbl_license = QLabel('license')
        lbl_license.setFont(lbl_font)
        lbl_license.setSizePolicy(horSizePolicy)
        vbox.addWidget(lbl_license)

        # License Edit
        edit_license = QLineEdit()
        edit_license.setFont(edit_font)
        edit_license.setSizePolicy(horSizePolicy)
        vbox.addWidget(edit_license)

        scroll_area = QScrollArea()
        scroll_area.setWidget(basic_info_widget)
        scroll_area.setWidgetResizable(True)

        return scroll_area

    def decide_basic_layout(self, article_ids):

        if len(article_ids) > 1:
            article = self.main_window.articles[int(article_ids[0])]
            basic_info_dict = article.figshare_metadata

            basic_info_layout = self.basic_info_widget.widget().layout()

            for widget_pos in range(0, basic_info_layout.count() - 1, 2):
                lbl = basic_info_layout.itemAt(widget_pos).widget().text()
                basic_info_layout.itemAt(widget_pos + 1).widget().setText(basic_info_dict[lbl])
                if lbl == 'title':
                    basic_info_layout.itemAt(widget_pos + 1).widget().setText('Multiple Files')
                    basic_info_layout.itemAt(widget_pos + 1).widget().setReadOnly(True)
        else:
            article = self.main_window.articles[int(article_ids[0])]
            basic_info_dict = article.figshare_metadata

            basic_info_layout = self.basic_info_widget.widget().layout()

            for widget_pos in range(0, basic_info_layout.count() - 1, 2):
                lbl = basic_info_layout.itemAt(widget_pos).widget().text()
                # The string call in this function produces the nested strings of lists I think.
                value = basic_info_dict[lbl]
                setText_str = ''
                if type(value) is list:
                    for item in value:
                        setText_str

                basic_info_layout.itemAt(widget_pos + 1).widget().setText(str(basic_info_dict[lbl]))


    def file_specific_info_layout(self, article_dicts):

        window_size = self.geometry()

        # Fonts
        # - Label Font
        s = window_size.height() / 20
        min_s = 10
        if s < min_s:
            lbl_font_size = min_s
        else:
            lbl_font_size = s
        lbl_font = QFont('SansSerif', lbl_font_size)
        lbl_font.setBold(True)

        # - Edit Font
        s = window_size.height() / 25
        min_s = 7
        if s < min_s:
            edit_font_size = min_s
        else:
            edit_font_size = s
        edit_font = QFont('SansSerif', edit_font_size)

        # - Expand Horizontally
        horSizePolicy = QSizePolicy()
        horSizePolicy.setVerticalPolicy(QSizePolicy.Preferred)
        horSizePolicy.setHorizontalPolicy(QSizePolicy.Expanding)

        file_info_widget = QWidget()
        vbox = QVBoxLayout(file_info_widget)

        for dictionary in article_dicts:

            for key, value in dictionary.items():
                lbl = QLabel(str(key))
                lbl.setFont(lbl_font)
                lbl.setSizePolicy(horSizePolicy)
                vbox.addWidget(lbl)

                edit = QLineEdit()
                edit.setFont(edit_font)
                edit.setText(str(value))
                edit.setSizePolicy(horSizePolicy)
                vbox.addWidget(edit)

        scroll_area = QScrollArea()
        scroll_area.setWidget(file_info_widget)
        scroll_area.setWidgetResizable(True)

        return scroll_area

    def known_file_type(self, article_id):
        article = self.main_window.articles[int(article_id)]
        article_type = article.get_type()
        if article_type != 'article':
            return article.input_dicts()[2:]
        else:
            return None

    def decide_file_layout(self, articles_ids):

        # Local reference to the articles dictionary.
        articles = self.main_window.articles

        # If more than one article is to be edited check to see if all files are of the same type.
        if len(articles_ids) > 1:
            # Get the type of the first article.
            first_type = articles[int(articles_ids[0])].get_type()
            # Check that all other articles are the same.
            for article in articles_ids:
                article_type = articles[int(article)].get_type()
                # If article is not the same type as the first return None. Else continue.
                if article_type != first_type:
                    return None
            # At this point we know all files are the same type, but will have different values for their metadata.
            # Here we create a new blank dictionary from the keys of the first article.

            article_dict = self.known_file_type(int(articles_ids[0]))
            if article_dict is not None:
                blank_dict = dict.fromkeys(article_dict[0], '')
                return self.file_specific_info_layout([blank_dict])
            else:
                return None

        # If a single article id has been given.
        else:
            # Find out if the file type is known.
            article_dicts = self.known_file_type(articles_ids[0])
            # If the file type is know generate a file specific metadata layout.
            if article_dicts is not None:
                return self.file_specific_info_layout(article_dicts)
            # Otherwise return nothing.
            else:
                return None

    def on_exit_pressed(self):
        self.close()
        self.main_window.centralWidget().projects_window.projects_info_window.on_show_articles_pressed()

    def on_save_pressed(self):

        basic_info_dict = {}
        basic_info_layout = self.basic_info_widget.widget().layout()

        for widget_pos in range(0, basic_info_layout.count() - 1, 2):
            lbl = basic_info_layout.itemAt(widget_pos).widget().text()
            widget = basic_info_layout.itemAt(widget_pos + 1).widget()
            if type(widget) is QLineEdit:
                value = widget.text()
            elif type(widget) is QTextEdit:
                value = widget.toPlainText()
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
                if type(widget) is QLineEdit:
                    value = widget.text()
                elif type(widget) is QTextEdit:
                    value = widget.toPlainText()
                if value is not []:
                    file_specific_dict[lbl] = value
                else:
                    file_specific_dict[lbl] = None

            update_dict = {**basic_info_dict, **file_specific_dict}

        if len(self.articles_ids) > 1:
            articles = self.main_window.articles
            for article_id in self.articles_ids:
                article = articles[int(article_id)]
                article.update_info(update_dict)
                upload_dict = article.get_upload_dict()
                Projects.update_article(self.token, int(article_id), upload_dict)

        else:
            article = self.main_window.articles[int(self.articles_ids[0])]
            article.update_info(update_dict)

            upload_dict = article.get_upload_dict()
            Projects.update_article(self.token, int(self.articles_ids[0]), upload_dict)

    def article_label_font(self):
        """
        Returns the font to use for label fields.
        :return: QFont.
        """
        window_size = self.geometry()
        s = window_size.height() / 20
        max_s = 14
        min_s = 10
        if s < min_s:
            s = min_s
        elif max_s < s:
            s = max_s
        lbl_font = QFont('SansSerif', s)
        lbl_font.setBold(True)

        return lbl_font

    def article_edit_font(self):
        """
        Returns the font to use for edit fields.
        :return: QFont.
        """
        window_size = self.geometry()
        s = window_size.height() / 25
        max_s = 12
        min_s = 7
        if s < min_s:
            s = min_s
        elif max_s < s:
            s = max_s
        edit_font = QFont('SansSerif', s)

        return edit_font

    def add_lineedit(self, layout, label, value, row=None, column=None, rowspan=None, columnspan=None):
        """
        Use this to add a QLabel, QLineEdit pair from the given values to the provided layout. If the layout is a
        QGridLayout then the row and column values are required.
        :param layout: QLayout to add widgets to.
        :param label: String to name the line edit field.
        :param value: String to fill the line edit field.
        Optional
        :param row: Grid row to add widgets from.
        :param column: Grid column to add widgets to.
        :param rowspan: Grid rows to span each widget.
        :param columnspan: Grid columns to span each widget.
        :return:
        """
        # Create the QLabel
        lbl = QLabel(label)
        lbl.setFont(self.label_font)
        # Create the QLineEdit
        edit = QLineEdit(value)
        edit.setFont(self.edit_font)

        if type(layout) is QGridLayout:
            if rowspan is not None and columnspan is not None:
                layout.addWidget(lbl, row, column, rowspan, columnspan)
                layout.addWidget(edit, row + rowspan + 1, column, rowspan, columnspan)
            else:
                layout.addWidget(lbl, row, column)
                layout.addWidget(edit, row + 1, column)

    def add_textedit(self, layout, label, value, row=None, column = None, rowspan=None, columnspan=None):
        """
        Use this to add a QLabel, QTextEdit pair from the given values to the provided layout. If the layout is a
        QGridLayout then the row and column values are required.
        :param layout: QLayout to add widgets to.
        :param label: String. Name for label.
        :param value: String. Text to fill QTextEdit with.
        Optional
        :param row: int. QGridLayout row from which to add widgets.
        :param column: int. QGridLayout column to add widgets to.
        :param rowspan: int. Number of rows to span widgets.
        :param columnspan: int. Number of columns to span widgets.
        :return:
        """
        # Create the QLabel
        lbl = QLabel(label)
        lbl.setFont(self.label_font)
        # Create the QLineEdit
        edit = QTextEdit(value)
        edit.setFont(self.edit_font)
        edit.setTabChangesFocus(True)

        if type(layout) is QGridLayout:
            if rowspan is not None and columnspan is not None:
                layout.addWidget(lbl, row, column, rowspan, columnspan)
                layout.addWidget(edit, row + rowspan + 1, column, rowspan, columnspan)
            else:
                layout.addWidget(lbl, row, column)
                layout.addWidget(edit, row + 1, column)

    def add_buttonlist(self, layout, label, values, key=None, row=None, column = None, rowspan=None,
                       columnspan=None):
        """
        Add an array of buttons to a layout that can be used to display arrays of data, e.g. tags or categories.
        The ability to add and remove items from the array is also added.
        :param layout: QLayout. Layout to add widgets to.
        :param label: String. Name of the field, e.g. tags, or categories.
        :param values: list. List of either strings or dictionary objects.
        Optional
        :param key: Dictionary Key. If the values given are in a dictionary object a dictionary key must also be provided.
        :param row: int. QGridLayout row from which to add widgets.
        :param column: int. QGridLayout column to add widgets to.
        :param rowspan: int. Number of rows to span widgets.
        :param columnspan: int. Number of columns to span widgets.
        :return:
        """
        # Create Qlabel for edit field.
        lbl = QLabel(label)
        lbl.setFont(self.label_font)
        # Create layout for buttons.
        hbox = QHBoxLayout()
        # Define a size policy for the buttons
        btn_sizePolicy = QSizePolicy
        btn_sizePolicy.setHorizontalPolicy(QSizePolicy.Expanding)
        btn_sizePolicy.setVerticalPolicy(QSizePolicy.Preferred)
        # Create a QButtonGroup
        btn_group = QButtonGroup()
        btn_group_id = 1
        # Create buttons and add to group and layout.
        list_element_type = type(values[0])
        if list_element_type is dict:
            for element in values:
                btn_str = str(element[key])
                btn = QPushButton(btn_str)
                btn.setFont(self.edit_font)
                btn.setFlat(True)
                btn.setSizePolicy(btn_sizePolicy)
                btn_group.addButton(btn, btn_group_id)
                hbox.addWidget(btn)
                btn_group_id += 1
        elif list_element_type is list:
            for element in values:
                btn_str = str(element)
                btn = QPushButton(btn_str)
                btn.setFont(self.edit_font)
                btn.setFlat(True)
                btn.setSizePolicy(btn_sizePolicy)
                btn_group.addButton(btn, btn_group_id)
                hbox.addWidget(btn)
                btn_group_id += 1

        new_btn = QLineEdit()
        new_btn.setFont(self.edit_font)
        new_btn.setSizePolicy(btn_sizePolicy)
        hbox.addWidget(new_btn)

        options_layout = QVBoxLayout()

        options_btn_size_policy = QSizePolicy()
        options_btn_size_policy.setHorizontalPolicy(QSizePolicy.Preferred)
        options_btn_size_policy.setVerticalPolicy(QSizePolicy.Expanding)

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/exit.png')))
        delete_btn.setSizePolicy(options_btn_size_policy)
        delete_btn.pressed.connect(lambda: self.on_delete_button_from_list(btn_group, hbox))
        options_layout.addWidget(delete_btn)

        add_btn = QPushButton()
        add_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Plus-50.png')))
        add_btn.setSizePolicy(options_btn_size_policy)
        add_btn.pressed.connect(lambda: self.on_add_button_to_list(btn_group, hbox, new_btn))
        options_layout.addWidget(add_btn)

        hbox.addLayout(options_layout)

        if type(layout) is QGridLayout:
            if rowspan is not None and columnspan is not None:
                layout.addWidget(lbl, row, column, rowspan, columnspan)
                layout.addLayout(hbox, row + rowspan + 1, column, rowspan, columnspan)
            else:
                layout.addWidget(lbl, row, column)
                layout.addLayout(hbox, row + 1, column)

    def on_delete_button_from_list(self, button_group, layout):
        """
        Removes a button from a layout and button group.
        :param button_group: QButtonGroup of button to be deleted.
        :param layout: QLayout button is in.
        :return:
        """
        btn_to_delete = button_group.checkedButton()

        button_group.removeButton(btn_to_delete)
        layout.removeWidget(btn_to_delete)

    def on_add_button_to_list(self, button_group, layout, lineedit):
        """
        Adds a buttn to a specified button group and layout.
        :param button_group: QButtonGroup button is to be added to.
        :param layout: QLayout button is to be added to.
        :param lineedit: QLineEdit containing the new button string.
        :return:
        """
        new_btn_str = lineedit.text()
        lineedit.clear()
        new_btn = QPushButton(new_btn_str)
        new_btn.setFont(self.edit_font)
        new_btn.setFlat(True)
        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        size_policy.setVerticalPolicy(QSizePolicy.Preferred)
        new_btn.setSizePolicy(size_policy)

        button_group.addButton(new_btn)
        inset_pos = layout.count() - 2
        layout.insertWidget(new_btn, inset_pos)
