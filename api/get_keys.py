from aiohttp import web
from services.mongodb import find_map_by_key


import infrastructure
import server


class GetKeys(web.View):
	async def get(self):
		response = { "success": False }

		key = None

		agent = self.request.headers.get("User-Agent")
		addr = "127.0.0.1" if infrastructure.is_local else self.request.headers.get("X-Forwarded-For")

		access_token = self.request.query.get("access_token")

		access_token = server.check_conn(access_token, addr)
		if access_token is None:
			response["error"] = "invalid query: `access_token` parameter missing"

			status = 400
		elif access_token:
			level = infrastructure.tokens[access_token]["level"]

			key = infrastructure.tokens[access_token]["key"]
			limit = infrastructure.config["platinum_conn_limit"] if key in infrastructure.config["high_perm"] \
				else infrastructure.config["default_conn_limit"]

			passed = True
			if addr not in infrastructure.tokens[access_token]["ips"]:
				if len(infrastructure.tokens[access_token]["ips"]) < limit:
					infrastructure.tokens[access_token]["ips"].append(addr)
				else:
					response["error"] = "connection limit exceeded"

					passed = False

			if passed:
				response["success"] = True

				keys = infrastructure.parser.keys()
				
				if level in ("FREE", "BRONZE"):
					del keys["SILVER"]
					del keys["GOLD"]
					del keys["PLATINUM"]

					if level == "FREE":
						del keys["BRONZE"]
				elif level == "SILVER":
					del keys["GOLD"]
					del keys["PLATINUM"]
				elif level in ("GOLD", "GOLD2"):
					del keys["PLATINUM"]

				response["keys"] = {
					"maps_allowed": bool(find_map_by_key(key)),
					"client_version": infrastructure.config["client_version"],
					"discord": infrastructure.discord.discord_name,
					"premium_level": level
				}
				for v in keys.values():
					response["keys"].update(v)

				status = 200
		else:
			response["error"] = "expired/invalid token"

			status = 401

		if key != "pataticover":
			infrastructure.loop.create_task(infrastructure.discord.log("TFM", response, status, addr, key, access_token, agent))

		return web.json_response(response, status=status)