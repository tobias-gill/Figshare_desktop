"""

"""
import os
from PyQt5.QtWidgets import (QTreeWidgetItem)

from ..figshare_articles.article import Article

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class LocalArticle(Article):

    def __init__(self, OAuth_token, filename):

        # Initialize dictionary for basic figshare metadata.
        self.figshare_metadata = {'title': None,
                                  'id': None,
                                  'description': None,
                                  'tags': None,
                                  'references': None,
                                  'categories': None,
                                  'authors': None,
                                  'defined_type': None,
                                  'funding': None,
                                  'license': None,
                                  'version': None,
                                  'size': None,
                                  'status': 'local',
                                  'type': 'article'
                                  }

        self.figshare_desktop_metadata = {'location': None,
                                          'thumb': None
                                          }
        # Define the local file path and file title.
        self.local_path = os.path.abspath(filename)
        file_title = os.path.split(filename)[-1]
        self.figshare_metadata['title'] = file_title
        self.figshare_desktop_metadata['location'] = self.local_path

        # Initialize an empty object that will hold generated QTreeWidgetItem representations of the article.
        self.qtreeitem = None

        # Save the OAuth token for later use
        self.token = OAuth_token

    def fill_info(self):
        """
        Overwriting parent function to prevent unexpected usage.
        :return:
        """
        pass

    def read_file(self, filename):
        """
        If the file type is recognised parse the file to get metadata.
        :param filename: local path to file.
        :return:
        """
        # This is not required for a simple figshare article. It should be re-defined for specific file types.
        return None

    def index_schema(self):

        return {}
