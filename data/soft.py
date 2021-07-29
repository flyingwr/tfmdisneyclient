import mongoengine


class Soft(mongoengine.Document):
    key = mongoengine.StringField(required=True)

    maps = mongoengine.DictField(default={})

    meta = { "collection": "soft" }