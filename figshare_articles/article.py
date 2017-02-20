"""

"""

from PyQt5.QtWidgets import (QTreeWidgetItem)

from figshare_interface.figshare_structures.projects import Projects
from figshare_interface.http_requests.figshare_requests import issue_request

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
                                  'modified_date': None,
                                  'published_date': None,
                                  'up_to_date': None,
                                  'status': None,
                                  'group_id': None}

        self.figshare_desktop_metadata = {
            'location': None,
            'thumb': None,
            'public_modified_date': None
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
        if self.figshare_metadata['status'] == 'public':
            result = issue_request('GET', 'articles/{a_id}'.format(a_id=self.article_id), token=self.token)
            date = result['modified_date']
            self.figshare_desktop_metadata['public_modified_date'] = date
        self.check_uptodate()

    def check_uptodate(self):
        """
        Checks to see if the private and public modified dates are equal and assigns the correct value to the
        figshare_metadata['up_to_date'] field.
        :return:
        """

        if self.figshare_metadata['status'] == 'public':
            if self.figshare_metadata['modified_date'] != self.figshare_desktop_metadata['public_modified_date']:
                self.figshare_metadata['up_to_date'] = False
            else:
                self.figshare_metadata['up_to_date'] = True
        else:
            self.figshare_metadata['up_to_date'] = 'Unpublished'

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
            if key is bool:
                self.qtreeitem.setData(column, 0, str(key))
            else:
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
        self.check_basic()

    def update_info(self, input_dict):

        self.gen_figshare_metadata(input_dict)
        self.check_basic()

    def check_basic(self):

        # Title
        title = self.figshare_metadata['title']
        if title is not None:
            if type(title) is not str:
                title = str(title)
                if title[0] == '[':
                    title = title[1:-1]
            if not 3 < len(self.figshare_metadata['title']) < 501:
                title = title[:500]
            self.figshare_metadata['title'] = title

        # Description
        descr = self.figshare_metadata['description']
        if descr is not None:
            if type(descr) is not str:
                descr = str(descr)
                if descr[0] == '[':
                    descr = descr[1:-1]
            self.figshare_metadata['description'] = descr

        # Tags
        tags = self.figshare_metadata['tags']
        if tags is not None:
            if type(tags) is not list:
                tags = str(tags)
                if tags[0] == '[':
                    tags = tags[1:-1]
                tags = [tags]
            else:
                for tag in range(len(tags)):
                    if type(tags[tag]) is not str:
                        tags[tag] = str(tags[tag])
                    elif tags[tag][0] == '[':
                        tags[tag] = tags[tag][1:-1]
            self.figshare_metadata['tags'] = tags

        # References
        refs = self.figshare_metadata['references']
        if refs is not None:
            if type(refs) is not list:
                refs = str(refs)
                if refs[0] == '[':
                    refs = refs[1:-1]
                checked_refs = [refs]
            else:
                for ref in range(len(refs)):
                    if type(refs[ref]) is not str:
                        refs[ref] = str(refs[ref])
                    elif refs[ref][0] == '[':
                        refs[ref] = refs[ref][1:-1]

                    if refs[ref][0:7] != 'http://':
                        refs[ref] = None

                checked_refs = []
                for ref in refs:
                    if ref is not None:
                        checked_refs.append(ref)

            self.figshare_metadata['references'] = checked_refs

        # Categories
        cats = self.figshare_metadata['categories']
        if cats is not None:

            allowed_cats = issue_request(method='GET', endpoint='categories', token=self.token)
            cat_dict = {}
            for cat in allowed_cats:
                cat_dict[cat['id']] = cat['title']


            if type(cats) is list:
                checked_cats = []
                for cat in cats:
                    cat_type = type(cat)
                    if cat_type is dict:
                        cat_id = cat['id']
                        if cat_id in cat_dict:
                            checked_cats.append(cat_id)
                    elif cat_type is str:
                        try:
                            cat_id = int(cat)
                            if cat_id in cat_dict:
                                checked_cats.append(cat_id)
                        except:
                            if cat in cat_dict.values():
                                for key, value in cat_dict.items():
                                    if value == cat:
                                        checked_cats.append(key)
                                        break
                    elif cat_type is int:
                        if cat in cat_dict:
                            checked_cats.append(cat)
                    else:
                        pass
            else:
                checked_cats = None
            self.figshare_metadata['categories'] = checked_cats

        # Authors
        auths = self.figshare_metadata['authors']
        if auths is not None:

            auths_type = type(auths)
            if auths_type is list and auths != []:
                list_type = type(auths[0])
                if list_type is dict:

                    checked_auths = []
                    for d in auths:
                        if 'id' in d:
                            temp_d = {'id': d['id']}

                        elif 'name' in d:
                            temp_d = {'name': d['name']}
                        checked_auths.append(temp_d)
                else:
                    checked_auths = []
                    for item in auths:
                        item_type = type(item)
                        if item_type is str:
                            try:
                                user_id = int(item)
                                checked_auths.append({'id': user_id})
                            except:
                                checked_auths.append({'name': item})
                        elif item_type is int:
                            checked_auths.append({'id': item})

            elif auths_type is str:
                checked_auths = [{'name': auths}]
            elif auths_type is int:
                checked_auths = [{'id': auths}]
            else:
                checked_auths = None

            self.figshare_metadata['authors'] = checked_auths

        # Defined_type
        def_type = self.figshare_metadata['defined_type']
        types = {1: 'figure', 2: 'media', 3: 'dataset', 4: 'fileset', 5: 'poster', 6: 'paper', 7: 'presentation',
                 8: 'thesis', 9: 'code', 10: 'metadata'}
        if def_type is not None:
            def_type_type = type(def_type)
            if def_type_type is str:
                if def_type not in types.values():
                    def_type = None
            elif def_type_type is int:
                if def_type not in types:
                    def_type = None
                else:
                    def_type = types[def_type]
            else:
                def_type = None

            self.figshare_metadata['defined_type'] = def_type

        # Funding
        fund = self.figshare_metadata['funding']
        if fund is not None:
            fund_type = type(fund)
            if fund_type is not str:
                fund = str(fund)
            if 0 < len(fund) < 2001:
                    fund = fund[:2000]

            self.figshare_metadata['funding'] = fund

        # Liscense
        lic = self.figshare_metadata['license']
        lics_list = issue_request(method='GET', endpoint='account/licenses', token=self.token)
        allowed_lics = {}
        for d in lics_list:
            allowed_lics[d['value']] = d['name']

        if lic is not None:
            lic_type = type(lic)
            if lic_type is dict:
                lic_id = lic['value']
                if lic_id in allowed_lics:
                    checked_lic = lic_id
                else:
                    checked_lic = None
            elif lic_type is str:
                try:
                    lic_id = int(lic)
                    if lic_id in allowed_lics:
                        checked_lic = lic_id
                    else:
                        checked_lic = None
                except:
                    if lic in allowed_lics.values():
                        for key, value in allowed_lics.items():
                            if value == lic:
                                checked_lic = key
                    else:
                        checked_lic = None
            elif lic_type is int:
                if lic in allowed_lics:
                    checked_lic = lic
                else:
                    checked_lic = None
            else:
                checked_lic = None
            self.figshare_metadata['license'] = checked_lic

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
