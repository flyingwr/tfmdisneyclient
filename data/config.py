import mongoengine


class Config(mongoengine.Document):
    key = mongoengine.StringField(required=True)

    tfm_menu = mongoengine.DictField(null=True)

    meta = { "collection": "config" }