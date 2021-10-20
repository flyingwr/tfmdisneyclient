import mongoengine


class Blacklist(mongoengine.Document):
    addr = mongoengine.StringField(required=True)

    meta = { "collection": "blacklist" }
