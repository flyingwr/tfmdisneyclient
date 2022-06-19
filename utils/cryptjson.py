from typing import AnyStr, Dict, List, Union
import base64, ujson, zlib

def json_zip(j: Union[Dict, List]) -> AnyStr:
	return base64.b64encode(
		zlib.compress(
			ujson.dumps(j).encode()
		)
	)

def json_unzip(j: AnyStr) -> Union[Dict, List]:
	return ujson.loads(
		zlib.decompress(
			base64.b64decode(j)
		)
	)

def text_encode(t: AnyStr) -> AnyStr:
	if isinstance(t, str):
		t = t.encode()
		
	return base64.b64encode(
		zlib.compress(t))

def text_decode(t: AnyStr) -> AnyStr:
	return zlib.decompress(
		base64.b64decode(t))