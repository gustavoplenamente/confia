from mongoengine import (
    EmbeddedDocument,
    StringField,
    LongField,
    BooleanField,
    EmbeddedDocumentField,
    IntField,
    ListField,
    EmbeddedDocumentListField,
    URLField,
)

from entities.user import User


class UserMention(EmbeddedDocument):
    screen_name = StringField()
    name = StringField()
    id = LongField()
    id_str = StringField()
    indices = ListField(IntField())


class TweetEntities(EmbeddedDocument):
    hashtags = ListField(StringField())
    symbols = ListField(StringField())
    user_mentions = EmbeddedDocumentListField(UserMention)
    urls = ListField(URLField)


class Tweet(EmbeddedDocument):
    created_at = StringField()
    id = LongField()
    id_str = StringField()
    text = StringField()
    truncated = BooleanField()
    entities = EmbeddedDocumentField(TweetEntities)
    source = StringField()
    in_reply_to_status_id = LongField()
    in_reply_to_status_id_str = StringField()
    in_reply_to_user_id = LongField()
    in_reply_to_user_id_str = StringField()
    in_reply_to_screen_name = StringField()
    user = EmbeddedDocument(User)
    geo = None
    coordinates = None
    place = None
    is_quote_status = BooleanField()
    retweet_count = IntField()
    favorite_count = IntField()
    favorited = BooleanField()
    retweeted = BooleanField()
    lang = StringField()


class Retweet(Tweet):
    retweeted_status = EmbeddedDocumentField(Tweet)
