from aiohttp import web


import os
import server


class Transformice(web.View):
	def check_req(self):
		agent = self.request.headers.get("User-Agent")
		accept = self.request.headers.get("Accept")
		flash_version = self.request.headers.get("x-flash-version")
		if not agent or (agent != "Shockwave Flash" and ".NET" not in agent) \
			or not accept or (accept != "*/*" and "application/x-shockwave-flash" not in accept) \
			or not flash_version or "," not in flash_version:
				return False
		return True

	async def get(self):
		if self.request.query.get("swf") is not None:
			if os.path.isfile("./tfm.swf"):
				return web.FileResponse("./tfm.swf")
				
			raise web.HTTPNoContent()

		if not self.check_req():
			raise web.HTTPBadRequest()

		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")
		if server.check_conn(access_token, addr):
			return web.FileResponse("./public/ChargeurTransformice.swf")

		return web.FileResponse("./public/invalid.swf")