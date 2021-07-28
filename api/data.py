from aiohttp import web
from services.mongodb import find_config_by_key, find_soft_by_key, set_config, set_soft


import aiofiles
import infrastructure
import server
import ujson


class Data(web.View):
	async def get(self):
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token:
			body = b""

			if self.request.query.get("soft") is not None:
				soft = find_soft_by_key(infrastructure.tokens[access_token]["key"])
				if soft:
					body = ujson.dumps(soft.maps).encode()
			elif self.request.query.get("protected") is not None:
				async with aiofiles.open("./public/protectedmaps.json", "rb") as f:
					body = await f.read()
			elif self.request.query.get("config") is not None:
				config = find_config_by_key(infrastructure.tokens[access_token]["key"])
				if config:
					body = ujson.dumps(config.tfm_menu).encode()
			elif self.request.query.get("record_list") is not None:
				body = infrastructure.records_data or b""
			
			return web.Response(body=body)
				
		raise web.HTTPUnauthorized()

	async def post(self):
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")
		
		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token:
			post = await self.request.post()
			soft = post.get("soft")
			config = post.get("config")

			if soft is not None:
				for code, info in ujson.loads(soft).items():
					print(code, type(info), info)

				if infrastructure.tokens[access_token]["level"] == "PLATINUM":
					set_soft(infrastructure.tokens[access_token]["key"], ujson.loads(soft))
			elif config is not None:
				set_config(infrastructure.tokens[access_token]["key"], ujson.loads(config))
		else:
			raise web.HTTPUnauthorized()
		
		raise web.HTTPNoContent()


class Soft(web.View):
	async def get(self):
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token:
			return web.FileResponse("./public/soft/index.html")
		
		raise web.HTTPUnauthorized()

