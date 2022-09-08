from aiohttp import web
from data import client

import aiofiles
import infrastructure
import server
import ujson

class Data(web.View):
	async def get(self):
		access_token = self.request.query.get("access_token")
		flash_token = self.request.query.get("flash_token")
		addr = self.request.headers.get("X-Forwarded-For")

		if (access_token := server.check_conn(access_token, addr, flash_token=flash_token)) is None:
			raise web.HTTPBadRequest()
		elif access_token:
			body = b""

			if self.request.query.get("soft") is not None:
				if (soft := client.find_soft_by_key(infrastructure.tokens[access_token]["key"])):
					body = soft.data
			elif self.request.query.get("protected") is not None:
				async with aiofiles.open("./public/protectedmaps.json", "rb") as f:
					body = await f.read()
			elif self.request.query.get("config") is not None:
				if (config := client.find_config_by_key(infrastructure.tokens[access_token]["key"])):
					body = ujson.dumps(config.tfm_menu).encode()
			elif self.request.query.get("record_list") is not None:
				body = infrastructure.records_data or b""
			
			return web.Response(body=body)
				
		raise web.HTTPUnauthorized()

	async def post(self):
		access_token = self.request.query.get("access_token")
		flash_token = self.request.query.get("flash_token")
		addr = "127.0.0.1" if infrastructure.is_local else self.request.headers.get("X-Forwarded-For")
		
		if self.request.path_qs.startswith("/data/soft"):
			access_token = server.check_conn(access_token, addr)
		else:
			access_token = server.check_conn(access_token, addr, flash_token=flash_token)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token:
			post = await self.request.post()
			soft = post.get("soft")
			config = post.get("config")

			if soft is not None:
				if infrastructure.tokens[access_token]["level"] == "PLATINUM":
					client.set_soft(infrastructure.tokens[access_token]["key"], soft.encode())
			elif config is not None:
				client.set_config(infrastructure.tokens[access_token]["key"], ujson.loads(config))
		else:
			raise web.HTTPUnauthorized()
		
		raise web.HTTPNoContent()

class Soft(web.View):
	async def get(self):
		access_token = self.request.query.get("access_token")
		addr = "127.0.0.1" if infrastructure.is_local else self.request.headers.get("X-Forwarded-For")

		if (access_token := server.check_conn(access_token, addr)) is None:
			raise web.HTTPBadRequest()
		elif access_token:
			if infrastructure.tokens[access_token]["level"] == "PLATINUM":
				return web.FileResponse("./public/soft/index.html")
			raise web.HTTPForbidden()
		
		raise web.HTTPUnauthorized()