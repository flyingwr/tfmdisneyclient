from aiohttp import web

import asyncio
import infrastructure
import os
import server

class Transformice(web.View):
	def check_req(self):
		agent = self.request.headers.get("User-Agent")
		accept = self.request.headers.get("Accept")
		flash_version = self.request.headers.get("x-flash-version")

		host = self.request.headers.get("Host")
		trust_host = host.startswith("localhost") or host == "tfmdisneyclient.herokuapp.com"

		referer = self.request.headers.get("Referer")
		trust_ref = referer is None or any(referer.startswith(s) for s in ("http://localhost", "https://localhost", "http://tfmdisneyclient.herokuapp.com", "https://tfmdisneyclient.herokuapp.com"))

		if not agent or (agent != "Shockwave Flash" and ".NET" not in agent) \
			or not accept or (accept != "*/*" and "application/x-shockwave-flash" not in accept) \
			or not flash_version or "," not in flash_version or not trust_ref or not trust_host:
				return False
		return True

	async def get(self):
		if self.request.query.get("swf") is not None:
			if os.path.isfile("./tfm.swf"):
				while os.path.getsize("./tfm.swf") != infrastructure.tfm_swf_expected_len:
					await asyncio.sleep(.5)
				return web.FileResponse("./tfm.swf")
			raise web.HTTPNoContent()

		if not self.check_req():
			raise web.HTTPBadRequest()

		access_token = self.request.query.get("access_token")
		addr = self.request.headers.get("X-Forwarded-For")
		if server.check_conn(access_token, addr):
			return web.FileResponse("./public/ChargeurTransformice.swf")
		return web.FileResponse("./public/invalid.swf")