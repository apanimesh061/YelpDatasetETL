# -*- coding: utf-8 -*-

import sys
from elasticsearch.helpers import streaming_bulk, parallel_bulk

"""
Loader script that loads transformed documents into Elasticsearch.
"""


class Load(object):
    bulk_size = None
    multi_threaded = None
    load_client = None
    index_name = None
    collection_type = None
    extractor = None
    no_of_threads = None
    ingestion_pipeline = None

    def __init__(self, load_client, index_name, extractor, bulk_size=500):
        """
        Creates the Elasticsearch end of this ETL pipeline.

        :param load_client:
        :param index_name:
        :param extractor:
        :param bulk_size:
        """
        self._prepare(load_client, index_name, extractor)
        self.bulk_size = bulk_size
        self.multi_threaded = False

    def _prepare(self, load_client, index_name, extractor):
        """
        :param load_client: This is an Elasticsearch client
        :param index_name: Name of the index name
        :param extractor: Object of the
        :raises: Exception if load_client or extractor are None
        """
        if (load_client is not None) and (extractor is not None):
            self.load_client = load_client
            self.index_name = index_name
            self.extractor = extractor
        else:
            raise Exception("Illegal Argument Exception")

    def set_current_collection(self, collection_type):
        """
        :param collection_type: Type of the collections
        :raises: Exception if collection_type
        """
        if not collection_type:
            raise Exception("Illegal Argument Exception")
        self.collection_type = collection_type

    def enable_multithreading(self):
        """

        :return:
        """
        self.multi_threaded = True

    def set_no_of_threads(self, n):
        """

        :param n:
        :return:
        """
        if not self.multi_threaded:
            raise Exception("Please enable multi threading")
        self.no_of_threads = n

    def enable_ingestion_pipeline(self, ingestion_pipeline):
        """

        :param ingestion_pipeline:
        :return:
        """
        self.ingestion_pipeline = ingestion_pipeline

    def start_streaming(self):
        """
        Performs a bulk insert to Elasticsearch.
        """
        total_docs = self.extractor.get_coll_size()

        indexed_docs = 0
        failures = 0
        for current_page in self.extractor.start():
            current_chunk = [self.collection_type.apply_transform()(doc) for doc in current_page]
            bulk_args = dict(
                client=self.load_client,
                actions=current_chunk,
                index=self.index_name,
                doc_type=self.collection_type.destination,
                chunk_size=self.bulk_size,
                raise_on_error=True
            )

            """
            This is another tranformation layer where an input documents field undergoes Sentiment Analysis using
            VADER analyzer. An Elasticsearch ingestion plugin was created for this purpose.
            Ref [1]: https://github.com/apanimesh061/elasticsearch-sentiment-plugin
            Ref [2]: https://github.com/apanimesh061/VaderSentimentJava
            """
            if self.ingestion_pipeline is not None:
                bulk_args.update({"pipeline": self.ingestion_pipeline})

            """
            This section helps us choose which bulk ingestion procedure we need to take.
            """
            bulk_type = streaming_bulk
            if self.multi_threaded:
                bulk_args.update({"thread_count": self.no_of_threads})
                bulk_type = parallel_bulk

            for response, result in bulk_type(**bulk_args):
                action, result = result.popitem()
                doc_id = '/%s/%s/%s' % (self.index_name, self.collection_type.destination, result['_id'])
                if not response:
                    failures += 1
                    sys.stderr.write('\n[FAILURE]\t%s document %s: %r' % (action, doc_id, result))
                else:
                    indexed_docs += 1
            sys.stdout.write("\rIndexed %d / %d documents with %d failures" % (indexed_docs, total_docs, failures))
            sys.stdout.flush()
