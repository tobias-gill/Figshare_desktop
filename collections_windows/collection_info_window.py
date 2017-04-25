"""
Collection Info Window

This window gives an overview of the metadata associated with a given Figshare Collection.

ToDo:
    * Abstract project info window, then sub class to here.
"""

# Standard Imports
from requests import HTTPError

# PyQt Imports
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QMessageBox)

# Figshare Desktop Imports
from Figshare_desktop.abstract_windows.object_info_window import ObjectInfoWindow
from Figshare_desktop.collections_windows.collection_articles_window import CollectionsArticlesWindow
from Figshare_desktop.custom_widgets.button_field import QButtonField

# Figshare API imports
from figshare_interface.figshare_structures.collections import Collections

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class CollectionInfoWindow(ObjectInfoWindow):
    """
    Creates a window to view the information of a given Figshare collection.
    """

    def initFig(self):
        """
        Get information on the given collection from Figshare.
        Args:

        Returns:
            object_info (dict): Dictionary containing key, value pairs of metadata on the collection.
        """
        collections = Collections(self.token)
        object_info = collections.get_info(self.object_id)
        return object_info

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
        self.vbox.addLayout(self.title_hbox(self.object_info['title']))

        # Create a vertical layout for the save and articles buttons
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.save_changes_button())
        self.buttons_layout.addWidget(self.articles_button())

        # Add the Buttons Layout to the horizontal layout
        self.hbox.addLayout(self.buttons_layout)
        # Add the description layout to the horizontal layout
        self.hbox.addLayout(self.textedit_vbox('Description', self.object_info['description']))
        # Add a separator to the horizontal layout
        self.hbox.addWidget(self.v_separator())
        # Add the project info grid to the horizontal layout
        self.hbox.addWidget(self.info_grid())

        # Add the horizontal layout to the vertical layout
        self.vbox.addLayout(self.hbox)

        # Create a central widget for the projects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(self.vbox)
        # Set the projects window widget
        self.setWidget(window_widget)

    # Window Widgets
    # ==============

    def info_grid(self):
        """
        Creates a grid layout with detailed information on the collection.
        Returns:
            grid (QGridLayout): Layout containing all the information fields and labels.
        """
        scroll_area = QScrollArea()
        grid = QGridLayout()
        scroll_area.setMaximumWidth(self.geometry().width() * 0.5)
        scroll_area.setMinimumWidth(self.geometry().width() * 0.5)

        # Create Labels
        # -------------

        # Collection ID Label
        id_lbl = self.create_label('Collection ID')

        # Published Label
        pub_lbl = self.create_label('Published')

        # Version Label
        ver_lbl = self.create_label('Version')

        # Group Label
        group_lbl = self.create_label('Group')

        # Authors Label
        auth_lbl = self.create_label('Authors')

        # Categories Label
        cat_lbl = self.create_label('Categories')

        # Tags Label
        tag_lbl = self.create_label('Tags')

        # References Label
        ref_lbl = self.create_label('References')

        # Article Count Label
        count_lbl = self.create_label('Article Count')

        # Citation Label
        cit_lbl = self.create_label('Citation')

        # Create Edit Fields
        # ------------------

        # Collection ID Field
        id_field = self.create_label(str(self.object_id))

        # Published Field
        published_date = self.object_info['published_date']
        if published_date is None:
            published_date = 'Private'
        pub_field = self.create_label(published_date)

        # Version Field
        ver_field = self.create_label("v{}".format(self.object_info['version']))

        # Group Field
        group_field = self.create_label(str(self.object_info['group_id']))

        # Authors Field
        auth_field = QButtonField(scroll_area)
        for auth_dict in self.object_info['authors']:
            auth_name = auth_dict['full_name']
            auth_id = str(auth_dict['id'])
            auth_field.add_tag(auth_name, auth_id)
        self.auth_field = auth_field

        # Categories Field
        cat_field = QButtonField(scroll_area)
        for cat in self.object_info['categories']:
            if cat['id'] in self.parent.categories:
                cat_name = cat['title']
                cat_id = str(cat['id'])
                cat_field.add_tag(cat_name, cat_id)
        self.cat_field = cat_field

        # Tags Field
        tag_field = QButtonField(scroll_area)
        for tag in self.object_info['tags']:
            tag_field.add_tag(tag)
        self.tag_field = tag_field

        # References Field
        ref_field = QButtonField(scroll_area)
        for ref in self.object_info['references']:
            ref_field.add_tag(ref)
        self.ref_field = ref_field

        # Article Count Field
        article_field = self.create_label(str(self.object_info['articles_count']))

        # Citation Field
        citation_field = self.create_label(self.object_info['citation'])

        # Create Grid
        # -----------

        grid.addWidget(id_lbl, 0, 0)
        grid.addWidget(id_field, 0, 1)

        grid.addWidget(pub_lbl, 0, 2)
        grid.addWidget(pub_field, 0, 3)

        grid.addWidget(group_lbl, 1, 0)
        grid.addWidget(group_field, 1, 1)

        grid.addWidget(ver_lbl, 1, 2)
        grid.addWidget(ver_field, 1, 3)

        grid.addWidget(auth_lbl, 2, 0)
        grid.addWidget(auth_field, 2, 1, 1, 3)

        grid.addWidget(cat_lbl, 3, 0)
        grid.addWidget(cat_field, 3, 1, 1, 3)

        grid.addWidget(tag_lbl, 4, 0)
        grid.addWidget(tag_field, 4, 1, 1, 3)

        grid.addWidget(ref_lbl, 5, 0)
        grid.addWidget(ref_field, 5, 1, 1, 3)

        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        scroll_area.setWidget(grid_widget)

        return scroll_area

    # Widget Actions
    # ==============

    def on_save_pressed(self):
        """
        Called when the save button is pressed.
        :return:
        """
        update_dict = {}

        # Check Title
        current_title = self.object_info['title']
        new_title = self.title_wid.text()
        if new_title != current_title:
            update_dict['title'] = new_title

        # Check Description
        current_description = self.object_info['description']
        new_description = self.desc_wid.toPlainText()
        if new_description != current_description:
            update_dict['description'] = new_description

        # Check Authors
        current_authors = self.object_info['authors']
        author_tags = self.auth_field.get_tags()
        new_authors = []
        for tag in author_tags:

            # Attempt to convert the tag into an integer
            try:
                tag = int(tag)
                new_auth = True
                # Check to see if author ID is already in list
                for auth in current_authors:
                    if auth['id'] == tag:
                        new_auth = False
                        break

                # If a new author add it to the update list
                if new_auth:
                    new_authors.append({'id': tag})
            except:
                new_auth = True

                # Check to see if the author name is already in the list
                for auth in current_authors:
                    if auth['full_name'] == tag:
                        new_auth = False
                        break

                # If a new author add it to the update list
                if new_auth:
                    new_authors.append({'name': tag})

        if new_authors != []:
            update_dict['authors'] = new_authors

        # Check Categories
        current_categories = self.object_info['categories']
        categories = self.cat_field.get_tags()
        new_categories = []
        for cat in categories:
            try:
                cat = int(cat)
                new_categories.append(cat)
            except:
                for cat_id, cat_name in self.parent.categories.items():
                    if cat_name == cat:
                        new_categories.append(cat_id)
                        break
        if new_categories != []:
            update_dict['categories'] = new_categories

        # Check Tags
        current_tags = self.object_info['tags']
        new_tags = self.tag_field.get_tags()
        if new_tags != current_tags:
            update_dict['tags'] = new_tags

        # Check References
        current_references = self.object_info['references']
        new_references = self.ref_field.get_tags()
        if new_references != current_references:
            update_dict['references'] = new_references

        # Update Collection
        if update_dict != {}:
            resp_code, resp_data = self.update_object(update_dict)

            if resp_code != 205:
                self.error_message_box(resp_data)
            else:
                self.success_message_box()

    def success_message_box(self):
        """
        Creates an message dialog box to confirm a successful update.
        Returns:

        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText('Updated collection: \n{}'.format(self.object_info['title']))
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msg_box))
        msg_box.show()

    def error_message_box(self, errors):
        """
        Creates an error message dialog box for errors raised during an update.
        Args:
            errors: list of errors.

        Returns:

        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("Errors in updating Collection:\n{}".format(self.object_info['title']))
        detailed_msg = ""
        for err in errors:
            detailed_msg += "{code}: {msg}\n\n".format(code=err[0], msg=err[1])
        msg_box.setDetailedText(detailed_msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msg_box))
        msg_box.show()

    def reopen_object_window(self):
        """
        Called to close and reopen the collection info window.
        Returns:

        """
        for i in range(2):
            self.parent.section_window.on_collections_btn_pressed()
        self.parent.collections_window.on_object_pressed(self.object_id)

    def on_articles_pressed(self):
        """
        Called when the articles button is pressed. This will open or close the articles window.

        Returns:

        """
        if 'collection_articles_window' in self.open_windows:
            self.open_windows.remove('collection_articles_window')
            self.parent.collection_articles_window.close()
        elif 'article_edit_window' in self.open_windows:
            self.open_windows.remove('article_edit_window')
            self.parent.article_edit_window.close()
        else:
            self.open_windows.add('collection_articles_window')
            self.parent.collection_articles_window = CollectionsArticlesWindow(self.app, self.token, self.parent,
                                                                               self.object_id)
            self.parent.mdi.addSubWindow(self.parent.collection_articles_window)
            self.parent.collection_articles_window.show()

    # Figshare API Functions
    # ======================

    def update_object(self, update_dict: dict):
        """
        Uploads changes to the Figshare object.
        Args:
            object_id: Figshare object ID number.
            update_dict: Dictionary with key, value pairs for info to update.

        Returns:

        """
        collections = Collections(self.token)
        resp_code, resp_data = collections.update(self.object_id, update_dict)
        return resp_code, resp_data
