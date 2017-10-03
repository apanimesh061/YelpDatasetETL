# -*- coding: utf-8 -*-

from transform import Transform

"""
This class represents one Collection in the data source MongoDB.
For evey collection:
source: Mongo collection name
destination: Elasticsearch document type
"""


class Collection(object):
    class Review(object):
        source = "review"
        destination = "review"

        @staticmethod
        def apply_transform():
            return Transform.review

    class Business(object):
        source = "business"
        destination = "business"

        @staticmethod
        def apply_transform():
            return Transform.business

    class User(object):
        source = "users"
        destination = "user"

        @staticmethod
        def apply_transform():
            return Transform.user

    class Tip(object):
        source = "tip"
        destination = "tip"

        @staticmethod
        def apply_transform():
            return Transform.tip

    class CheckIn(object):
        source = "checkin"
        destination = "checkin"

        @staticmethod
        def apply_transform():
            return Transform.checkin

    class Photo(object):
        source = "photo_business"
        destination = "photo"

        @staticmethod
        def apply_transform():
            return Transform.photo
