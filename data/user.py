import mongoengine


class User(mongoengine.Document):
    key = mongoengine.StringField(required=True)
    uuid = mongoengine.UUIDField(binary=False, null=True)
    
    premium_level = mongoengine.StringField(default="SILVER")
    
    browser_access = mongoengine.BooleanField(default=True)
    browser_access_token = mongoengine.StringField(null=True)

    connection_limit = mongoengine.IntField(default=1)

    meta = { "collection": "users" }