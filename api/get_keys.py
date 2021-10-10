from aiohttp import web
from services.mongodb import find_map_by_key


import infrastructure
import server


class GetKeys(web.View):
	async def get(self):
		response = { "success": False }

		key = None

		status = 401

		addr = "127.0.0.1" if infrastructure.is_local else self.request.headers.get("X-Forwarded-For")
		agent = self.request.headers.get("User-Agent")
		access_token = self.request.query.get("access_token")

		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			response["error"] = "invalid query: `access_token` parameter missing"

			status = 400
		elif access_token:
			info = infrastructure.tokens[access_token]
			level = info["level"]

			key = info["key"]

			passed = True
			if addr not in info["ips"]:
				if len(info["ips"]) < info["conn_limit"]:
					info["ips"].append(addr)
				else:
					response["error"] = "connection limit exceeded"

					passed = False

			if passed:
				response["success"] = True
				response["keys"] = {
					"maps_allowed": False, # bool(find_map_by_key(key, True)),
					"client_version": infrastructure.config["client_version"],
					"discord": infrastructure.discord.discord_name,
					"premium_level": level
				}

				async with infrastructure.session.get(
					f"{infrastructure.parser_url}/api/tfm_keys?token={infrastructure.tfm_parser_token}&level={level}"
				) as _response:
					if _response.status == 200:
						response["keys"].update(await _response.json())

				status = 200
		else:
			response["error"] = "expired/invalid token"

		if key != "pataticover":
			infrastructure.loop.create_task(infrastructure.discord.log("TFM", response, status, addr, key, access_token, agent))

		return web.json_response(response, status=status)