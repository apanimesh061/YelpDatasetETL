# YelpDatasetETL
A MongoDb to Elasticsearch ETL pipeline

This project is mini ETL pipeline that is able to stream documents from a Mongodb collection to an Elasticsearch index after applying two layers of transformations.

 - First transformation is done to convert the Mongo Bson to a Json that conforms with the Elasticsearch schema defined [here](https://github.com/apanimesh061/YelpDatasetETL/blob/master/es_mappins/yelp_mapping.json).
 - Second transformation is performed on selected collections that text fields on which a VADER sentiment analyzer is applied.

#### VADER Sentiment Analyzer
In this project, this analyzer could be applied using two ways:
 - using the NLTK package tool `nltk.sentiment.vader.SentimentIntensityAnalyzer`
 - creating an ingestion plugin that does the analysis
 
The aim of the project was to create an ETL pipeline as well as learn about the [Ingestion pipeline](https://www.elastic.co/guide/en/elasticsearch/reference/5.2/ingest-apis.html) introduced in Elasticsearch 5.x.

----

Elasticsearch Version: 5.2.1

Python: 2.7.13

[VaderSentimentJava](https://github.com/apanimesh061/VaderSentimentJava): 1.0.1

[elasticsearch-sentiment-plugin](https://github.com/apanimesh061/elasticsearch-sentiment-plugin): 1.0.1

----
Dataset used:

[https://www.yelp.com/dataset](https://www.yelp.com/dataset)

    business - 77445 records
    photo_business - 200000 records
    checkin - 55569 records
    review - 2225213 records
    tip - 591864 records
    users - 552339 records

----
#### Usage

    $ python YelpEtlPipeline.py -c business,user,checkin,tip,photo,review -t -n 4 
    Connected to MongoDB Client                                      
    Connected to ElasticSearch Client                                

    Indexing business...                                             
    Indexed 77445 / 77445 documents with 0 failures                  
    Time taken for business ingestion : 65.8003674392 seconds.       

    Indexing user...                                                 
    Indexed 552339 / 552339 documents with 0 failures                
    Time taken for user ingestion : 433.517403755 seconds.           

    Indexing checkin...                                              
    Indexed 55569 / 55569 documents with 0 failures                  
    Time taken for checkin ingestion : 58.5147706969 seconds.        

    Indexing tip...                                                  
    Indexed 591864 / 591864 documents with 0 failures                
    Time taken for tip ingestion : 410.815298934 seconds.            

    Indexing photo...                                                
    Indexed 200000 / 200000 documents with 0 failures                
    Time taken for photo ingestion : 102.609901614 seconds.          

    Indexing review...                                               
    Indexed 2225213 / 2225213 documents with 0 failures              
    Time taken for review ingestion : 10633.6480628 seconds.         


