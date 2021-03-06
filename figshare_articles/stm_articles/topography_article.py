"""

"""
from figshare_interface.figshare_structures.projects import Projects
from ..article import Article

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class TopoArticle(Article):

    def __init__(self, OAuth_token, project_id, article_id):

        # Initialize STM topography metadata dictionary.
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

        super().__init__(OAuth_token, project_id, article_id)

    def gen_stm_topo_metadata(self, input_dict):
        """
        Fill values in the stm_topo_metadata dict from an input dictionary.
        :param input_dict: dict. Only extracts values from keys in both stm_topo_metadata and input_dict dictionaries.
        :return:
        """
        for key in input_dict:
                if key in self.stm_topo_metadata:
                    if input_dict[key] != 'None' and input_dict[key] is not None:
                        self.stm_topo_metadata[key] = input_dict[key]

    def fill_info(self):
        """
        Fill in the metadata dictionaries.
        :return:
        """
        project = Projects(self.token)
        basic_info = project.get_article(self.project_id, self.article_id)
        stm_topo_info = self.recreate_custom_fields(basic_info['custom_fields'])
        self.gen_figshare_metadata(basic_info)
        self.gen_stm_topo_metadata(stm_topo_info)
        self.check_basic()

    def update_info(self, input_dict):
        self.gen_figshare_metadata(input_dict)
        self.gen_stm_topo_metadata(input_dict)
        self.check_basic()

    def input_dicts(self):

        return [self.figshare_metadata, self.figshare_desktop_metadata, self.stm_topo_metadata]

    def check_file_specific(self):
        pass

    def get_upload_dict(self):
        """
        Takes the different metadata dictionaries and ensures that their contents are of for upload to figshare.
        :return:
        """

        self.check_basic()
        ignore_list = {'id', 'size', 'version', 'created_date', 'modified_date', 'published_date', 'up_to_date',
                       'status', 'group_id'}
        upload_dict = {}
        for key, value in self.figshare_metadata.items():

            if key not in ignore_list:
                if value is not None:
                    upload_dict[key] = value

        upload_dict['custom_fields'] = {}
        for key, value in self.stm_topo_metadata.items():
            if value is not None:
                upload_dict['custom_fields'][key] = value

        return upload_dict

    def get_type(self):
        return 'stm_topo'

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
