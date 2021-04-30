from mongoengine import (
    StringField,
    LongField,
    BooleanField,
    IntField,
    ReferenceField, DynamicDocument, DynamicEmbeddedDocument, EmbeddedDocumentField,
)

from entities.news import NewsContent


class User(DynamicEmbeddedDocument):
    pass


class Tweet(DynamicDocument):
    id = LongField()
    created_at = StringField()
    news = ReferenceField(NewsContent)
    retweet_count = IntField()
    favorite_count = IntField()
    favorited = BooleanField()
    retweeted = BooleanField()
    user = EmbeddedDocumentField(User)

    meta = {
        'allow_inheritance': True,
    }


class Retweet(Tweet):
    retweeted_status = ReferenceField(Tweet)
