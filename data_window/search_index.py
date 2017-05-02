"""

"""

import os
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.qparser import QueryParser


class ArticleIndex(object):
    """

    """

    def __init__(self, index_dir: str='figshare_desktop_index'):
        super().__init__()

        self.index_dir = index_dir
        # If there is no index directory create it
        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)

        self.schemas = {}
        self.document_types = set()

    #####
    # Index Functions
    #####

    def list_schema(self):
        """
        Returns a list of the schema name currently in the index
        :return: list
        """
        names = []
        for name in self.schemas.keys():
            names.append(name)
        return names

    def delete_index(self):
        """
        Called to remove the index from the disk.
        :return:
        """
        if os.path.isdir(self.index_dir):
            os.rmdir(self.index_dir)

    #####
    # Schema Functions
    #####

    def create_schema(self, schema_name: str):
        """
        Creates a schema and adds it to the index
        :param schema_name:
        :return:
        """
        index = create_in(self.index_dir, Schema())
        self.schemas[schema_name] = index

    def add_field(self, schema, field_name, field):
        """

        :return:
        """
        writer = self.schemas[schema].writer()
        writer.add_field(field_name, field)
        writer.commit()

    def add_TEXT(self, schema, field_name: str, stored: bool=False):
        """
        Adds a text field to the given schema
        :param schema: index schema
        :param field_name: name of the field to be added
        :param stored: should field be stored
        :return:
        """
        self.add_field(schema, field_name, TEXT(stored=stored))

    def add_KEYWORD(self, schema, field_name: str, stored: bool=False, commas: bool=True):
        """
        Addsa a keyword field to the given schema
        :param schema: index schema
        :param field_name: name of the field to be added
        :param stored: should field be stored
        :param commas: is this field a list of comma separated variables
        :return:
        """
        self.add_field(schema, field_name, KEYWORD(stored=stored, commas=commas))

    def add_ID(self, schema, field_name: str, stored: bool=False, unique: bool=False):
        """
        Adds a id field to the given schema
        :param schema: index schema
        :param field_name: name of the field to be added
        :param stored: should field be stored
        :return:
        """
        self.add_field(schema, field_name, ID(stored=stored, unique=unique))

    def add_NUMERIC(self, schema, field_name: str, stored: bool=False):
        """
        Adds a numeric (integer or float) field to the given schema
        :param schema: index schema
        :param field_name: name of the field to be added
        :param stored: should field be stored
        :return:
        """
        self.add_field(schema, field_name, NUMERIC(float, stored=stored))

    def add_DATETIME(self, schema, field_name: str, stored: bool=False):
        """
        Adds a datetime field to the given schema
        :param schema: index schema
        :param field_name: name of the field to be added
        :param stored: should field be stored
        :return:
        """
        self.add_field(schema, field_name, DATETIME(stored=stored))

    def add_BOOLEAN(self, schema, field_name: str, stored: bool=False):
        """
        Adds a booelan field to the given schema
        :param schema: index schema
        :param field_name: name of the field to be added
        :param stored: should field be stored
        :return:
        """
        self.add_field(schema, field_name, BOOLEAN(stored=stored))

    def add_NGRAM(self, schema, field_name: str, stored: bool=False):
        """
        Adds a N-Gram field to the given schema
        :param schema: index schema
        :param field_name: name of the field to be added
        :param stored: should field be stored
        :return:
        """
        self.add_field(schema, field_name, NGRAM(stored=stored))

    def get_fields(self, schema):
        """
        Returns a list of schema fields
        :return:
        """
        return self.schemas[schema].schema.names()

    def remove_field(self, schema, field_name: str):
        """
        Removes a given field from the schema
        :param field_name: name of the field to be removed
        :return:
        """
        writer = self.schemas[schema].writer()
        writer.remove_field(field_name)
        writer.commit()

    #####
    # Document Functions
    #####

    def addDocument(self, schema: str, data_dict: dict):
        """
        Adds a document to the index with fields from a dictionary

        Args:
            schema: Name of the Whoosh index schema to add document to.
            data_dict: Dictionary of document metadata from which schema relevant key, value pairs will be extracted.

        Returns:
            None
        """
        # Create an empty dictionary to hold schema relevant key, value pairs.
        document_dict = {}

        for key, value in data_dict.items():
            # Check to see if key is in the schema.
            if key in self.get_fields(schema):
                if value is not None and value != '':
                    # For lists create a string with comma separated tags.
                    if type(value) is list and value != []:
                        tags = ''
                        for tag in value:
                            tags += '{},'.format(tag)
                        value = tags[:-1]  # Drop the last comma.
                    document_dict[key] = u"{}".format(value)  # Convert value to unicode and add to the doc dict

        # Add the new document to the inedx schema
        writer = self.schemas[schema].writer()
        writer.add_document(**document_dict)
        writer.commit()

    def updateDocument(self, schema, data_dict: dict):
        """
        Updates an existing document in the given schema
        :param schema:
        :param data_dict: must contain the th unique document identifier as a field
        :return:
        """
        document_dict = {}
        for key, value in data_dict.items():
            if key in self.get_fields(schema):
                if value is not None and value != '':
                    if type(value) is list and value != []:
                        tags = ''
                        for tag in value:
                            tags += '{},'.format(tag)
                        value = tags[:-1]
                    document_dict[key] = u"{}".format(value)
        writer = self.schemas[schema].writer()
        writer.update_document(**document_dict)
        writer.commit()

    def removeDocument(self, schema, docnum: int):
        """
        Removes a document from the index by its document number
        :param docnum: docnum
        :return:
        """
        writer = self.schemas[schema].writer()
        writer.delete_document(docnum)
        writer.commit()

    #####
    # Search Functions
    #####

    def perform_search(self, schema, field: str, query: str, page: int=1, pagelen: int=20):
        """
        Performs a query of the index from the given field and query string
        :param schema:
        :param field: String. Index field
        :param query: String.
        :param page: int. starting page of results to return results from
        :param pagelen: int. number of results to display per page
        :return: list. results
        """
        if field is '':
            field = '*'

        results_dict = {}

        with self.schemas[schema].searcher() as searcher:
            last_page = False
            while not last_page:
                parser = QueryParser(field, self.schemas[schema].schema)
                search_query = parser.parse(query)
                results = searcher.search_page(search_query, page, pagelen)

                if results.total > 0:
                    for doc in range(results.pagelen):
                        results_dict[results.docnum(doc)] = results.results.fields(doc)

                last_page = results.is_last_page()
                page += 1

        return results_dict
