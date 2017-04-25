"""
Base Class of Figshare Articles for use in Figshare Desktop
"""

from PyQt5.QtWidgets import (QTreeWidgetItem)

from figshare_interface.figshare_structures.collections import Collections
from figshare_interface.http_requests.figshare_requests import issue_request

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class Article(object):
    """
    Figshare Article Base Class
    """

    def __init__(self, OAuth_token: str, collection_id: int, article_id: str):
        """
        Creates the base Figshare metadata dictionary for an article and fills all available information.

        Args:
            OAuth_token: Authentication token generated from Figshare login.
            project_id: ID number of Figshare project article is within.
            article_id: ID number of the Figshare article.

        Returns:
            None

        Raises:
            None
        """
        # Create class variables
        self.token = OAuth_token
        self.collection_id = collection_id
        self.article_id = article_id

        # Initialise dictionary for basic Figshare metadata.
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

        # Initialise dictionary of metadata needed only for Figshare Desktop
        self.figshare_desktop_metadata = {
            'location': None,
            'thumb': None,
            'public_modified_date': None
        }

        # Initialize an empty object that will hold generated QTreeWidgetItem representations of the article
        self.qtreeitem = None

        # Request the article information from Figshare and fill the initialised metadata dictionaries
        self.fill_info()

        # Set the location field to Figshare to denote that it is not a local file
        self.figshare_desktop_metadata['location'] = 'Figshare'

    def gen_figshare_metadata(self, input_dict: dict):
        """
        Fill values in basic figshare_metadata dictionary from an input dictionary.

        Args:
            input_dict: Common keys in input_dict and figshare_metadata dict have values set to those of input_dict

        Returns:
            None

        Raises:
            None
        """
        # Iterate through keys in the input dictionary and check to see if they are in figshare_metadata
        for key in input_dict:
            if key in self.figshare_metadata:
                # For non-None values in input_dict set the values of figshare_metadata to those of input_dict
                if input_dict[key] != 'None' and input_dict[key] is not None:
                    self.figshare_metadata[key] = input_dict[key]

        # For published articles check to see if the public article is up-to-date
        if self.figshare_metadata['status'] == 'public':
            # Get the date of the last modification to the public article
            result = issue_request('GET', 'articles/{a_id}'.format(a_id=self.article_id), token=self.token)
            date = result['modified_date']
            self.figshare_desktop_metadata['public_modified_date'] = date
        # Perform up-to-date check
        self.check_uptodate()

    def check_uptodate(self):
        """
        Compares the private and public versions of an article to determine if it is up-to-date

        Args:

        Returns:
            None

        Raises:
            None
        """
        # For published articles
        if self.figshare_metadata['status'] == 'public':
            # Compare the private and public modified dates and set the up-to-date field appropriately
            if self.figshare_metadata['modified_date'] != self.figshare_desktop_metadata['public_modified_date']:
                self.figshare_metadata['up_to_date'] = False
            else:
                self.figshare_metadata['up_to_date'] = True
        # For unpublished articles, denote as such
        else:
            self.figshare_metadata['up_to_date'] = 'Unpublished'

    def input_dicts(self):
        """
        Returns a list of all metadata dictionaries associated with this article. Should be overwritten by child classes

        Args:

        Returns:
            list of dictionaries containing all metadata dictionaries

        Raises:
            None
        """
        return [self.figshare_metadata, self.figshare_desktop_metadata]

    def gen_qtree_item(self, input_list: list, input_dicts: list=None):
        """
        Create a QTreeWidgetItem from a list of keys corresponding to values in dictionry of metadata fields.

        Args:
        input_list: List of strings corresponding to keys in the input dictionaries. The order of the list
               dictates the order of the columns generated in the QTreeWidgetItem.
        input_dicts: List of dictionaries from which to generate the input list values. The order of the input
               dictionaries is important if multiple dictionaries contain the same key. Only the first will be used.

        Returns:
            None

        Raises:
            None
        """

        # If no input dictionaries are given take the default metadata dictionaries
        if input_dicts is None:
            input_dicts = self.input_dicts()

        # Create an empty list to generate the QTreeWidgetItem from
        tree_list = []
        # Loop through strings in the input_list
        for key in input_list:
            key_found = False  # Initialise that key has not yet been found
            # Loop through input dictionaries
            for d in input_dicts:
                # If the key is in the current dictionary add its value to the list and break the dictionary loop
                if key in d:
                    tree_list.append(str(d[key]))
                    key_found = True
                    break
            # If the key was not found then append a blank value to the list
            if not key_found:
                tree_list.append('')
        # Create a blank QTreeWidgetItem
        self.qtreeitem = QTreeWidgetItem()

        # Loop through the keys in the input list and add string versions of them to the columns in QTreeWidgetItem
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
        Retrieves article information from Figshare and fills the local metadata dictionaries from it.

        Args:

        Returns:
            None
        Raises:
            None
        """
        # Create an instance of the Projects class
        collections = Collections(self.token)
        # Retrieve a dictionary of article information from the project
        basic_info = collections.get_article(self.article_id)
        # Use the retrieved dictionary to fill the local metadata dictionaries
        self.gen_figshare_metadata(basic_info)
        # Perform a check on the format of the filled information
        self.check_basic()

    def update_info(self, input_dict: dict):
        """
        Updates the local metadata dictionaries from a given input dictionary.

        Args:
            input_dict: Key, Value pairs to overwrite existing values in the article metadata dictionaries.
        Returns:
            None
        Raises:
            None
        """
        # Use the input dictionary to fill the local metadata dictionaries
        self.gen_figshare_metadata(input_dict)
        # Perform a check on the format of the filled information
        self.check_basic()

    def check_basic(self):
        """
        Checks the formatting of metadata fields in the figshare_metadata dictionary

        Args:

        Returns:
            None

        Raises:
            None
        """

        # TITLE
        # =====
        # Title metadata should be a string with length between 3 and 500 characters

        title = self.figshare_metadata['title']  # get the current value for title
        if title is not None:
            # Convert the title to a string if it is not one already
            if type(title) is not str:
                title = str(title)
                # If the title was a list then it will have square brackets around it. Remove these
                if title[0] == '[':
                    title = title[1:-1]
            # The Article title must be between 2 and 500 characters
            if len(title) < 3:
                title += '000'
            if len(title) > 500:
                title = title[:500]
            # Set the metadata title to the edited version
            self.figshare_metadata['title'] = title

        # DESCRIPTION
        # ===========
        # Description should be a string of unlimited length.
        # Here we will remove any vestige of the description being within a list
        descr = self.figshare_metadata['description']  # get the current value
        if descr is not None:
            # Convert to a string if necessary, and remove brackets from a list if present
            if type(descr) is not str:
                descr = str(descr)
                if descr[0] == '[' and descr[-1] == ']':
                    descr = descr[1:-1]
            # Set the metadata value to the edited version
            self.figshare_metadata['description'] = descr

        # TAGS
        # ====
        # Tags should be a list of strings.
        tags = self.figshare_metadata['tags']  # get the current value
        if tags is not None:
            # If the tags are not in a list attempt to structure them into one
            if type(tags) is not list:
                tags = str(tags)
                if tags[0] == '[':
                    tags = tags[1:-1]
                tags = [tags]
            # For each tag in the list of tags check that it is a string and does not have brackets around it
            else:
                for tag in range(len(tags)):
                    if type(tags[tag]) is not str:
                        tags[tag] = str(tags[tag])
                    elif tags[tag][0] == '[':
                        tags[tag] = tags[tag][1:-1]
            # Set the metadata value to the edited version
            self.figshare_metadata['tags'] = tags

        # REFERENCES
        # ==========
        # References should be a list of strings of valid URLS
        refs = self.figshare_metadata['references']  # get the current value
        if refs is not None:
            # If references are not in a list convert to one
            if type(refs) is not list:
                refs = str(refs)
                if refs[0] == '[':
                    refs = refs[1:-1]
                checked_refs = [refs]
            else:
                # For each reference in the list remove encompassing brackets and check that it is a valid url
                for ref in range(len(refs)):
                    if type(refs[ref]) is not str:
                        refs[ref] = str(refs[ref])
                    elif refs[ref][0] == '[':
                        refs[ref] = refs[ref][1:-1]

                    if refs[ref][0:7] != 'http://':
                        refs[ref] = None

                # Remove any references that were not valid
                checked_refs = []
                for ref in refs:
                    if ref is not None:
                        checked_refs.append(ref)

            # Set the metadata value to the edited version
            self.figshare_metadata['references'] = checked_refs

        # CATEGORIES
        # ==========
        # Categories should be a list of integers that relate to valid category ID numbers on Figshare.
        # Here we will attempt to construct this list from either given integers, or strings that correspond to the
        # category names on Figshare.
        cats = self.figshare_metadata['categories']  # get the current value
        if cats is not None:
            # Get a dictionary of categories from Figshare with id and name pairs
            allowed_cats = issue_request(method='GET', endpoint='categories', token=self.token)
            cat_dict = {}
            for cat in allowed_cats:
                cat_dict[cat['id']] = cat['title']

            # If the current value of categories is a list check each of the items
            if type(cats) is list:
                checked_cats = []  # create an empty list to hold checked categories
                for cat in cats:
                    cat_type = type(cat)
                    # If the category value is a dictionary object check that it is a valid id, name pair
                    if cat_type is dict:
                        if 'id' in cat:
                            cat_id = cat['id']
                            if cat_id in cat_dict:
                                checked_cats.append(cat_id)

                    # If the category value is a string attempt to convert it to a valid categoriy ID number
                    elif cat_type is str:
                        # If the string can be converted directly to an integer do so and check for a valid ID
                        try:
                            cat_id = int(cat)
                            if cat_id in cat_dict:
                                checked_cats.append(cat_id)
                        # If the string could not be converted check if the string is the name of a category
                        except:
                            if cat in cat_dict.values():
                                for key, value in cat_dict.items():
                                    if value == cat:
                                        checked_cats.append(key)
                                        break
                    # If the category value is an integer check to see if it is a valid ID
                    elif cat_type is int:
                        if cat in cat_dict:
                            checked_cats.append(cat)

            # If the categories value is not a list set it to none
            else:
                checked_cats = None

            # Set the metadata value to the edited version
            self.figshare_metadata['categories'] = checked_cats

        # AUTHORS
        # =======
        # Authors metadata should comprise of a list of dictionaries which have either or the two following structures
        #    {'id': int}
        #    {'name': string}
        auths = self.figshare_metadata['authors']  # get the current value
        if auths is not None:
            auths_type = type(auths)  # get the type of the current value

            # If value is a list and not empty check its values
            if auths_type is list and auths != []:
                checked_auths = []  # create an empty list to hold the author dictionaries
                # Iterate through the list of authors
                for auth in auths:
                    item_type = type(auth)  # get the type of the value

                    # If the value is a dictionary object
                    if item_type is dict:
                        if 'id' in auth:  # If the value is an id
                            try:
                                id_int = int(auth['id'])
                                temp_d = {'id': id_int}
                                checked_auths.append(temp_d)
                            except:
                                pass

                        elif 'name' in auth:  # If the value is a name
                            if type(auth['name']) is str:
                                temp_d = {'name': auth['name']}
                                checked_auths.append(temp_d)
                    elif item_type is str:
                        try:
                            user_id = int(auth)
                            checked_auths.append({'id': user_id})
                        except:
                            checked_auths.append({'name': auth})

                    elif item_type is int:
                        checked_auths.append({'id': auth})

            elif auths_type is str:
                checked_auths = [{'name': auths}]
            elif auths_type is int:
                checked_auths = [{'id': auths}]
            else:
                checked_auths = None

            self.figshare_metadata['authors'] = checked_auths

        # DEFINED TYPE
        # ============
        # Defined type should be string equal to one of ten pre-defiend values. Here we will normalise inputs that
        # are either the string itself or an integer corresponding to the position in the list
        def_type = self.figshare_metadata['defined_type']  # get the current value
        # define a dictionary of the allowed values and corresponding integer keys
        types = {1: 'figure', 2: 'media', 3: 'dataset', 4: 'fileset', 5: 'poster', 6: 'paper', 7: 'presentation',
                 8: 'thesis', 9: 'code', 10: 'metadata'}
        if def_type is not None:
            def_type_type = type(def_type)  # get the type of the metadata value
            # If a string check that it is one of the ten pre-defined values
            if def_type_type is str:
                if def_type not in types.values():
                    def_type = None
            # If in integer check to see if it is in the pre-defined keys
            elif def_type_type is int:
                if def_type not in types:
                    def_type = None
                else:
                    def_type = types[def_type]
            else:
                def_type = None
            # Set the metadata value to the edited version
            self.figshare_metadata['defined_type'] = def_type

        # FUNDING
        # =======
        # Funding should be a string of length between 0 and 2000 characters
        fund = self.figshare_metadata['funding'] # get the current value
        if fund is not None:
            fund_type = type(fund)
            if fund_type is not str:
                fund = str(fund)
            if 0 < len(fund) < 2001:
                    fund = fund[:2000]
            # Set string to edited version
            self.figshare_metadata['funding'] = fund

        # License
        # ========
        # License should be a string of an integer corresponding to a predefined value
        lic = self.figshare_metadata['license'] # Get the current value of the license

        # Retrieve a list of available licenses from Figshare
        # Yields a list of dictionaries, with string-integer: name pairs
        lics_list = issue_request(method='GET', endpoint='account/licenses', token=self.token)

        # Convert the list of dictionaries into a single dictionary
        allowed_lics = {}
        for d in lics_list:
            allowed_lics[d['value']] = d['name']

        if lic is not None:
            lic_type = type(lic)  # get the type of the value
            # If a dictionary object is given try to extract value string-integer
            if lic_type is dict:
                if 'value' in lic:
                    lic_id = lic['value']
                    if lic_id in allowed_lics:
                        checked_lic = lic_id
                    else:
                        checked_lic = None
            # If a string is given then check if it is an allowed value
            elif lic_type is str:
                if lic in allowed_lics:
                    checked_lic = lic
                else:
                    checked_lic = None
            # If an integer is passed try to see if a string version of it is an allowed value
            elif lic_type is int:
                lic = str(lic)
                if lic in allowed_lics:
                    checked_lic = lic
                else:
                    checked_lic = None
            else:
                checked_lic = None
            # Set the metadata value to the edited version
            self.figshare_metadata['license'] = checked_lic

    def get_upload_dict(self):
        """
        Takes the different metadata dictionaries and ensures that their contents are ok for upload to figshare.

        Args:

        Returns:
            None

        Raises:
            None
        """
        self.check_basic()

        upload_dict = {}
        for key, value in self.figshare_metadata.items():
            if value is not None:
                upload_dict[key] = value
        return upload_dict

    def get_type(self):
        """
        Used to determine the type of the article instance. Should be overwritten by child classes.

        Args:

        Returns:
            string. Specifying the article type

        Raises:
            None
        """
        return 'article'
