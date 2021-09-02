import mongoengine


class Map(mongoengine.Document):
    key = mongoengine.StringField(required=True)

    data = mongoengine.DictField(default={})

    meta = { "collection": "maps" }