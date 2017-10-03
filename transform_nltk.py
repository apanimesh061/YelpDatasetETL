# -*- coding: utf-8 -*-

from nltk.sentiment.vader import SentimentIntensityAnalyzer

"""
This class has static methods that help in transforming a given input json document into
a document that conforms with the mapping of the Elasticsearch index.
"""


class Transform(object):
    def __init__(self):
        pass

    @staticmethod
    def business(input_json):
        time_slots = []
        for day_name, slots in input_json["hours"].iteritems():
            new_hours = dict()
            new_hours["day"] = day_name
            new_hours["opening_time"] = slots["open"]
            new_hours["closing_time"] = slots["close"]
            time_slots.append(new_hours)
        input_json.pop("hours")
        input_json.pop("_id")
        input_json["location"] = {
            "lat": input_json["latitude"],
            "lon": input_json["longitude"],
        }
        input_json.pop("latitude")
        input_json.pop("longitude")
        input_json["_id"] = input_json["business_id"]
        input_json.pop("business_id")
        input_json.update({"opening_hours": time_slots})
        return input_json

    @staticmethod
    def checkin(input_json):
        all_checkins = []
        for time_day_pair, count in input_json["checkin_info"].iteritems():
            time, day = time_day_pair.split('-')
            if int(time) < 10:
                time = '0' + time
            window_start = time + ":00"
            all_checkins.append({
                "window_start": window_start,
                "day": int(day),
                "count": count
            })

        return {
            "_parent": input_json["business_id"],
            "checkin_info": all_checkins
        }

    @staticmethod
    def tip(input_json, sentiment_model=None):
        sentiment = sentiment_model.polarity_scores(text=input_json["text"])
        return {
            "_parent": input_json["business_id"],
            "content": input_json["text"],
            "polarity": {
                "positive": sentiment["pos"],
                "negative": sentiment["neg"],
                "neutral": sentiment["neu"],
                "compound": sentiment["compound"],
            },
            "tip_user_id": input_json["user_id"],
            "tip_date": input_json["date"],
            "likes": input_json["likes"]
        }

    @staticmethod
    def user(input_json):
        return {
            "_id": input_json["user_id"],
            "name": input_json["name"],
            "user_review_count": input_json["review_count"],
            "average_stars": input_json["average_stars"],
            "user_votes": [{"vote_type": i, "count": j} for i, j in input_json["votes"].iteritems()],
            "friends": input_json["friends"],
            "yelping_since": input_json["yelping_since"],
            "elite": input_json["elite"],
            "compliments": [{"compliment_type": i, "num_compliments": j} for i, j in input_json["votes"].iteritems()],
            "fans": input_json["fans"]
        }

    @staticmethod
    def review(input_json, sentiment_model=None):
        sentiment = sentiment_model.polarity_scores(text=input_json["text"])
        return {
            "_parent": input_json["business_id"],
            "_id": input_json["review_id"],
            "review_user_id": input_json["user_id"],
            "review_stars": input_json["stars"],
            "content": input_json["text"],
            "polarity": {
                "positive": sentiment["pos"],
                "negative": sentiment["neg"],
                "neutral": sentiment["neu"],
                "compound": sentiment["compound"],
            },
            "review_date": input_json["date"],
            "review_votes": [{"vote_type": i, "count": j} for i, j in input_json["votes"].iteritems()]
        }

    @staticmethod
    def photo(input_json):
        current_caption = input_json.get("caption", "")
        current_label = input_json.get("label", "")
        current_neuraltalk_caption = input_json.get("neuraltalk_caption", "")
        return {
            "_parent": input_json["business_id"],
            "_id": input_json["photo_id"],
            "caption": current_caption if current_caption else "",
            "label": current_label if current_label else "",
            "neuraltalk_caption": current_neuraltalk_caption if current_neuraltalk_caption else "",
        }


class Collection(object):
    class Review(object):
        source = "review"
        destination = "review"

        @staticmethod
        def transformer(input_json):
            return Transform.review(input_json, SentimentIntensityAnalyzer())

    class Business(object):
        source = "business"
        destination = "business"

        @staticmethod
        def transformer(input_json):
            return Transform.business(input_json)

    class User(object):
        source = "users"
        destination = "user"

        @staticmethod
        def transformer(input_json):
            return Transform.user(input_json)

    class Tip(object):
        source = "tip"
        destination = "tip"

        @staticmethod
        def transformer(input_json):
            return Transform.tip(input_json, SentimentIntensityAnalyzer())

    class CheckIn(object):
        source = "checkin"
        destination = "checkin"

        @staticmethod
        def transformer(input_json):
            return Transform.checkin(input_json)

    class Photo(object):
        source = "photo_business"
        destination = "photo"

        @staticmethod
        def transformer(input_json):
            return Transform.photo(input_json)
