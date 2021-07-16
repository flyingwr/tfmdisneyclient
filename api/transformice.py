from aiohttp import web


import server


class Transformice(web.View):
	async def get(self):
		if self.request.query.get("swf") is not None:
			return web.FileResponse("./tfm.swf")

		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")
		if server.check_conn(access_token, addr):
			return web.FileResponse("./public/ChargeurTransformice.swf")

		return web.FileResponse("./public/invalid.swf")