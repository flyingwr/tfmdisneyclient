import mongoengine


class Soft(mongoengine.Document):
    key = mongoengine.StringField(required=True)

    maps = mongoengine.DictField(null=True)

    meta = { "collection": "soft" }