import mongoengine


class User(mongoengine.Document):
    key = mongoengine.StringField(required=True)

    uuid = mongoengine.UUIDField(binary=False, null=True)
    premium_level = mongoengine.StringField(default="SILVER")
    
    browser_access = mongoengine.BooleanField(required=True, default=False)

    meta = { "collection": "users" }