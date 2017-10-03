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
