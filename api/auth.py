from aiohttp import web

class Auth(web.View):
	async def get(self):
		raise web.HTTPFound(f"{self.request.app.router['auth'].url_for()}?{self.request.query_string}")