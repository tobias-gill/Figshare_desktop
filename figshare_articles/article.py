"""

"""

from PyQt5.QtWidgets import  (QTreeWidgetItem)

from figshare_interface.figshare_structures.projects import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class Article(object):

    def __init__(self, OAuth_token, project_id, article_id):

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
                                  'size': None,
                                  'version': None,
                                  'created_date': None,
                                  'published_date': None,
                                  'status': None,
                                  'group_id': None}

        self.figshare_desktop_metadata = {
            'location': None,
            'thumb': None,
        }

        # Initialize an empty object that will hold generated QTreeWidgetItem representations of the article.
        self.qtreeitem = None

        self.token = OAuth_token
        self.project_id = project_id
        self.article_id = article_id

        self.fill_info()


    def gen_figshare_metadata(self, input_dict):
        """
        Fill values in basic figshare_metadata dictionary from input dictionary.
        :param input_dict: dict object. Only extracts values from keys in both figshare_metadata and input dictionaries.
        :return:
        """
        for key in input_dict:
            if key in self.figshare_metadata:
                if input_dict[key] != 'None' and input_dict[key] is not None:
                    self.figshare_metadata[key] = input_dict[key]

    def input_dicts(self):

        return [self.figshare_metadata, self.figshare_desktop_metadata]

    def gen_qtree_item(self, input_list, input_dicts):
        """
        Create a QTreeWidgetItem from a list of keys corresponding to values in figshare_metadata.
        :param input_list: List of strings corresponding to keys in the input dictionaries. The order of the list
               dictates the order of the columns generated in the QTreeWidgetItem.
        :param input_dicts: Series of input dictionaries from which to generate the list. The order of the input
               dictionaries is important if multiple dictionaries contain the same key. Only the first will be used.
        :return:
        """

        tree_list = []
        for key in input_list:
            key_found = False
            for d in input_dicts:
                if key in d:
                    tree_list.append(str(d[key]))
                    key_found = True
                    break
            if not key_found:
                tree_list.append('')
        self.qtreeitem = QTreeWidgetItem()
        column = 0
        for key in tree_list:
            self.qtreeitem.setData(column, 0, key)
            column += 1

    @staticmethod
    def recreate_custom_fields(custom_fields):
        d = {}

        for row in custom_fields:
            d[row['name']] = row['value']
        return d

    def fill_info(self):
        """
        Fill in the metadata dictionaries.
        :return:
        """
        project = Projects(self.token)
        basic_info = project.get_article(self.project_id, self.article_id)
        self.gen_figshare_metadata(basic_info)

    def update_info(self, input_dict):

        self.gen_figshare_metadata(input_dict)

    def check_basic(self):

        # Title
        title = self.figshare_metadata['title']
        if title is not None:
            if type(title) is not str:
                title = str(title)
            if not 3 < len(self.figshare_metadata['title']) < 501:
                title = title[:500]
            self.figshare_metadata['title'] = title

        # Description
        descr = self.figshare_metadata['description']
        if descr is not None:
            if type(descr) is not str:
                descr = str(descr)
            self.figshare_metadata['description'] = descr

        # Tags
        tags = self.figshare_metadata['tags']
        if tags is not None:
            if type(tags) is not list:
                tags = [str(tags)]
            else:
                for tag in range(len(tags)):
                    if type(tags[tag]) is not str:
                        tags[tag] = str(tags[tag])
            self.figshare_metadata['tags'] = tags

        # References
        refs = self.figshare_metadata['references']
        if refs is not None:
            if type(refs) is not list:
                refs = [str(refs)]
            else:
                for ref in range(len(refs)):
                    if type(refs[ref]) is not str:
                        refs[ref] = str(refs[ref])
            self.figshare_metadata['references'] = refs

        # Categories
        cats = self.figshare_metadata['categories']
        if cats is not None:
            if type(cats) is not list:
                try:
                    cats = [int(cats)]
                except:
                    cats = None
            else:
                for cat in range(len(cats)):
                    if type(cats[cat]) is not int:
                        try:
                            cats[cat] = int(cats[cat])
                        except:
                            cats = None
                            break
            self.figshare_metadata['categories'] = cats

        # Authors
        auths = self.figshare_metadata['authors']
        if auths is not None:
            if type(auths) is not list:
                auths = None
            else:
                for auth in range(len(auths)):
                    if type(auths[auth]) is not dict:
                        auths = None
                        break
                    elif type(auths[auth]) is dict:
                        for key, value in auths[auth].items():
                            if key != 'id' or key != 'name':
                                auths = None
                            elif key == 'id':
                                if type(value) != int:
                                    auths = None
                            elif key == 'name':
                                if type(value) != str:
                                    auths = None
            self.figshare_metadata['authors'] = auths

        # Defined_type
        def_type = self.figshare_metadata['defined_type']
        types = ['figure', 'media', 'dataset', 'fileset', 'poster', 'paper', 'presentation', 'thesis', 'code',
                 'metadata']
        if def_type is not None:
            if type(def_type) is not str:
                def_type = None
            elif def_type not in types:
                def_type = None
            self.figshare_metadata['defined_type'] = def_type

        # Funding
        fund = self.figshare_metadata['funding']
        if fund is not None:
            if type(fund) is not str:
                fund = str(fund)
            if 0 < len(fund) < 2001:
                fund = fund[:2000]
            self.figshare_metadata['funding'] = fund

        # Liscense
        lisc = self.figshare_metadata['license']
        if lisc is not None:
            if type(lisc) is not int:
                try:
                    lisc = int(lisc)
                except:
                    lisc = None
            self.figshare_metadata['license'] = lisc

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
        return upload_dict

    def get_type(self):
        return 'article'
