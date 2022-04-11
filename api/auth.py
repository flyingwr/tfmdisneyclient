from aiohttp import web
from data import client

import base64
import infrastructure
import server


class Auth(web.View):
	async def get(self):
		response = dict(success=False)
		status = 401

		agent = self.request.headers.get("User-Agent")
		client_version = self.request.query.get("version")
		cookies = self.request.cookies

		key = None
		log = True

		addr = "127.0.0.1" if infrastructure.is_local else self.request.headers.get("X-Forwarded-For")
		if addr not in infrastructure.blacklisted_ips:
			if client_version and client_version != infrastructure.config["version"]:
				response.update(dict(error="outdated version", update_url=infrastructure.config["update_url"]))
				
				status = 406
			else:
				auth = self.request.headers.get("Authorization")
				if auth:
					credentials = auth.split()
					if len(credentials) == 2:
						scheme, key = auth.split()
						if scheme == "Basic":
							key = base64.b64decode(key.encode()).decode()
							
					user = client.find_user_by_key(key)
					if user:
						log = not user.key_hidden

						if user.browser_access:
							browser_access_token = cookies.get("browser_access_token")
							if browser_access_token:
								if all(
									(self.request.headers.get(header) for header in (
										"Connection", "Accept-Language"
									))
								):
									if user.browser_access_token is None:
										user.browser_access_token = browser_access_token
										client.commit()

										status = 200
									elif user.browser_access_token == browser_access_token:
										status = 200
									else:
										response["error"] = "your key was used by another device"
								else:
									response["error"] = "info mismatch. try another browser"
							else:
								response["error"] = "info mismatch. try another browser"
						else:
							response["error"] = "your key is not allowed for browsers"

						if status == 200:
							response["success"] = True
							response.update(server.store_access(key, addr, user))
					else:
						response["error"] = "invalid key"

						infrastructure.auth_attempts[addr] += 1
						n = infrastructure.auth_attempts[addr]
						if n >= 8:
							if n == 8:
								infrastructure.loop.create_task(server.unblock_addr(addr))

							response["error"] = "temporarily blocked due to many login attemps"
				else:
					response["error"] = "bad request"

					status = 400
		else:
			response["error"] = "ip address blacklisted"

		if log:
			infrastructure.loop.create_task(infrastructure.discord.log(
				"Login", response, status, addr, key, browser=agent))

		return web.json_response(response, status=status)