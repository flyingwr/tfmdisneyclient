from aiohttp import web
from data import client

import infrastructure
import server

class GetKeys(web.View):
	def check_req(self):
		agent = self.request.headers.get("User-Agent")
		accept = self.request.headers.get("Accept")
		flash_version = self.request.headers.get("x-flash-version")

		host = self.request.headers.get("Host")
		trust_host = host.startswith("localhost") or host == "tfmdisney.herokuapp.com"

		referer = self.request.headers.get("Referer")
		trust_ref = referer is None or any(referer.startswith(s) for s in ("http://localhost", "https://localhost", "http://tfmdisney.herokuapp.com", "https://tfmdisney.herokuapp.com"))

		if not agent or (agent != "Shockwave Flash" and ".NET" not in agent) \
			or not accept or (accept != "*/*" and "application/x-shockwave-flash" not in accept) \
			or not flash_version or "," not in flash_version or not trust_ref or not trust_host:
				return False
		return True

	async def get(self):
		response = { "success": False }
		status = 401

		key = None
		log = True

		addr = "127.0.0.1" if infrastructure.is_local else self.request.headers.get("X-Forwarded-For")
		agent = self.request.headers.get("User-Agent")
		access_token = self.request.query.get("access_token")
		flash_token = self.request.query.get("flash_token")
		access_token = server.check_conn(access_token, addr)

		if self.check_req():
			if access_token is None:
				status = 400

				response["error"] = "bad request"
			elif access_token:
				info = infrastructure.tokens[access_token]
				level = info["level"]
				user = info["user"]

				passed = True
				if user.flash_token is None:
					if flash_token:
						user.flash_token = flash_token
						client.commit()
					else:
						passed = False
						status = 400

						response["error"] = "bad request"
				else:
					passed = user.flash_token == flash_token
					if not passed:
						print(f"User stored token: {user.flash_token}; Request token: {flash_token}")

						status = 200

						response["error"] = "your key was used by another device"

				if passed:
					key = info["key"]
					log = not user.key_hidden

					if addr not in info["ips"]:
						if len(info["ips"]) < info["conn_limit"]:
							info["ips"].append(addr)
						else:
							passed = False
							status = 200

							response["error"] = "connection limit exceeded"

					if passed:
						response["success"] = True
						response["keys"] = {
							"maps_allowed": bool(client.find_map_by_key(key, True)) if infrastructure.config["map_storage_fetch"] else False,
							"client_version": infrastructure.config["client_version"],
							"discord": infrastructure.discord.discord_names,
							"premium_level": level
						}

						async with infrastructure.session.get(
							f"{infrastructure.parser_url}/api/tfm_keys?token={infrastructure.tfm_parser_token}&level={level}"
						) as _response:
							if _response.ok:
								response["keys"].update(await _response.json())

						status = 200
			else:
				status = 200

				response["error"] = "expired/invalid token"
		else:
			status = 400

			response["error"] = "bad request"

		if log:
			infrastructure.loop.create_task(infrastructure.discord.log(
				"TFM", response, status, addr, key, access_token, agent))

		return web.json_response(response, status=status)