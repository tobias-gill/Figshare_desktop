"""

"""

import os
import math
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QMessageBox, QMainWindow,
                             QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QObject)

from ..formatting.formatting import (scaling_ratio, checkable_button, search_bar)
from Figshare_desktop.projects_windows.new_project_window import NewProjectWindow
from Figshare_desktop.projects_windows.project_info_window import ProjectInfoWindow

from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ProjectsWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.open_windows = self.parent.open_windows

        self.initFig()
        self.initUI()

    def initFig(self):
        """
        Initialize Figshare information
        """
        self.project_list = self.get_project_list(self.token)

    def initUI(self):

        self.format_window()

        # Create a horizontal box layout to hold the project buttons
        self.project_buttons_box = QHBoxLayout()
        # Create a vertical box layout to hold the project window widgets and layouts
        self.vbox = QVBoxLayout()

        # Add the Projects button to the vertical box layout
        init_finish = len(self.project_list)
        if init_finish > 4:
            init_finish = 4
        self.create_project_bar(0, init_finish)
        self.vbox.addLayout(self.project_buttons_box)

        # Add the scroll bar to the vertical box layout
        self.s_bar = self.scroll_bar()
        self.vbox.addWidget(self.s_bar)

        self.hbox = QHBoxLayout()
        temp = QVBoxLayout()
        temp.addWidget(self.search_bar())
        temp.addLayout(self.management_buttons())
        self.hbox.addLayout(temp)
        self.hbox.addLayout(self.vbox)

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(self.hbox)
        # Set the projects window widget
        self.setWidget(window_widget)

    #####
    # Window Formatting
    #####

    def format_window(self):
        """
        Formats the Projects window
        """
        # Gets the QRect of the main window
        geom = self.parent.geometry()
        # Gets the Qrect of the sections window
        section_geom = self.parent.section_geom

        # Define geometries for the projects window
        x0 = section_geom.x() + section_geom.width()
        y0 = section_geom.y()
        w = geom.width() - x0
        h = ((geom.height() - y0) / 6)
        self.setGeometry(x0, y0, w, h)
        # Remove frame from projects window
        self.setWindowFlags(Qt.FramelessWindowHint)

    #####
    # Window Widgets
    #####

    def scroll_bar(self):
        """
        Creates a scroll bar set to the size of the projects list
        :return: QScrollBar Object
        """
        s_bar = QScrollBar(Qt.Horizontal)
        s_bar.setMaximum(len(self.project_list) - 4)
        s_bar.sliderMoved.connect(self.slider_val)
        s_bar.valueChanged.connect(self.slider_val)
        return s_bar

    def create_proj_thumb(self, title, published_date, project_id):
        """
        Creates a large pushbutton for a project
        :param title: string. Project title
        :param published_date: string. project published date
        :param id: int. figshare project id number
        :return: QPushButton object
        """
        geom = self.geometry()

        # Get the scalig ratios for the current window
        w_ratio, f_ratio = scaling_ratio(self.app)
        # Scale the font sizes
        title_fnt_size = 12 * f_ratio
        date_ftn_size = 8 * f_ratio

        # Create the title label
        title_lbl = QLabel()
        title_lbl.setText("{}".format(title))
        title_lbl_fnt = QFont('SansSerif', title_fnt_size)
        title_lbl_fnt.setBold(True)
        title_lbl.setFont(title_lbl_fnt)
        title_lbl.setWordWrap(True)

        # Create the date label
        date_lbl = QLabel()
        if published_date is None:
            published_date = 'Private'
        date_lbl.setText("Published: {}".format(published_date))
        date_lbl_fnt = QFont('SansSerif', date_ftn_size)
        date_lbl.setFont(date_lbl_fnt)
        date_lbl.setStyleSheet('color: gray')
        date_lbl.setWordWrap(True)

        # Create a layout to hold the labels
        lbl_box = QVBoxLayout()
        # Add labels to layout
        lbl_box.addWidget(title_lbl)
        lbl_box.addWidget(date_lbl)

        # Create a button for the project
        btn = QPushButton(self)
        checkable_button(self.app, btn)
        btn.setLayout(lbl_box)
        btn.clicked[bool].connect(lambda: self.on_project_pressed(project_id))

        self.project_buttons_box.addWidget(btn)

    def create_project_bar(self, start, finish):
        """
        Creates a series of Project push buttons
        :param start: start position in projects list
        :param finish: finish position in projects list
        """
        self.buttons = {}
        i = 0
        for project_pos in range(start, finish):
            title = self.project_list[project_pos]['title']
            pub_date = self.project_list[project_pos]['published_date']
            project_id = self.project_list[project_pos]['id']
            self.create_proj_thumb(title, pub_date, project_id)
            self.buttons[project_id] = self.project_buttons_box.itemAt(i).widget()
            i += 1

    def management_buttons(self):
        """
        Creates a layout that holds buttons to be used for creating and deleting projects
        :return: QVBoxLayout holding the create, and delete projects buttons
        """

        # Create New Project Button
        np_btn = QPushButton()
        np_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        np_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Folder-48.png')))
        np_btn.setToolTip('Create a new Figshare Project')
        np_btn.setToolTipDuration(1)
        np_btn.pressed.connect(self.on_projects_btn_pressed)

        # Create Delete Project Button
        del_btn = QPushButton()
        del_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        del_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/del_folder.png')))
        del_btn.setToolTip('Delete Selected Project')
        del_btn.setToolTipDuration(1)
        del_btn.pressed.connect(self.on_delete_btn_pressed)

        # Create layout to hold buttons
        hbox = QHBoxLayout()
        # Add Buttons to layout
        hbox.addWidget(np_btn)
        hbox.addWidget(del_btn)

        return hbox

    def search_bar(self):
        """
        Creates a QLineEdit object for the user to enter a search query
        :return: Edits the projects list object according to the filter
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
        edit.returnPressed.connect(lambda: self.search_on_return(edit.text()))
        edit.textChanged.connect(lambda: self.search_on_clear(edit.text()))
        return edit

    #####
    # Widget Actions
    #####

    def slider_val(self):
        """
        Called when the projects button slider is changed.
        Removes all existing buttons and regenerates from the new position
        :return:
        """
        while self.project_buttons_box.count():
            item = self.project_buttons_box.takeAt(0)
            item.widget().deleteLater()

        s_bar_pos = self.s_bar.value()

        if 1 < len(self.project_list) < 4:
            number = len(self.project_list)
        else:
            number = 4
        self.s_bar.setMaximum(len(self.project_list) - number)

        self.create_project_bar(s_bar_pos, s_bar_pos + number)

    def search_init(self):
        """
        Called when the projects search bar is used.
        Removes all existing buttons and regenerates from new projects list
        :return:
        """
        while self.project_buttons_box.count():
            item = self.project_buttons_box.takeAt(0)
            item.widget().deleteLater()

        if 1 <= len(self.project_list) <= 4:
            number = len(self.project_list)
        else:
            number = 4

        self.s_bar.setMaximum(len(self.project_list) - number)

        self.create_project_bar(0, number)

    def search_on_return(self, search_text):
        """
        Called when return is pressed in the search bar.
        :return:
        """
        if search_text != '':
            self.project_list = self.search_projects(search_text, self.token)
            self.search_init()

    def search_on_clear(self, lineedit_text):
        """
        Called when the search bar is cleared
        :return:
        """
        if lineedit_text == '':
            self.project_list = self.get_project_list(self.token)
            self.slider_val()

    def on_projects_btn_pressed(self):
        """
        Called when the create new project button is pressed
        """
        if 'new_project_window' in self.open_windows:
            self.open_windows.remove('new_project_window')
            self.parent.new_project_window.close()
        else:
            self.open_windows.remove('projects_window')
            self.close()

            if 'project_info_window' in self.open_windows:
                self.parent.project_info_window.close()
                self.open_windows.remove('project_info_window')
            if 'project_articles_window' in self.open_windows:
                self.parent.project_articles_window.close()
                self.open_windows.remove('project_articles_window')
            if 'article_edit_window' in self.open_windows:
                self.open_windows.remove('article_edit_window')
                self.parent.article_edit_window.close()

            self.open_windows.add('new_project_window')
            self.parent.new_project_window = NewProjectWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.new_project_window)
            self.parent.new_project_window.show()

    def on_project_pressed(self, project_id):
        """
        Called when a project is clicked.
        :return:
        """
        # For if there is already a project info window open
        if 'project_info_window' in self.open_windows:
            # Get the project id number of the current window
            open_proj = self.parent.project_info_window.project_id

            # For a different project than the currently open project
            if open_proj != project_id:
                # If the current project is in the current view of project buttons (it may have been scrolled away from)
                if open_proj in self.buttons:
                    # If that button is checked, uncheck it
                    if self.buttons[open_proj].isChecked():
                        self.buttons[open_proj].toggle()
                # Close the currently open project info window
                self.parent.project_info_window.close()
                # Create a new project info window for the different project
                self.parent.project_info_window = ProjectInfoWindow(self.app, self.token, self.parent, project_id)
                # Add it as a sub window to the framing window
                self.parent.mdi.addSubWindow(self.parent.project_info_window)
                self.parent.project_info_window.show()

            # If the current projects button is pressed
            else:
                # Close the window and remove from the open window list
                self.open_windows.remove('project_info_window')
                self.parent.project_info_window.close()

            # If any sub windows are open close them as well
            if 'project_articles_window' in self.open_windows:
                self.open_windows.remove('project_articles_window')
                self.parent.project_articles_window.close()
            if 'article_edit_window' in self.open_windows:
                self.open_windows.remove('article_edit_window')
                self.parent.article_edit_window.close()

        # For when no project info window is open
        else:
            self.open_windows.add('project_info_window')
            self.parent.project_info_window = ProjectInfoWindow(self.app, self.token, self.parent, project_id)
            self.parent.mdi.addSubWindow(self.parent.project_info_window)
            self.parent.project_info_window.show()

    def on_delete_btn_pressed(self):
        """
        Called when the project delete button is pressed/
        :return:
        """
        open_proj = self.parent.project_info_window.project_id
        project_title = self.parent.project_info_window.project_info['title']

        msg = "Are you sure you want to delete Figshare Project: {}".format(project_title)
        msg_box = QMessageBox.question(self, 'Message', msg, QMessageBox.Yes, QMessageBox.No)

        if msg_box == QMessageBox.Yes:
            successful = self.delete_project(self.token, open_proj)

            if successful:
                con_reply = QMessageBox.information(self, 'Deletion Confirmation', 'Project successfully deleted',
                                                    QMessageBox.Ok)
                if con_reply == QMessageBox.Ok:
                    self.reopen_projects()
                else:
                    self.reopen_projects()
            else:
                con_reply = QMessageBox.warning(self, 'Deletion Confirmation',
                                                'Unknown error occurred.\n Project may not have been deleted.',
                                                QMessageBox.Ok)
                if con_reply == QMessageBox.Ok:
                    self.reopen_projects()
                else:
                    self.reopen_projects()

    def reopen_projects(self):
        """
        Called to open and close the projects window.
        :return:
        """
        for i in range(2):
            self.parent.section_window.on_projects_btn_pressed()


    #####
    # Figshare API Interface Calls
    #####

    def get_project_list(self, token):
        """
        Returns the users private project list
        :param token: Figshare OAuth token
        :return: array of project
        """
        projects = Projects(token)
        return projects.get_list()

    def search_projects(self, search_text, token):
        """
        Returns a list of projects matching the users search criteria
        :param search_text: String. Figshare style elastic search string
        :param token: Figshare OAuth token
        :return:
        """
        projects = Projects(token)

        result = projects.search(search_text)
        if len(result) == 0:
            result = projects.get_list()

        return result

    def delete_project(self, token, project_id):
        """
        Deletes the given project from Figshare
        :param token:
        :param project_id: Int. Figshare project ID number
        :return:
        """
        projects = Projects(token)
        try:
            projects.delete(project_id, safe=False)  # Suppresses command line requirement for acknowledgement
            return True
        except:
            return False

