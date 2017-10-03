# -*- coding: utf-8 -*-

"""
This class has static methods that help in transforming a given input json document into
a document that conforms with the mapping of the Elasticsearch index.
"""


class Transform(object):
    @staticmethod
    def business(input_json):
        """
        :param input_json: Json representing a Yelp business.
        :return: transformed Json
        """
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
        """
        :param input_json: Json representing a CheckIn on Yelp.
        :return: transformed Json
        """
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
    def tip(input_json):
        """
        :param input_json: Json representing a Tip on Yelp
        :return:
        """
        return {
            "_parent": input_json["business_id"],
            "content": input_json["text"],
            "tip_user_id": input_json["user_id"],
            "tip_date": input_json["date"],
            "likes": input_json["likes"]
        }

    @staticmethod
    def user(input_json):
        """
        :param input_json: Json representing a User on Yelp
        :return: transformed Json
        """
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
    def review(input_json):
        """
        :param input_json: Json representing a Review on Yelp
        :return: transformed Json
        """
        return {
            "_parent": input_json["business_id"],
            "_id": input_json["review_id"],
            "review_user_id": input_json["user_id"],
            "review_stars": input_json["stars"],
            "content": input_json["text"],
            "review_date": input_json["date"],
            "review_votes": [{"vote_type": i, "count": j} for i, j in input_json["votes"].iteritems()]
        }

    @staticmethod
    def photo(input_json):
        """
        The Yelp Dataset had a set of business photos.
        Image Captioning tool "Neuratalk" was applied on each photo and was stored in MongoDB.
        Before the processing an image had one Caption and a Label associated with it, Neuraltalk
        had the capability to give an idea about what the image contained in case there was no caption.

        :param input_json: Json representing Neuraltalk caption for a photo.
        :return: transformed Json
        """
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
