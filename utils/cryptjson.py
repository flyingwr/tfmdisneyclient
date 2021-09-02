from typing import AnyStr, Dict, List, Union
import base64, ujson, zlib

def json_zip(j: Union[Dict, List]) -> AnyStr:
	return base64.b64encode(
		zlib.compress(
			ujson.dumps(j).encode("utf-8")
		)
	)

def json_unzip(j: AnyStr) -> Union[Dict, List]:
	return ujson.loads(
		zlib.decompress(
			base64.b64decode(j)
		)
	)

def maps_encode(i: Dict) -> AnyStr:
	return "#".join(
		(f"{code}:{info}" for code, info in _map.data.items())
	).encode()

def maps_decode(i: AnyStr) -> Dict:
	maps = {}
	for s in text_decode(i).split(b"#"):
		search = map_pattern.search(s)
		if search:
			maps[search.group(1)] = search.group(2)
	return maps

def text_encode(t: AnyStr) -> AnyStr:
	if isinstance(t, str):
		t = t.encode()
		
	return base64.b64encode(
		zlib.compress(t)
	)

def text_decode(t: AnyStr) -> AnyStr:
	return zlib.decompress(
		base64.b64decode(t)
	)