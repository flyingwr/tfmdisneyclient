from aiohttp import web

import infrastructure

class Update(web.View):
	async def get(self):
		return web.json_response({
			"client_version": infrastructure.config.get("client_version"),
			"standalone_url": infrastructure.config.get("standalone_url"),
			"update_url": infrastructure.config.get("update_url"),
			"version": infrastructure.config.get("version")})