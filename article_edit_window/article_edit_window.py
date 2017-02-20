"""

"""
import os
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTabWidget,
                             QGridLayout, QTextEdit, QLineEdit, QScrollArea, QButtonGroup, QComboBox)
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

    def __init__(self, app, OAuth_token, main_window, parent_window_loc, article_ids, project_id=None,
                 collection_id=None):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.main_window = main_window
        self.piw_loc = parent_window_loc

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
        self.button_groups = {}
        hbox = QHBoxLayout()
        self.tab_layout = QTabWidget()

        hbox.addLayout(self.confirmation_layout())

        self.basic_info_widget = self.basic_info_layout()

        self.decide_basic_layout(self.articles_ids)

        self.tab_layout.addTab(self.basic_info_widget, 'Figshare Metadata')

        self.file_specific_layout = self.decide_file_layout(self.articles_ids)
        if self.file_specific_layout is not None:
            self.tab_layout.addTab(self.file_specific_layout, 'File Metadata')

        hbox.addWidget(self.tab_layout)
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

        # Layout
        basic_info_widget = QWidget()
        vbox = QVBoxLayout(basic_info_widget)

        # Title
        self.add_lineedit(vbox, 'title', '')

        # Description
        self.add_textedit(vbox, 'description', '')

        # Tags
        self.add_buttonlist(vbox, 'tags', [''])

        # Categories
        self.add_buttonlist(vbox, 'categories', [''])

        # References
        self.add_buttonlist(vbox, 'references', [''])

        # Authors
        self.add_buttonlist(vbox, 'authors', [''])

        # Defined Type
        self.add_dropdownlist(vbox, 'defined_type', [''])

        # Funding Label
        self.add_textedit(vbox, 'funding', '')

        # License
        self.add_dropdownlist(vbox, 'license', [''])

        scroll_area = QScrollArea()
        scroll_area.setWidget(basic_info_widget)
        scroll_area.setWidgetResizable(True)



        return scroll_area

    def decide_basic_layout(self, article_ids):

        article = self.main_window.articles[int(article_ids[0])]
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

        tab_layout = self.tab_layout
        open_tab_index = tab_layout.currentIndex()

        if open_tab_index == 0:
            basic_info_dict = {}
            basic_info_layout = self.basic_info_widget.widget().layout()

            for widget_pos in range(0, basic_info_layout.count() - 1, 2):
                lbl = basic_info_layout.itemAt(widget_pos).widget().text()
                widget = basic_info_layout.itemAt(widget_pos + 1).widget()
                if widget is None:
                    widget = basic_info_layout.itemAt(widget_pos + 1).layout()

                widget_type = type(widget)
                if widget_type is QLineEdit:
                    if len(self.articles_ids) > 1:
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

        elif open_tab_index == 1:
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

                update_dict = {**file_specific_dict}

        if len(self.articles_ids) > 1:
            articles = self.main_window.articles
            for article_id in self.articles_ids:
                a_id = int(article_id)
                article = articles[a_id]
                article.update_info(update_dict)
                upload_dict = article.get_upload_dict()
                Projects.update_article(self.token, a_id, upload_dict)
                private_modified_date = Projects(self.token).get_article(self.project_id, a_id)['modified_date']
                article.figshare_metadata['modified_date'] = private_modified_date
                article.check_uptodate()
        else:
            a_id = int(self.articles_ids[0])
            article = self.main_window.articles[a_id]
            article.update_info(update_dict)
            upload_dict = article.get_upload_dict()
            Projects.update_article(self.token, a_id, upload_dict)
            private_modified_date = Projects(self.token).get_article(self.project_id, a_id)['modified_date']
            article.figshare_metadata['modified_date'] = private_modified_date
            article.check_uptodate()

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

        else:
            layout.addWidget(lbl)
            layout.addWidget(edit)

    def add_textedit(self, layout, label, value, row=None, column=None, rowspan=None, columnspan=None):
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
        else:
            layout.addWidget(lbl)
            layout.addWidget(edit)

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
        btn_sizePolicy = QSizePolicy()
        btn_sizePolicy.setHorizontalPolicy(QSizePolicy.Expanding)
        btn_sizePolicy.setVerticalPolicy(QSizePolicy.Preferred)
        # Create a QButtonGroup
        btn_group = QButtonGroup()
        self.button_groups[label] = btn_group
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
                btn.setSizePolicy(btn_sizePolicy)
                btn_group.addButton(btn, btn_group_id)
                hbox.addWidget(btn)
                btn_group_id += 1

        txt_sizePolicy = QSizePolicy()
        txt_sizePolicy.setVerticalPolicy(QSizePolicy.Preferred)
        txt_sizePolicy.setHorizontalPolicy(QSizePolicy.Preferred)

        new_btn = QTextEdit()
        new_btn.setFont(self.edit_font)
        new_btn.setSizePolicy(txt_sizePolicy)
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
        else:
            layout.addWidget(lbl)
            layout.addLayout(hbox)

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
        btn_to_delete.deleteLater()

    def on_add_button_to_list(self, button_group, layout, textedit, overide_str=None):
        """
        Adds a button to a specified button group and layout.
        :param button_group: QButtonGroup button is to be added to.
        :param layout: QLayout button is to be added to.
        :param lineedit: QLineEdit containing the new button string.
        :return:
        """
        if overide_str is not None:
            new_btn_str = overide_str
        else:
            new_btn_str = textedit.toPlainText()
            textedit.clear()
        new_btn = QPushButton(new_btn_str)
        new_btn.setFont(self.edit_font)
        new_btn.setFlat(True)
        new_btn.setCheckable(True)
        new_btn.toggle()
        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        size_policy.setVerticalPolicy(QSizePolicy.Preferred)
        new_btn.setSizePolicy(size_policy)

        button_group.addButton(new_btn)
        inset_pos = layout.count() - 2
        layout.insertWidget(inset_pos, new_btn)

    def add_dropdownlist(self, layout, label, values, row=None, column=None, rowspan=None, columnspan=None):
        """
        Adds a drop down list to the given layout.
        :param layout: QLayout to add widget to.
        :param label: String containing the list title.
        :param values: List containing dropdown items.
        Optional
        :param row: int. If layout is a QGridLayout then the row must be given.
        :param column: int. If the layout is a QGridLayout then the column must be given.
        :param rowspan: int. For how many rows widget will span in QGridLayout.
        :param columnspan: int. For how many columns widget will span in QGridLayout.
        :return:
        """
        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        size_policy.setVerticalPolicy(QSizePolicy.Preferred)

        lbl = QLabel(label)
        lbl.setFont(self.label_font)
        lbl.setSizePolicy(size_policy)

        drop_menu = QComboBox()
        drop_menu.addItems(values)
        drop_menu.setFont(self.edit_font)
        drop_menu.setSizePolicy(size_policy)

        if type(layout) is QGridLayout:
            if rowspan is not None and columnspan is not None:
                layout.addWidget(lbl, row, column, rowspan, columnspan)
                layout.addWidget(drop_menu, row + rowspan + 1, column, rowspan, columnspan)
            else:
                layout.addWidget(lbl, row, column)
                layout.addWidget(drop_menu, row + 1, column)
        else:
            layout.addWidget(lbl)
            layout.addWidget(drop_menu)
