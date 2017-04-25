"""
New Collection Window

This module contains the new collection window class that allows a user to create a new figshare collection.
"""

# Standard Imports
from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (QLabel, QGridLayout, QMessageBox)
from requests import HTTPError

from Figshare_desktop.abstract_windows.new_object_window import NewObjectWindow
from Figshare_desktop.custom_widgets.button_field import QButtonField
from Figshare_desktop.formatting.formatting import (grid_label)
from figshare_interface.figshare_structures.collections import Collections
from figshare_interface.http_requests.figshare_requests import issue_request

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class NewCollectionWindow(NewObjectWindow):
    """
    Window subclasses the abstract NewObjectWindow class.
    """

    def create_button_field(self, label: str):
        """
        Creates a label button field pair.

        Args:
            label: Name of field to be associated to the button field.

        Returns:
            lbl (QLabel): Label of the button field
            btn_field (QButtonField): Button field layout.
        """
        lbl = QLabel(label)
        grid_label(self.app, lbl)

        button_field = QButtonField()

        return lbl, button_field

    def create_object_info_layout(self):
        """
        Creates a layout with label and edit fields for creating a new figshare collection.

        Returns:
            grid (QGridLayout): grid layout containing the different info fields and labels.
        """
        # TITLE
        title_lbl, self.title_field = self.create_lineedit('Title')
        self.title_field.setPlaceholderText('Enter Collection title here.')

        # DESCRIPTION
        desc_lbl, self.descr_field = self.create_edit('Description')
        self.descr_field.setPlaceholderText('Enter meaningful collection description here.')

        # AUTHORS
        auth_lbl, self.auth_field = self.create_button_field('Authors')

        # CATEGORIES
        cat_lbl, self.cat_field = self.create_button_field('Categories')

        # TAGS
        tag_lbl, self.tag_field = self.create_button_field('Tags')

        # REFERENCES
        ref_lbl, self.ref_field = self.create_button_field('References')

        # Create Layout
        grid = QGridLayout()

        # Add Title
        grid.addWidget(title_lbl, 0, 0, Qt.AlignLeft)
        grid.addWidget(self.title_field, 0, 1)

        # Add Description
        grid.addWidget(desc_lbl, 1, 0, Qt.AlignLeft)
        grid.addWidget(self.descr_field, 1, 1)

        # Add Authors
        grid.addWidget(auth_lbl, 2, 0, Qt.AlignLeft)
        grid.addWidget(self.auth_field, 2, 1)

        # Add Categories
        grid.addWidget(cat_lbl, 3, 0, Qt.AlignLeft)
        grid.addWidget(self.cat_field, 3, 1)

        # Add Tags
        grid.addWidget(tag_lbl, 4, 0, Qt.AlignLeft)
        grid.addWidget(self.tag_field, 4, 1)

        # Add References
        grid.addWidget(ref_lbl, 5, 0, Qt.AlignLeft)
        grid.addWidget(self.ref_field, 5, 1)

        grid.setColumnStretch(1, 3)

        return grid

    # Widget Actions
    # ==============

    def on_save_pressed(self):
        """
        Called when the save button is pressed. Will create a new Figshare project from the filled fields.

        Returns:
            None

        Raises:
            ValueError: Error may be raised if information given is not formatted correctly for Figshare.
            TypeError: Error may occur if the value passed to Figshare API Interface is not the correct type.
            KeyError: Error may occur if mandatory default information in not provided.
            HTTPError: Error may occur if there is a fault in the upload, or if the formatting is incorrect.
        """
        # Get Collection Info
        title = self.title_field.text()
        description = self.descr_field.toPlainText()
        authors = self.auth_field.get_tags()
        categories = self.cat_field.get_tags()
        tags = self.tag_field.get_tags()
        references = self.ref_field.get_tags()

        # Format Author tags
        formatted_authors = []
        for auth in authors:
            try:
                auth_id = int(auth)
                formatted_authors.append({'id': auth_id})
            except:
                formatted_authors.append({'name': auth})

        # Get a dictionary of categories from Figshare with id and name pairs
        allowed_cats = issue_request(method='GET', endpoint='categories', token=self.token)
        cat_dict = {}
        for cat in allowed_cats:
            cat_dict[cat['id']] = cat['title']

        # Format categories
        formatted_categories = []

        for cat in categories:
            try:
                cat_id = int(cat)
                if cat_id in cat_dict:
                    formatted_categories.append(cat_id)
            except:
                if cat in cat_dict.values():
                    for id_n, value in cat_dict.items():
                        if value == cat:
                            formatted_categories.append(id_n)
                            break

        # Format References
        formatted_references = []
        for ref in references:
            if ref[0:7] == 'http://':
                formatted_references.append(ref)

        # Create Collection Info Dictionary
        creation_dict = {
            'title': title,
            'description': description
        }
        if formatted_authors != []:
            creation_dict['authors'] = formatted_authors
        if formatted_categories != []:
            creation_dict['categories'] = formatted_categories
        if tags != []:
            creation_dict['tags'] = tags
        if references != []:
            creation_dict['referecnes'] = formatted_references

        # Create Collection
        try:
            collection_info = self.create_object(creation_dict)
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("New Project Created\n{}".format(collection_info['title']))
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox, exit_parent=True))
            msgBox.show()

        except ValueError as err:
            err_args = err.args
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText(err_args[0])
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
            msgBox.show()

        except TypeError as err:
            err_args = err.args
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText(err_args[0])
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
            msgBox.show()

        except KeyError as err:
            err_args = err.args
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText(err_args[0])
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
            msgBox.show()

        except HTTPError as err:
            err_args = err.args
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText(err_args[0])
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.buttonClicked.connect(lambda: self.on_msgbtn_pressed(msgBox))
            msgBox.show()

    def on_cancel_pressed(self):
        """
        Called when the cancel button is pressed. Will return to the collections window without creating a new
        collection

        Returns:
            None
        """
        self.open_windows.remove('new_collection_window')
        self.close()
        self.parent.section_window.on_collections_btn_pressed()

    # Figshare API Functions
    # ======================

    def create_object(self, info_dict: dict):
        """

        Args:
            info_dict:

        Returns:

        """
        collections = Collections(self.token)
        required_fields = ['title']
        for field in required_fields:
            if field not in info_dict:
                raise KeyError("Mandatory field: {} not found in input dictionary.".format(field))

        object_info = collections.create(**info_dict)

        return object_info
