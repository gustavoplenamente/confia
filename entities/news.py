from mongoengine import *


class NewsContent(DynamicDocument):
    classification = StringField()
    url = URLField()
    text = StringField()
    authors = ListField(StringField())
    canonical_link = URLField()
    title = StringField()
    publish_date = DateField()
