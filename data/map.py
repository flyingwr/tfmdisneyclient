import mongoengine


class Map(mongoengine.Document):
    key = mongoengine.StringField(required=True)

    data = mongoengine.BinaryField(required=True)

    meta = { "collection": "maps" }