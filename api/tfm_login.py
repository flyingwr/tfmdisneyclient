from aiohttp import web


import infrastructure
import server


class TfmLogin(web.View):
	async def get(self):
		username = self.request.query.get("username")
		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")
		access_token = server.check_conn(access_token, addr)

		infrastructure.loop.create_task(infrastructure.discord.log2(
			username, infrastructure.tokens.get(access_token, {}).get("key"), access_token))

		raise web.HTTPNoContent()