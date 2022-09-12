from aiohttp import streamer
from aiohttp import web
from data import client
from io import BytesIO
from utils import cryptjson

import aiofiles
import infrastructure
import re
import server

map_pattern2 = re.compile(b"#$")

@streamer
async def data_sender(writer, **kwargs):
	if (file_path := kwargs.get("file_path")) is not None:
		with open(file_path, "rb") as f:
			while (chunk := f.read(2 ** 16)):
				await writer.write(chunk)
	elif (data := kwargs.get("data")) is not None:
		while (chunk := data.read(2 ** 16)):
			await writer.write(chunk)

class MapStorage(web.View):
	def check_req(self):
		agent = self.request.headers.get("User-Agent")
		accept = self.request.headers.get("Accept")
		flash_version = self.request.headers.get("x-flash-version")

		host = self.request.headers.get("Host")
		trust_host = host.startswith("localhost") or host == "tfmdisneyclient.herokuapp.com"

		referer = self.request.headers.get("Referer")
		trust_ref = referer is None or any(referer.startswith(s) for s in ("http://localhost", "https://localhost", "http://tfmdisneyclient.herokuapp.com", "https://tfmdisneyclient.herokuapp.com"))

		if not agent or (agent != "Shockwave Flash" and ".NET" not in agent) \
			or not accept or (accept != "*/*" and "application/x-shockwave-flash" not in accept) \
			or not flash_version or "," not in flash_version or not trust_ref or not trust_host:
				return False
		return True
		
	async def get(self):
		access_token = self.request.query.get("access_token")
		flash_token = self.request.query.get("flash_token")
		addr = self.request.headers.get("X-Forwarded-For")

		if (session_token := self.request.cookies.get("session")) is None:
			access_token = server.check_conn(access_token, addr, flash_token=flash_token)
		else:
			access_token = server.check_conn(access_token, addr, session_token=session_token)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token == False:
			raise web.HTTPUnauthorized()

		if infrastructure.config["map_storage_fetch"]:
			if (_map := client.find_map_by_key(infrastructure.tokens[access_token]["key"])):
				data = _map.data
				return web.Response(body=data)

		if infrastructure.tokens[access_token]["level"] in infrastructure.config["storage_allowed_levels"]:
			return web.Response(body=data_sender(file_path="./public/maps.json"))

		raise web.HTTPForbidden()
				
	async def post(self):
		access_token = self.request.query.get("access_token")
		flash_token = self.request.query.get("flash_token")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = server.check_conn(access_token, addr, flash_token=flash_token)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token == False:
			raise web.HTTPUnauthorized()

		data = await self.request.post()
		code, info = data.get("code"), data.get("info")
		
		method = self.request.query.get("method")

		if infrastructure.tokens[access_token]["level"] in infrastructure.config["storage_allowed_levels"]:
			_map = client.find_map_by_key(infrastructure.tokens[access_token]["key"])
			if _map:
				if method in ("del", "save"):
					if code:
						data_decoded = cryptjson.text_decode(_map.data) if _map.data else b""
						_search = re.search(b"%s:([^#]*)" % code.encode(), data_decoded)

						if method == "save":
							if info:
								if _search:
									data_decoded = data_decoded.replace(
										_search.group(),
										b"%s:%s" % (code.encode(), cryptjson.text_decode(info))
									)
								else:
									data_decoded += b"#%s:%s" % (code.encode(), cryptjson.text_decode(info))
							else:
								raise web.HTTPBadRequest()
						elif method == "del":
							if _search:
								data_decoded = data_decoded.replace(_search.group(), b"")

						_map.data = cryptjson.text_encode(map_pattern2.sub(
							b"", data_decoded.replace(b"##", b"#")))
						client.commit()

						raise web.HTTPNoContent()
				raise web.HTTPBadRequest()
		raise web.HTTPForbidden()