"""

"""
from os.path import splitext
from figshare_interface.figshare_structures.projects import Projects
from figshare_interface.file_parsers import flatfile_3 as FlatFile
from figshare_interface.file_parsers.zyvex_parser import ZyvexFile
from ...figshare_articles.stm_articles.topography_article import TopoArticle
from ..local_article import LocalArticle

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class LocalTopoArticle(TopoArticle, LocalArticle):

    def __init__(self, OAuth_token, filename, file_ext):

        # Initialize STM topography metadata dictionary
        self.stm_topo_metadata = {'type': None,
                                  'vgap': None,
                                  'current': None,
                                  'xres': None,
                                  'yres': None,
                                  'xinc': None,
                                  'yinc': None,
                                  'xreal': None,
                                  'yreal': None,
                                  'unit': None,
                                  'unitxy': None,
                                  'date': None,
                                  'direction': None,
                                  'sample': None,
                                  'users': None,
                                  'substrate': None,
                                  'adsorbate': None,
                                  'prep': None,
                                  'notebook': None,
                                  'notes': None
                                  }

        self.file_ext = file_ext

        LocalArticle.__init__(self, OAuth_token, filename)

        self.read_file(filename)
        self.figshare_metadata['type'] = 'topo'

    def read_file(self, filename):
        """
        Determines the type of STM file and uses the correct parse function to fill the stm_topo_metadata fields.
        :param filename: str. Local path to file.
        :return:
        """

        file_types = {
            # OMICRON FLAT FILES
            '.Z_flat': FlatFile,

            # ZYVEX Files
            '.zad': ZyvexFile
        }
        if self.file_ext in file_types:
            if self.file_ext == '.Z_flat':
                file_data = file_types[self.file_ext].load(filename)
                file_info = file_data[0].info

                directions_str = ''
                for direction in file_data:
                    directions_str += direction.info['direction'] + ', '
                self.stm_topo_metadata['direction'] = directions_str
            else:
                file_data = file_types[self.file_ext].load(filename)
                file_info = file_data.info

            for key in file_info:
                if key in self.stm_topo_metadata:
                    # Added string to comply with new figshare custom fields formatting
                    self.stm_topo_metadata[key] = str(file_info[key])

    def index_schema(self):
        """
        Creates a dictionary to create a Whoosh index schema from
        :return:
        """
        schema_dict = {'type': ('id', True),
                       'vgap': ('numeric', True),
                       'current': ('numeric', True),
                       'xres': ('numeric', True),
                       'yres': ('numeric', True),
                       'xinc': ('numeric', True),
                       'yinc': ('numeric', True),
                       'xreal': ('numeric', True),
                       'yreal': ('numeric', True),
                       'unit': ('id', True),
                       'unitxy': ('id', True),
                       'date': ('text', True),
                       'direction': ('keyword', True),
                       'sample': ('text', True),
                       'users': ('keyword', True),
                       'substrate': ('text', True),
                       'adsorbate': ('text', True),
                       'prep': ('text', True),
                       'notebook': ('keyword', True),
                       'notes': ('text', True)
                       }
        return schema_dict

