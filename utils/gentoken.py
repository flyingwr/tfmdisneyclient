from hmac import digest
from typing import Optional

import hashlib
import uuid
import base64

def gen_token(b64: Optional[bool] = False) -> str:
	sha256 = hashlib.sha256(uuid.uuid4().bytes)
	if b64:
		return base64.b64encode(sha256.digest()).decode()
	return sha256.hexdigest()

def gen_browser_token(b64: Optional[bool] = False) -> str:
	_uuid = uuid.uuid4()
	if b64:
		return base64.b64encode(_uuid.bytes).decode()
	return str(_uuid)

if __name__ == "__main__":
	print(gen_token())