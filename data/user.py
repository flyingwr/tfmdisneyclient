import mongoengine


class User(mongoengine.Document):
    key = mongoengine.StringField(required=True)
    uuid = mongoengine.UUIDField(binary=False, null=True, required=True)
    
    premium_level = mongoengine.StringField(default="SILVER", required=True)
    
    browser_access = mongoengine.BooleanField(default=True)
    browser_access_token = mongoengine.StringField(null=True)

    meta = { "collection": "users" }