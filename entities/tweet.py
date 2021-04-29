from mongoengine import (
    StringField,
    LongField,
    BooleanField,
    IntField,
    ReferenceField, DynamicDocument,
)

from entities.news import NewsContent


class Tweet(DynamicDocument):
    id = LongField()
    created_at = StringField()
    news = ReferenceField(NewsContent)
    retweet_count = IntField()
    favorite_count = IntField()
    favorited = BooleanField()
    retweeted = BooleanField()

    meta = {
        'allow_inheritance': True,
    }


class Retweet(Tweet):
    retweeted_status = ReferenceField(Tweet)
