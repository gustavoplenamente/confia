from mongoengine import (
    EmbeddedDocument,
    URLField,
    StringField,
    ListField,
    IntField,
    EmbeddedDocumentListField, LongField, BooleanField, EmbeddedDocumentField,
)


class UserUrls(EmbeddedDocument):
    url = URLField()
    expanded_url = URLField()
    display_url = StringField()
    indices = ListField(IntField())


class UserEntity(EmbeddedDocument):
    urls = EmbeddedDocumentListField(UserUrls)


class UserEntities(EmbeddedDocument):
    url = EmbeddedDocumentField(UserEntity)
    description = EmbeddedDocumentField(UserEntity)


class User(EmbeddedDocument):
    id = LongField()
    id_str = StringField()
    name = StringField()
    screen_name = StringField()
    location = StringField()
    description = StringField()
    url = URLField()
    entities = EmbeddedDocumentField(UserEntities)
    protected = BooleanField()
    followers_count = IntField()
    friends_count = IntField()
    listed_count = IntField()
    created_at = StringField()
    favourites_count = IntField()
    utc_offset = StringField()
    time_zone = StringField()
    geo_enabled = BooleanField()
    verified = BooleanField()
    statuses_count = IntField()
    lang = StringField()
    contributors_enabled = BooleanField()
    is_translator = BooleanField()
    is_translation_enabled = BooleanField()
    profile_background_color = StringField()
    profile_background_image_url = URLField()
    profile_background_image_url_https = URLField()
    profile_background_tile = BooleanField()
    profile_image_url = URLField()
    profile_image_url_https = URLField()
    profile_banner_url = URLField()
    profile_link_color = StringField()
    profile_sidebar_border_color = StringField()
    profile_sidebar_fill_color = StringField()
    profile_text_color = StringField()
    profile_use_background_image = BooleanField()
    has_extended_profile = BooleanField()
    default_profile = BooleanField()
    default_profile_image = BooleanField()
    following = BooleanField()
    follow_request_sent = BooleanField()
    notifications = BooleanField()
    translator_type = StringField()
