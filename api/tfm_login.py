from aiohttp import web

import infrastructure
import server

class TfmLogin(web.View):
	async def get(self):
		username = self.request.query.get("username")
		addr = self.request.headers.get("X-Forwarded-For")

		access_token = self.request.query.get("access_token")
		access_token = server.check_conn(access_token, addr)

		key = None
		log = True

		if access_token:
			if (info := infrastructure.tokens.get(access_token)):
				key = info["key"]
				log = not info["user"].key_hidden

		if log:
			infrastructure.loop.create_task(infrastructure.discord.log2(username, key, access_token))

		raise web.HTTPNoContent()