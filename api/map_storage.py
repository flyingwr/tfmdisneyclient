from aiohttp import web
from services.mongodb import find_map_by_key
from utils import cryptjson


import aiofiles
import infrastructure
import re
import server


map_pattern = re.compile(b"(.*?):(.*)")
map_pattern2 = re.compile(b"#$")


class MapStorage(web.View):
	def check_conn(self):
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = server.check_conn(access_token, addr)
		if access_token is not None:
			addr = self.request.headers.get("X-Forwarded-For")
			if addr in infrastructure.ips:
				access_token = infrastructure.ips[addr][1]
		else:
			return None

		return access_token if (
			access_token is not None or access_token in infrastructure.tokens
		) else False
		
	async def get(self):
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token == False:
			raise web.HTTPUnauthorized()

		# _map = find_map_by_key(infrastructure.tokens[access_token]["key"])
		# if _map:
		# 	return web.Response(body=_map.data)

		if infrastructure.tokens[access_token]["level"] in infrastructure.config["storage_allowed_levels"]:
			async with aiofiles.open("./public/maps.json", "rb") as f:
				return web.Response(body=await f.read())

		raise web.HTTPForbidden()
				
	async def post(self):
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token == False:
			raise web.HTTPUnauthorized()

		data = await self.request.post()
		code, info = data.get("code"), data.get("info")
		
		method = self.request.query.get("method")

		if infrastructure.tokens[access_token]["level"] in infrastructure.config["storage_allowed_levels"]:
			_map = find_map_by_key(infrastructure.tokens[access_token]["key"])
			if _map:
				if method in ("del", "save"):
					if code:
						data_decoded = cryptjson.text_decode(_map.data)
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

						_map.update(data=cryptjson.text_encode(map_pattern2.sub(
							b"", data_decoded.replace(b"##", b"#"))))

						raise web.HTTPNoContent()

				raise web.HTTPBadRequest()

		raise web.HTTPForbidden()