from aiohttp import web
from services.mongodb import find_map_by_key
from utils import cryptjson, pasteee


import aiofiles
import infrastructure
import re
import server


ls_pattern = re.compile(br"(@\d+):")
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

		_map = find_map_by_key(infrastructure.tokens[access_token]["key"])
		if _map:
			if isinstance(_map.data, bytes):
				return web.Response(body=_map.data)
			else:
				return web.Response(body=cryptjson.text_encode(
					cryptjson.maps_encode(_map.data)))

		async with aiofiles.open("./public/maps.json", "rb") as f:
			return web.Response(body=await f.read())
				
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

		level = infrastructure.tokens[access_token]["level"]
		if level in infrastructure.config["storage_allowed_levels"]:
			_map = find_map_by_key(infrastructure.tokens[access_token]["key"])
			if _map:
				if method == "ls":
					result = infrastructure.tokens[access_token].get("lsmap")
					if not result:
						result = await pasteee.new_paste(", ".join(_map.data.keys()))
						infrastructure.tokens[access_token]["lsmap"] = result
						infrastructure.loop.create_task(infrastructure.del_lsmap(access_token))

					return web.Response(body=result.encode())
				elif method in ("del", "save"):
					if method == "del":
						if code in _map.data:
							del _map.data[code]
					else:
						_map.data[code] = info
					_map.save()

					raise web.HTTPNoContent()

				raise web.HTTPBadRequest()

		raise web.HTTPForbidden()