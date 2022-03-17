import infrastructure
import mongoengine
import os


mongoengine.connect(host=os.getenv("MONGODB_URL"))


from .blacklist import Blacklist
infrastructure.blacklisted_ips = [obj.addr for obj in Blacklist.objects().only("addr")]
