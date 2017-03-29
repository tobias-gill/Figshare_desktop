"""

"""

import os
import math
from requests import HTTPError

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QMainWindow, QMdiSubWindow,
                             QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor)
from PyQt5.QtCore import (Qt, QPoint)

from Figshare_desktop.custom_widgets.button_field import QButtonField

from Figshare_desktop.formatting.formatting import (grid_label, grid_edit, checkable_button)

from Figshare_desktop.projects_windows.articles_window import ProjectsArticlesWindow

from figshare_interface import (Groups, Projects)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ProjectInfoWindow(QMdiSubWindow):

    def __init__(self, app, OAuth_token, parent, project_id):
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.project_id = project_id

        self.open_windows = self.parent.open_windows

        self.initFig(self.project_id)
        self.initUI()

    def initFig(self, project_id):
        """
        Initilizes Fighsare information for the given project
        :return:
        """
        projects = Projects(self.token)
        self.project_info = projects.get_info(project_id)

    def initUI(self):
        """
        Initilizes the GUI
        :return:
        """

        self.format_window()

        # Create a Horizontal and Vertical Box layout
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        # Add the title to the vertical layout
        self.vbox.addLayout(self.title_hbox())

        # Create a vertical layout for the save and articles buttons
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.save_changes_button())
        self.buttons_layout.addWidget(self.articles_button())

        # Add the Buttons Layout to the horizontal layout
        self.hbox.addLayout(self.buttons_layout)
        # Add the description layout to the horizontal layout
        self.hbox.addLayout(self.description_vbox())
        # Add a separator to the horizontal layout
        self.hbox.addWidget(self.seperator())
        # Add the project info grid to the horizontal layout
        self.hbox.addLayout(self.info_grid())

        # Add the horizontal layout to the vertical layout
        self.vbox.addLayout(self.hbox)

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(self.vbox)
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
        h = ((geom.height() - y0) / 3)
        self.setGeometry(x0, y0, w, h)
        # Remove frame from the window
        self.setWindowFlags(Qt.FramelessWindowHint)

    #####
    # Window Widgets
    #####

    def articles_button(self):
        """
        Creates a click button to open and close the project articles window
        :return: QPushButton
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Magazine-50.png')))
        checkable_button(self.app, btn)
        btn.setMaximumWidth(self.geometry().width() / 20)
        btn.setMinimumWidth(self.geometry().width() / 20)
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        btn.setToolTip('Open Project Articles Window')
        #btn.setToolTipDuration(1)
        #btn.clicked[bool].connect()
        return btn

    def save_changes_button(self):
        """
        Creates a save changes button to push edits to Figshare
        :return: QMessageWindow
        """
        btn = QPushButton()
        btn.setIcon(QIcon(os.path.abspath(__file__ + '/../../img/figshare_upload.png')))
        btn.setMaximumWidth(self.geometry().width() / 20)
        btn.setMinimumWidth(self.geometry().width() / 20)
        btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        btn.setToolTip('Save Changes to Figshare')
        #btn.setToolTipDuration(1)
        btn.pressed.connect(self.on_save_pressed)
        return btn

    def create_label(self, label):
        """
        Creates a QLabel with a default formatting
        :param label: String to be displayed in the label
        :return: QLabel
        """
        lbl = QLabel(label)
        grid_label(self.app, lbl)
        return lbl

    def create_lineedit(self):
        """
        Creates a QLineEdit with a default formatting
        :return: QLineEdit
        """
        edit = QLineEdit()
        grid_edit(self.app, edit)
        return edit

    def create_textedit(self):
        """
        Creates a QTextEdit with a default formatting
        :return: QTextEdit
        """
        edit = QTextEdit()
        grid_edit(self.app, edit)
        return edit

    def title_hbox(self):
        """
        Creates a Horizontal box layout containing the title lineedit and an edit button
        :return: QHBoxLayout
        """
        # Create Edit/Label
        title = self.project_info['title']
        title_edit = QLineEdit(title)
        grid_label(self.app, title_edit)
        title_edit.setEnabled(False)
        self.title_wid = title_edit

        # Create Edit Button
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        edit_btn.setMaximumWidth(self.geometry().width() / 50)
        edit_btn.setMaximumHeight(self.geometry().width() / 50)
        checkable_button(self.app, edit_btn)

        # Add an action to the edit button
        edit_btn.clicked[bool].connect(lambda: self.on_edit_pressed(title_edit))

        # Create Layout
        hbox = QHBoxLayout()
        hbox.addWidget(title_edit)
        hbox.addWidget(edit_btn)

        return hbox

    def description_vbox(self):
        """
        Creates a Vertical box layour containing the description label and edit button and a textedit field
        :return: QVBoxLayout
        """

        # Create the Description Label
        lbl = self.create_label('Description')
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Create Edit Button
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Pencil-52.png')))
        edit_btn.setMaximumWidth(self.geometry().width() / 50)
        edit_btn.setMaximumHeight(self.geometry().width() / 50)
        checkable_button(self.app, edit_btn)

        # Create TextEdit
        description = self.project_info['description']
        text_edit = QTextEdit()
        if description is not None and description != '':
            text_edit.setText(description)
        grid_edit(self.app, text_edit)
        text_edit.setEnabled(False)
        self.desc_wid = text_edit

        # Add an action to the edit button
        edit_btn.clicked[bool].connect(lambda: self.on_edit_pressed(text_edit))

        # Create a horizontal layout for the label and edit button
        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(edit_btn)

        # Create a Vertical layout to hold the label layout and the edit field
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(text_edit)

        return vbox

    def seperator(self):
        """
        Creates a vertical sepearator.
        :return: QFrame
        """

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        return sep


    def info_grid(self):
        """
        Creates a grid layout containing more details on the project
        :return: QGridlayout
        """

        # Create Labels

        # Project ID Label
        id_lbl = QLabel('Project ID')
        grid_label(self.app, id_lbl)

        # Published Label
        pub_lbl = QLabel('Published')
        grid_label(self.app, pub_lbl)

        # Collaborators Label
        col_lbl = QLabel('Collaborators')
        grid_label(self.app, col_lbl)

        # Funding Label
        fund_lbl = QLabel('Funding')
        grid_label(self.app, fund_lbl)

        # Group Label
        group_lbl = QLabel('Group')
        grid_label(self.app, group_lbl)

        # Storage Label
        stor_lbl = QLabel('Storage')
        grid_label(self.app, stor_lbl)

        # Create Edit Fields

        # Project ID Field
        id_field = QLabel()
        grid_edit(self.app, id_field)
        id_field.setText(str(self.project_info['id']))

        # Published Field
        published_date = self.project_info['published_date']
        if published_date is None:
            published_date = 'Private'
        pub_field = QLabel()
        pub_field.setText(published_date)

        # Collaborators Field
        collaborators = self.project_info['collaborators']
        col_field = QButtonField()
        if collaborators is not None:
            for col in collaborators:
                name = col['name']
                user_id = col['user_id']
                tag = "{}: {}".format(name, user_id)
                col_field.add_tag(tag)
        self.col_wid = col_field

        # Funding Field
        funding = self.project_info['funding']
        funding_field = QButtonField()
        if funding != '':
            for funder in funding.split(':_:'):
                if funder != '':
                    funding_field.add_tag(funder)
        self.fund_wid = funding_field

        # Group Field
        group_id = self.project_info['group_id']
        group_field = QLabel()
        grid_label(self.app, group_field)
        if group_id != 0:
            group_field.setText(str(group_id))
        else:
            group_field.setText('Private Project')

        # Storage Field
        quota_text = self.get_quota_percentage()
        storage_field = QLabel(quota_text)
        grid_label(self.app, storage_field)


        # Create and Populate grid
        grid = QGridLayout()

        grid.addWidget(id_lbl, 0, 0)
        grid.addWidget(id_field, 0, 1)

        grid.addWidget(pub_lbl, 1, 0)
        grid.addWidget(pub_field, 1, 1)

        grid.addWidget(col_lbl, 2, 0)
        grid.addWidget(col_field, 2, 1)

        grid.addWidget(fund_lbl, 3, 0)
        grid.addWidget(funding_field, 3, 1)

        grid.addWidget(group_lbl, 4, 0)
        grid.addWidget(group_lbl, 4, 1)

        grid.addWidget(stor_lbl, 5, 0)
        grid.addWidget(storage_field, 5, 1)

        return grid

    def get_quota_percentage(self):
        """
        Returns a string containg the current percentage of the figshare quota used for a given project
        :return:
        """

        group_id = self.project_info['group_id']
        quota = self.project_info['quota']
        if group_id != 0:
            used_quota = self.project_info['used_quota_public']
        else:
            used_quota = self.project_info['used_quota_private']

        if quota != 0:
            quota_percentage = round(100 * used_quota / quota, 2)
        else:
            quota_percentage = 0

        quota_gb = round(quota / (10**9), 1)

        return "{} % of {} GB".format(quota_percentage, quota_gb)

    #####
    # Widget Actions
    #####

    def on_edit_pressed(self, edit_field):
        """
        Called when a edit button is pressed. This will activate or deactivate the passed edit field
        :param edit_field: QLineEdit or QTextEdit
        :return:
        """

        if edit_field.isEnabled():
            edit_field.setEnabled(False)
        else:
            edit_field.setEnabled(True)

    def on_save_pressed(self):
        """
        Called when the save button is pressed.
        :return:
        """
        # Empty dictionary to hold update information
        update_dict = {}
        collaborators_list = []

        # Check to see if there has been a change to the title
        old_title = self.project_info['title']
        new_title = self.title_wid.text()
        if old_title != new_title:
            update_dict['title'] = new_title

        # Check to see if there has been a change to the description
        old_desc = self.project_info['description']
        new_desc = self.desc_wid.toPlainText()
        if old_desc != new_desc:
            update_dict['description'] = new_desc

        # Check to see if there has been a change to the collaborators
        old_col = self.project_info['collaborators']
        old_col_ids = [col['user_id'] for col in old_col]
        col_tags = self.col_wid.get_tags()
        new_col = []
        for tag in col_tags:
            value = tag.split(':')
            if len(value) > 1:
                key, value = tag.split(':')
            else:
                value = value[0]
            if value[0] == ' ':
                value = value[1:]
            try:
                value = int(value)
                key = 'user_id'
            except:
                key = 'email'
            new_col.append({key: value})
        for col in new_col:
            if 'user_id' in col:
                if col['user_id'] not in old_col_ids:
                    collaborators_list.append(col)
            elif 'email' in col:
                collaborators_list.append(col)

        # Check to see if there has been a change to the funding
        old_fund = self.project_info['funding']
        fund_tags = self.fund_wid.get_tags()
        new_fund = ''
        for tag in fund_tags:
            new_fund += ':_:{}'.format(tag)
        if old_fund != new_fund:
            update_dict['funding'] = new_fund

        # Call Figshare API Interface functions
        successful = self.update_project(self.project_id, self.token, update_dict)

        if collaborators_list is not None:
            print('need to update collaborators')
            successful = self.invite_collaborators(self.project_id, self.token, collaborators_list)

        if successful is True:
            resp = QMessageBox.information(self, 'Update Confirmation', 'Project successfully updated',
                                           QMessageBox.Ok)

            if resp == QMessageBox.Ok:
                self.reopen_project_info()
            else:
                self.reopen_project_info()
        else:
            resp = QMessageBox.warning(self, 'Update Confirmation',
                                       'Error occurred.\nProject may not have updated.\n{}'.format(successful.args),
                                       QMessageBox.Ok)

            if resp == QMessageBox.Ok:
                self.reopen_project_info()
            else:
                self.reopen_project_info()

    def reopen_project_info(self):
        """
        Closes and reopens the current project info window.
        :return:
        """
        for i in range(2):
            self.parent.projects_window.on_project_pressed(self.project_id)

    #####
    # Figshare API Interface Actions
    #####

    def update_project(self, project_id, token, update_dict):
        """
        Uploads changes to a figshare project
        :param project_id: int. Figshare project id number
        :param token: OAuth token
        :param update_dict: dict. Dictionary holding named arguments to pass to Projects.update()
        :return:
        """
        try:
            projects = Projects(token)
            info = projects.update(project_id, **update_dict)
            return True
        except TypeError as err:
            return err
        except ValueError as err:
            return err
        except HTTPError as err:
            return err

    def invite_collaborators(self, project_id, token, collaborators):
        """

        :param project_id:
        :param token:
        :param collaborators:
        :return:
        """
        for col in collaborators:
            col['role_name'] = 'collaborator'

        try:
            projects = Projects(token)
            for col in collaborators:
                info = projects.invite(project_id, col)
                print(info)
            return True
        except TypeError as err:
            return err
        except ValueError as err:
            return err
        except HTTPError as err:
            print(err.args)
            return err
