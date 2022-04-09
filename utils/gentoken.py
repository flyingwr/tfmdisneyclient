from typing import Optional

import uuid
import base64

def gen_token(b64: Optional[bool] = False) -> str:
	_uuid = uuid.uuid4()
	if b64:
		return base64.b64encode(_uuid.bytes).decode()
	return str(_uuid)