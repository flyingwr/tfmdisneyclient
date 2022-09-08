from aiohttp import web
from data import client

import infrastructure
import server

class Fetch(web.View):
	async def get(self):
		response = dict(success=False)
		status = 401

		agent = self.request.headers.get("User-Agent")
		cookies = self.request.cookies

		session_token = cookies.get("session")
		if (session := infrastructure.sessions.get(session_token)) is not None:
			key, user, access_token = session
			response["user"] = {
				"key": key,
				"premium_level": user.level,
				"access_token": access_token,
				"maps_allowed": bool(client.find_map_by_key(key, True))
			}

			status = 200
		else:
			response["error"] = "unauthorized"

		return web.json_response(response, status=status)