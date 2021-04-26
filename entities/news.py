from mongoengine import *

from entities.news_metadata import NewsMetadata
from entities.tweet import Tweet, Retweet


class NewsContent(EmbeddedDocument):
    url = URLField()
    text = StringField()
    images = ListField(ImageField())
    top_img = ImageField()
    keyword = ListField(StringField())
    authors = ListField(StringField())
    canonical_link = URLField()
    title = StringField()
    meta_data = EmbeddedDocumentField(NewsMetadata)
    movies = ListField(StringField())
    publish_date = DateField()
    source = URLField()
    summary = StringField()


class News(Document):
    news_content = EmbeddedDocumentField(NewsContent)
    tweets = EmbeddedDocumentListField(Tweet)
    retweets = EmbeddedDocumentListField(Retweet)
