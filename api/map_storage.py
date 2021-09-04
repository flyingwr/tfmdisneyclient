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
			return web.Response(body=_map.data)

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
				found_map_data = _map.data

				if method == "ls":
					result = infrastructure.tokens[access_token].get("lsmap")
					if not result:
						result = await pasteee.new_paste(", "
							.join(
								ls_pattern.findall(cryptjson.text_decode(found_map_data))
							).replace("@", "")
						)

						infrastructure.tokens[access_token]["lsmap"] = result
						infrastructure.loop.create_task(infrastructure.del_lsmap(access_token))

					return web.Response(body=result.encode())
				elif method in ("del", "save"):
					data_decoded = cryptjson.text_decode(found_map_data)
					_search = re.search(b"%s:([^#]*)" % code.encode(), data_decoded)

					if method == "save":
						if info:
							if code.encode() in data_decoded:
								if _search:
									if method == "save":
										data_decoded = data_decoded.replace(
											_search.group(),
											b"%s:%s" % (code.encode(), info.encode())
										)
								else:
									data_decoded += b"#%s:%s" % (code.encode(), info.encode())
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