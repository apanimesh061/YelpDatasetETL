# -*- coding: utf-8 -*-

import sys

"""
This class accepts documents from a MongoDB database.
"""


class Extract(object):
    extract_client = None
    database_name = None
    batch_size = None
    collection_type = None
    size = None
    cursor = None

    def __init__(self, extract_client, database_name, batch_size=100):
        """
        Creates an instance of the Extractor that gets documents from a MongoDB collection.
        :param extract_client: This is a MongoClient
        :param database_name: Name of the database
        :param batch_size: Batch size of the cursor on the collection user extraction
        """
        self._prepare(extract_client=extract_client, database_name=database_name, batch_size=batch_size)

    def _prepare(self, extract_client, database_name, batch_size):
        """
        :param extract_client: This is a MongoClient
        :param database_name: Name of the database
        :param batch_size: Batch size of the cursor on the collection user extraction
        :raises: Exception if extract_client or database_name are None
        """
        if extract_client is None:
            raise Exception("Looks like MongoDB was not initialized.")

        if database_name is None:
            raise Exception("Looks like you have used an invalid collection name.")

        self.extract_client = extract_client
        self.database_name = database_name
        self.batch_size = batch_size

    def set_current_collection(self, collection_type):
        """
        Setter of the collection from which the extraction would be performed.
        :param collection_type: type of the collection that is a part of self.database_name
        :raises: Exception if collection_name is None
        """
        if not collection_type:
            raise Exception("Looks like you have used an invalid collection name.")
        self.collection_type = collection_type
        self.size = self.database_name[self.collection_type.source].count()
        self.cursor = self.database_name[self.collection_type.source].find().batch_size(self.batch_size)

    def get_coll_size(self):
        return self.size

    def start(self):
        """
        This function scrolls over a collection is batch sizes of batch_size.
        :returns: a generator of page of size PAGE_SIZE
        """
        assert self.cursor is not None
        try:
            current_page = []
            for document in self.cursor:
                current_page.append(document)
                if len(current_page) == self.batch_size:
                    yield current_page
                    current_page = []
            if 0 < len(current_page) < self.batch_size:
                yield current_page
        except KeyboardInterrupt:
            sys.stderr.write("\nEncountered a keyboard interrupt.")
            sys.stderr.write("\nClosing the MongoDB cursor.\n")
        finally:
            self.cursor.close()
