"""
Figshare Collections Window

This window presents a view of the collections in a users account and allows for them to be created, and deleted.
Collections can then be opened to examine their contents, an action that creates new child windows.
"""
# Standard Imports

# PyQt Imports

# Figshare Desktop Imports
from Figshare_desktop.abstract_windows.figshare_structure_list import FigshareObjectWindow
from Figshare_desktop.collections_windows.collection_info_window import CollectionInfoWindow
from Figshare_desktop.collections_windows.new_collection_window import NewCollectionWindow
from figshare_interface import Collections

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class CollectionsWindow(FigshareObjectWindow):
    """
    Child of the Abstract FigshareObjectWindow with changes to call Collections objects from Figshare.
    """

    def on_create_btn_pressed(self):
        """
        Called when the create new collection button is pressed.

        Returns:
            None
        """
        if 'new_collection_window' in self.open_windows:
            self.open_windows.remove('new_collection_window')
            self.parent.new_collection_window.close()
        else:
            self.open_windows.remove('collections_window')
            self.close()

            if 'collection_info_window' in self.open_windows:
                self.open_windows.remove('collection_info_window')
                self.parent.collection_info_window.close()
            if 'collection_articles_window' in self.open_windows:
                self.open_windows.remove('collection_articles_window')
                self.parent.collection_articles_window.close()
            if 'article_edit_window' in self.open_windows:
                self.open_windows.remove('article_edit_window')
                self.parent.article_edit_window.close()

            self.open_windows.add('new_collection_window')
            self.parent.new_collection_window = NewCollectionWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.new_collection_window)
            self.parent.new_collection_window.show()

    def is_info_open(self):
        """
        Called to see if there is a Figshare collection info window open.

        Returns:
            open (bool): True, or False dependent on if info window is already open
            object_id (int): Figshare collection ID number
        """
        if 'collection_info_window' in self.open_windows:
            open_obj_id = self.parent.collection_info_window.object_id
            return True, open_obj_id
        else:
            return False, None

    def close_object_info_window(self):
        """
        Called when the existing object info window needs to be closed.

        Returns:
            None
        """
        self.open_windows.remove('collection_info_window')
        self.parent.collection_info_window.close()

        if 'collection_articles_window' in self.open_windows:
            self.open_windows.remove('collection_articles_window')
            self.parent.collection_articles_window.close()
        if 'articles_edit_window' in self.open_windows:
            self.open_windows.remove('article_edit_window')
            self.parent.article_edit_window.close()

    def create_new_object_info_window(self, object_id: int):
        """
        Called when a new object info window is to be created.

        Args:
            object_id: Figshare collection ID number

        Returns:
            None
        """
        self.open_windows.add('collection_info_window')
        self.parent.collection_info_window = CollectionInfoWindow(self.app, self.token, self.parent, object_id)
        self.parent.mdi.addSubWindow(self.parent.collection_info_window)
        self.parent.collection_info_window.show()

    def reopen_objects(self):
        """
        Called to open and close the figshare collection window

        Returns:
            None
        """
        for i in range(2):
            self.parent.section_window.on_collection_btn_pressed()

    # Figshare API Interface Functions
    # ================================

    def get_object_list(self):
        """
        Called to return a list of Figshare collections associated to the user.

        Returns:
            object_list (list of dicts): List of users Figshare objects.
        """
        collections = Collections(self.token)
        object_list = collections.get_list()
        return object_list

    def search_objects(self, search_text: str):
        """
        Gets a list of objects matching the users search query.

        Args:
            search_text: Figshare style elastic search string

        Returns:
            result (list of dicts): Gives a list of dictionary objects that either match those of the search criteria,
                or returns the full set if no matches found.
        """
        collections = Collections(self.token)
        result = collections.search(search_text)
        if len(result) == 0:
            result = collections.get_list()
        return result

    def delete_object(self, object_id: int):
        """
        Called to delete the given figshare object.

        Args:
            object_id:

        Returns:
            bool: True of False dependent on if the deletion was successful.
        """
        collections = Collections(self.token)
        try:
            collections.delete(object_id, safe=False)  # Suppress command line confirmation
            return True
        except:
            return False
