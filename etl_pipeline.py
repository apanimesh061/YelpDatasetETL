# -*- coding: utf-8 -*-

import sys
import timeit
import getopt
import elasticsearch
from load import Load
from extract import Extract
from pymongo import MongoClient
from pymongo import errors
from datatype import Collection

"""
This is a command line tool to extract Mongo Tables to an Elasticsearch index.
"""

if __name__ == "__main__":
    # Flag which sets whether or not the application is going to be multi-threaded.
    is_mt = False

    # This is the collection name which will be transferred from Mongo to Elasticsearch.
    coll_name = None

    # If `is_mt` is True, this is the default number of threads that will be used to processing.
    num_threads = 2

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'c:tn:', ['collections=', 'multi-threaded=', 'num-threads='])
    except getopt.GetoptError:
        sys.exit(2)

    if len(opts) < 1:
        print "Correct usage:", __file__, "-c <CSL of collections [business,user,checkin,photo,tip,review]> " \
                                          "-t <enables multi-threaded bulk> " \
                                          "-n <number of threads>"
        sys.exit(2)

    coll_names = []
    for opt, arg in opts:
        if opt in ('-c', '--collections'):
            coll_names = map(lambda x: x.strip(), arg.split(','))
        elif opt in ('-t', '--multi-threaded'):
            is_mt = True
        elif opt in ('-n', '--num-threads'):
            num_threads = int(arg)
        else:
            print "Correct usage:", __file__, "-c <CSL of collections [business,user,checkin,photo,tip,review]> " \
                                              "-t <enables multi-threaded bulk> " \
                                              "-n <number of threads>"
            sys.exit(2)

    # https://github.com/apanimesh061/elasticsearch-sentiment-plugin/blob/master/README.md
    sentiment_analyzer_ingestion_pipeline_id = 'sentiment-analyzer'

    # Destination index name.
    # Schema in ./es_mappings/yelp_mapping.json
    index_name = 'yelp_index'

    """
    > use yelp;
    switched to db yelp
    > show collections;
    business
    checkin
    photo_business
    review
    tip
    users
    > db.business.count()
    77445
    > db.photo_business.count()
    200000
    > db.checkin.count()
    55569
    > db.review.count()
    2225213
    > db.tip.count()
    591864
    > db.users.count()
    552339
    """
    database_name = 'yelp'

    try:
        client = MongoClient(host='localhost', port=27017, serverSelectionTimeoutMS=1500)
    except errors.ServerSelectionTimeoutError as err:
        sys.exit(2)

    db = client[database_name]
    sys.stdout.write("Connected to MongoDB Client\n")

    es_client = elasticsearch.Elasticsearch(hosts=[{"host": "localhost", "port": 9200}])
    sys.stdout.write("Connected to ElasticSearch Client\n")

    # Instantiate extractor object.
    extractor = Extract(extract_client=client, database_name=db, batch_size=750)

    # Instantiate loader object.
    loader = Load(load_client=es_client, index_name=index_name, extractor=extractor, bulk_size=750)
    if is_mt:
        loader.enable_multithreading()
        loader.set_no_of_threads(num_threads)

    for coll_name in coll_names:
        sys.stdout.write("\nIndexing " + coll_name + "...\n")
        start = timeit.default_timer()
        collection_type = None
        if coll_name == 'user':
            collection_type = Collection.User
        elif coll_name == 'checkin':
            collection_type = Collection.CheckIn
        elif coll_name == 'photo':
            collection_type = Collection.Photo
        elif coll_name == 'business':
            collection_type = Collection.Business
        elif coll_name == 'tip':
            collection_type = Collection.Tip
            loader.enable_ingestion_pipeline(sentiment_analyzer_ingestion_pipeline_id)
        elif coll_name == 'review':
            collection_type = Collection.Review
            loader.enable_ingestion_pipeline(sentiment_analyzer_ingestion_pipeline_id)
        else:
            sys.stderr.write("\nInvalid collection name: " + coll_name)
            sys.stderr.write("\nIgnoring...\n")
            continue
        extractor.set_current_collection(collection_type)
        loader.set_current_collection(collection_type)
        loader.start_streaming()
        end = timeit.default_timer()
        sys.stdout.write("\nTime taken for " + coll_name + " ingestion : " + str(end - start) + " seconds.\n")
