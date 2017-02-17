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


class SpecArticle(Article):

    def __init__(self, OAuth_token, project_id, article_id):
        # Initialize STM topography metadata dictionary.
        self.stm_spec_metadata = {'type': None,
                                  'vgap': None,
                                  'current': None,
                                  'vres': None,
                                  'vinc': None,
                                  'vreal': None,
                                  'vstart': None,
                                  'unitv': None,
                                  'unit': None,
                                  'date': None,
                                  'direction': None,
                                  'sample': None,
                                  'users': None,
                                  'substrate': None,
                                  'adsorbate': None,
                                  'prep': None,
                                  'notebook': None,
                                  'notes': None,
                                  'vmod': None,
                                  'vsen': None,
                                  'freq': None,
                                  'tmeas': None,
                                  'phase': None,
                                  'harm': None
                                  }

        super().__init__(OAuth_token, project_id, article_id)

    def gen_stm_spec_metadata(self, input_dict):
        """
        Fill values in the stm_topo_metadata dict from an input dictionary.
        :param input_dict: dict. Only extracts values from keys in both stm_topo_metadata and input_dict dictionaries.
        :return:
        """
        for key in input_dict:
            if key in self.stm_spec_metadata:
                if input_dict[key] != 'None' and input_dict[key] is not None:
                    self.stm_spec_metadata[key] = input_dict[key]

    def fill_info(self):
        """
        Fill in the metadata dictionaries.
        :return:
        """
        project = Projects(self.token)
        basic_info = project.get_article(self.project_id, self.article_id)
        stm_top_info = self.recreate_custom_fields(basic_info['custom_fields'])
        self.gen_figshare_metadata(basic_info)
        self.gen_stm_spec_metadata(stm_top_info)
        self.check_basic()

    def update_info(self, input_dict):
        self.gen_figshare_metadata(input_dict)
        self.gen_stm_spec_metadata(input_dict)
        self.check_basic()

    def input_dicts(self):

        return [self.figshare_metadata, self.figshare_desktop_metadata, self.stm_spec_metadata]

    def check_file_specific(self):
        pass

    def get_upload_dict(self):
        """
        Takes the different metadata dictionaries and ensures that their contents are of for upload to figshare.
        :return:
        """

        self.check_basic()

        upload_dict = {}
        for key, value in self.figshare_metadata.items():
            if value is not None:
                upload_dict[key] = value

        upload_dict['custom_fields'] = {}
        for key, value in self.stm_spec_metadata.items():
            if value is not None:
                upload_dict['custom_fields'][key] = value

        return upload_dict

    def get_type(self):
        return 'stm_spec'
