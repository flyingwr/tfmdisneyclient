from aiohttp import web
from services.mongodb import find_user_by_key


import infrastructure
import server


class Auth(web.View):
	async def get(self):
		response = dict(success=False)
		status = 401

		key = self.request.query.get("key")
		client_version = self.request.query.get("version")
		uuid = self.request.query.get("uuid")

		agent = self.request.headers.get("User-Agent")

		print(self.request.raw_headers)

		addr = "127.0.0.1" if infrastructure.is_local else self.request.headers.get("X-Forwarded-For")
		if addr not in infrastructure.blacklisted_ips:
			if client_version and client_version != infrastructure.config["version"]:
				response.update(dict(error="outdated version", update_url=infrastructure.config["update_url"]))
				status = 406
			else:
				if key is not None:
					user = find_user_by_key(key)
					if user:
						if "disneyclient" not in agent:
							if user.browser_access:
								cookies = self.request.cookies
								browser_access_token = cookies.get("browser_access_token")
								if browser_access_token:
									if user.browser_access_token is None:
										user.update(browser_access_token=browser_access_token)

										status = 200
									elif user.browser_access_token == browser_access_token:
										status = 200
									else:
										response["error"] = "this key is used by another device"
								else:
									response["error"] = "info mismatch. try refreshing the page"
							else:
								response["error"] = "your key is not allowed for browsers"
						else:
							if uuid is None:
								response["error"] = "invalid query: `uuid` parameter missing"
							else:
								if user.uuid is None:
									user.update(uuid=uuid)

									status = 200
								elif str(user.uuid).upper() == uuid:
									status = 200
								else:
									response["error"] = "uuid does not match"
									status = 451

						if status == 200:
							response["success"] = True
							response.update(server.store_access(key, user.premium_level, addr, user.connection_limit))
					else:
						response["error"] = "invalid key"

						infrastructure.auth_attempts[addr] += 1
						n = infrastructure.auth_attempts[addr]
						if n >= 8:
							if n == 8:
								infrastructure.loop.create_task(server.unblock_addr(addr))

							response["error"] = "temporarily blocked due to many login attemps"
				else:
					response["error"] = "invalid query: `key` parameter missing"
		else:
			response["error"] = "ip address blacklisted :P"

		if key != "pataticover":
			infrastructure.loop.create_task(infrastructure.discord.log(
				"Login", response, status, addr, key, browser=agent))

		return web.json_response(response, status=status)
