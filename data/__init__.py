from dotenv import load_dotenv
load_dotenv()


import infrastructure
import mongoengine
import os


if infrastructure.is_local:
    from ssl import CERT_NONE
    mongoengine.connect(host=os.getenv("MONGODB_URL"), ssl_cert_reqs=CERT_NONE)
else:
    mongoengine.connect(host=os.getenv("MONGODB_URL"))