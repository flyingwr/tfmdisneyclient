from aiohttp import web
from services.mongodb import find_config_by_key, set_config


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
				body = infrastructure.tokens[access_token].get("soft", b"")
			elif self.request.query.get("protected") is not None:
				with open("./public/protectedmaps.json", "rb") as f:
					body = f.read()
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
				if infrastructure.tokens[access_token]["level"] == "PLATINUM":
					infrastructure.tokens[access_token]["soft"] = soft.encode()

			if config is not None:
				set_config(infrastructure.tokens[access_token]["key"], ujson.loads(config))
		else:
			raise web.HTTPUnauthorized()
		
		raise web.HTTPNoContent()

	async def put(self):
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			raise web.HTTPBadRequest()
		elif access_token:
			post = await self.request.post()
			soft = post.get("soft")
			if soft is not None:
				if infrastructure.tokens[access_token]["level"] == "PLATINUM":
					infrastructure.tokens[access_token]["soft"] = soft.encode()
			raise web.HTTPNoContent()
					
		raise web.HTTPUnauthorized()