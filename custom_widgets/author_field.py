"""

"""

# PyQt Imports
from Figshare_desktop.custom_widgets.tag_button import QTagButton

# Figshare Desktop Imports
from Figshare_desktop.custom_widgets.button_field import QButtonField

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class AuthorField(QButtonField):
    """
    Subclass of the QButton field widget that is customised visualise and return Figshare author metadata.
    """

    def add_tag(self, author_dict: dict):
        """
        Adds an author tag button to the frame.

        Args:
            author_dict: Figshare style author dictionary object.

        Returns:

        """
        if type(author_dict) is dict:
            if 'full_name' in author_dict and 'id' in author_dict:
                lbl = author_dict['full_name']
                tooltip = author_dict['id']

            elif 'full_name' in author_dict:
                lbl = author_dict['name']
                tooltip = ''

            elif 'id' in author_dict:
                lbl = str(author_dict['id'])
                tooltip = ''

        elif type(author_dict) is str:
            lbl = author_dict
            tooltip = ''

        btn = QTagButton(lbl, self.tags, tooltip)
        self.tags.add(lbl)
        self.tag_box.addWidget(btn)

    def get_tags(self):
        """
        Gets the tags in a Figshare author metadata format.

        Returns:
            auth_list (list): list of dictionary objects for the authors.
        """
        auth_list = []
        tags = list(self.tags)
        for tag in tags:
            auth_dict = {}
            try:
                tag = int(tag)
                auth_dict['id'] = tag
            except:
                auth_dict['name'] = tag

            auth_list.append(auth_dict)

        return auth_list
