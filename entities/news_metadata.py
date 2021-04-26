from mongoengine import (
    EmbeddedDocument,
    LongField,
    StringField,
    ImageField,
    EmbeddedDocumentField,
)


class FacebookMetadata(EmbeddedDocument):
    app_id = LongField()


class OpenGraphMetadata(EmbeddedDocument):
    url = StringField()
    type = StringField()
    title = StringField()
    description = StringField()
    image = ImageField()


class NewsMetadata(EmbeddedDocument):
    viewport = StringField()
    facebook_app_id = StringField()
    fb = EmbeddedDocumentField(FacebookMetadata)
    og = EmbeddedDocumentField(OpenGraphMetadata)
