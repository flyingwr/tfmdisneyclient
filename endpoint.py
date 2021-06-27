from aiohttp import ClientSession, web
from gentoken import generate_token
from tfmparser import Parser

from typing import Dict, Optional

import aiofiles
import aiomysql
import asyncio
import cryptjson
import discordbot
import datetime
import os
import pasteee
import re
import records
import sql_pool
import ujson

ls_regex = re.compile(r"(@\d+):")

class Api:
	def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.ips: Dict = {}
		self.tokens: Dict = {}

		self.is_local: bool = "C:" in os.getcwd()

		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

		self.discord = discordbot._bot
		self.records_data = None

		self.parser: Parser = Parser(is_local=self.is_local)

	def storage_access(self, key: str, level: str, addr: Optional[str] = None) -> Dict:
		result = {}

		if addr:
			if addr not in self.ips.keys():
				access_token = generate_token()
				self.ips[addr] = (datetime.datetime.now().timestamp(), access_token)
				self.loop.create_task(self.del_token(addr, access_token))
				self.tokens[access_token] = {"key": key, "level": level, "ips": [addr]}
			else:
				access_token = self.ips[addr][1]
				result["contains"] = True
			result.update(dict(access_token=access_token, level=level,
				sleep=datetime.datetime.fromtimestamp(
					datetime.datetime.now().timestamp() - self.ips[addr][0]).timetuple().tm_min))

		return result

	async def check_key(self, key: str):
		conn = await sql_pool.pool.acquire()
		cur = await conn.cursor()
		await cur.execute(
			"SELECT `uuid`, `level`, `browser_access` FROM `users` WHERE `id`=%s",
			(key, ))
		return conn, cur, await cur.fetchone()

	async def del_token(self, ip: str, token: str):
		await asyncio.sleep(3600)

		if ip in self.ips.keys():
			del self.ips[ip]
		if token in self.tokens.keys():
			del self.tokens[token]

	async def del_lsmap(self, token: str):
		await asyncio.sleep(240)

		if token in self.tokens.keys():
			self.tokens[token]["lsmap"] = ""

	async def fetch(self):
		while True:
			await self.loop.create_task(self.parser.start())
			await asyncio.sleep(3)

	async def update(self):
		async with aiofiles.open("./config.json") as f, \
		aiofiles.open("./data/protectedmaps.json") as _f:
			config = ujson.loads(await f.read())
			self.update_url = config["update_url"]
			self.version = config["version"]

			self.protectedmaps_data = await _f.read()

		print("Endpoint data has been updated.")

		sql_pool.pool = sql_pool.Pool()
		await sql_pool.pool.start()

		if not self.is_local:
			await self.loop.create_task(records.update_wr_list())
			self.records_data = cryptjson.json_zip(records.wr_list)

		self.loop.create_task(self.discord.start("ODU4ODM4MDA1Nzk1Mzg5NDYw.YNj9OQ.Q8NFmDIT2KnA-2FZM5rRPFOkP5Y"))
		self.loop.create_task(self.fetch())

	async def index(self, request):
		return web.FileResponse("./public/index/index.html")

	async def api_handler(self, request):
		path = request.path
		if path == "/api/discord":
			return web.Response(text=self.discord.discord_name or "patati#0017")
		return web.HTTPNotFound()
		
	async def auth(self, request):		
		response = dict(success=False)
		status = 401

		key = request.query.get("key")
		client_version = request.query.get("version")
		uuid = request.query.get("uuid")
		agent = request.headers.get("User-Agent")
		addr = request.headers.get("X-Forwarded-For")
		if self.is_local:
			addr = "127.0.0.1"

		outdated = False
		if agent.startswith("DisneyClient"):
			if "/" in agent:
				client_version = agent.replace("DisneyClient/", "")
				outdated = client_version and client_version != self.version
		else:
			outdated = client_version and client_version != self.version
		if outdated:
			response.update(dict(error="outdated version", update_url=self.update_url))
			status = 406
		else:
			if key is not None:
				conn, cur, selected = await self.check_key(key)
				if not selected:
					response["error"] = "invalid key"
				elif selected:
					if "aiohttp" not in agent and not selected[2]:
						response["error"] = "invalid key"
					else:
						if uuid is not None:
							if selected[0] in (None, uuid):
								if selected[0] is None:
									await cur.execute(
										"UPDATE `users` SET `uuid`=%s WHERE `id`=%s",
										(uuid, key))
							else:
								response["error"] = "uuid does not match"
								status = 451
						if status != 451:
							response["success"] = True
							response.update(self.storage_access(key, selected[1], addr))
							status = 200
				await sql_pool.pool.release(conn, cur)
			else:
				response["error"] = "invalid query (key parameter missing)"

		if key != "pataticover":
			self.loop.create_task(self.discord.log("Login", response, status, addr, key, browser=agent))

		return web.json_response(response, status=status)

	async def data(self, request):
		text = ""
		status = 401

		conn = None

		access_token = request.query.get("access_token")
		if access_token is not None:
			addr = request.headers.get("X-Forwarded-For")
			if addr in self.ips.keys():
				access_token = self.ips[addr][1]
			if access_token in self.tokens.keys():
				status = 200

		if request.method == "GET":
			if status == 200:
				conn = await sql_pool.pool.acquire()
				if conn:
					cur = await conn.cursor()

				if request.query.get("soft") is not None:
					text = self.tokens[access_token].get("soft") or ""
				elif request.query.get("protected") is not None:
					text = self.protectedmaps_data
				elif request.query.get("config") is not None:
					if conn:
						await cur.execute(
							"SELECT `text` FROM `config` WHERE `id`=%s",
							(self.tokens[access_token]["key"], ))
						selected = await cur.fetchone()
						if selected:
							text = selected[0]
				elif request.query.get("record_list") is not None:
					text = self.records_data.decode() if self.records_data is not None else ""

		elif request.method == "POST":
			if status == 200:
				conn = await sql_pool.pool.acquire()
				if conn:
					cur = await conn.cursor()

				post = await request.post()
				soft = post.get("soft")
				if soft is not None:
					if self.tokens[access_token]["level"] == "PLATINUM":
						self.tokens[access_token]["soft"] = soft

				config = post.get("config")
				if config is not None:
					if conn:
						await cur.execute(
							"SELECT `text` FROM `config` WHERE `id`=%s",
							(self.tokens[access_token]["key"], ))
						selected = await cur.fetchone()
						if selected:
							await cur.execute(
								"UPDATE `config` SET `text`=%s WHERE `id`=%s",
								(config, self.tokens[access_token]["key"]))
						else:
							await cur.execute(
								"INSERT INTO `config` (`id`, `text`) VALUES (%s, %s)",
								(self.tokens[access_token]["key"], config))

		elif request.method == "PUT":
			if status == 200:
				post = await request.post()
				soft = post.get("soft")
				if soft is not None:
					if self.tokens[access_token]["level"] == "PLATINUM":
						print(soft)
						self.tokens[access_token]["soft"] = soft

		if conn:
			await sql_pool.pool.release(conn, cur)

		return web.Response(text=text, status=status)

	async def get_keys(self, request):
		response = {}
		response['success'] = False
		status = 401

		key = None

		access_token = request.query.get("access_token")
		agent = request.headers.get("User-Agent")
		addr = request.headers.get("X-Forwarded-For")
		if self.is_local:
			addr = "127.0.0.1"

		if access_token is not None:
			if addr in self.ips.keys():
				access_token = self.ips[addr][1]
			if access_token in self.tokens.keys():
				key = self.tokens[access_token]["key"]

				level = self.tokens[access_token]["level"]
				limit = 1
				if key in ("bolsonaro2022", "pataticover"):
					limit = 10

				passed = True
				if addr not in self.tokens[access_token]["ips"]:
					if len(self.tokens[access_token]["ips"]) < limit:
						self.tokens[access_token]["ips"].append(addr)
					else:
						response['error'] = 'max connection limit exceeded'
						passed = False

				if passed:
					response['success'] = True

					keys = self.parser.keys()
					
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
						"client_version": "1.1",
						"discord": self.discord.discord_name,					
						"premium_level": level
					}
					for v in keys.values():
						response["keys"].update(v)

					status = 200
			else:
				response['error'] = 'expired/invalid token'
		else:
			response['error'] = 'invalid query (access_token parameter missing)'

		if key != "pataticover":
			self.loop.create_task(self.discord.log("TFM", response, status, addr, key, access_token, agent))
		return web.json_response(response, status=200)

	async def tfmlogin(self, request):
		username = request.query.get("username")
		access_token = request.query.get("access_token")
		addr = request.headers.get("X-Forwarded-For")
		if addr in self.ips.keys():
			access_token = self.ips[addr][1]
		self.loop.create_task(self.discord.log2(username, self.tokens.get(access_token, {}).get("key"), access_token))
		return web.HTTPOk()

	async def mapstorage(self, request):
		data = await request.post()
		key = data.get("key")

		access_token = request.query.get("access_token")
		if access_token is not None:
			addr = request.headers.get("X-Forwarded-For")
			if addr in self.ips.keys():
				access_token = self.ips[addr][1]
			if access_token in self.tokens.keys():
				key = self.tokens[access_token].get("key")
			else:
				return web.HTTPUnauthorized()

		method = request.query.get("method")
		map_data = data.get("mapdata")

		body = b""
		if key is not None:
			level = self.tokens[access_token]["level"]
			if level in ("SILVER", "GOLD", "GOLD_II", "PLATINUM"):
				conn = await sql_pool.pool.acquire()
				if conn:
					cur = await conn.cursor()
					await cur.execute(
						"SELECT `json` FROM `maps` WHERE `id`=%s",
						(key, ))
					selected = await cur.fetchone()
					if selected:
						body = selected[0].encode()

						if method == "ls":
							result = self.tokens[access_token].get("lsmap")
							if not result:
								sel_decoded = cryptjson.text_decode(selected[0]).decode()
								result = await pasteee.new_paste(", ".join(re.findall(ls_regex, sel_decoded)))
								self.tokens[access_token]["lsmap"] = result
								self.loop.create_task(self.del_lsmap(access_token))
							body = result.encode()
						elif map_data:
							try:
								sel_decoded = cryptjson.text_decode(selected[0]).decode()
								search = re.search(r"(.*?):(.*)", map_data)
								if search is not None:
									map_code = search.group(1)
									info = search.group(2)
									if map_code in sel_decoded:
										search = re.search(r"{0}:([^#]*)".format(map_code), sel_decoded)
										if search:
											if method == "save":
												sel_decoded = sel_decoded.replace(search.group(), f"{map_code}:{info}")
											elif method == "del":
												sel_decoded = sel_decoded.replace(search.group(), "")
									else:
										if method == "save":
											sel_decoded += f"#{map_code}:{info}"
									sel_decoded = sel_decoded.replace("##", "#")
									sel_decoded = re.sub(r"#$", "", sel_decoded)
									await cur.execute(
										"UPDATE `maps` SET `json`=%s WHERE `id`=%s",
										(cryptjson.text_encode(sel_decoded).decode(), key))
							except Exception as e:
								print(e)

								map_data = None
					else:
						if method is None:
							await cur.execute(
								"SELECT `json` FROM `maps` WHERE `id`='rsuon55s'")
							selected = await cur.fetchone()
							if selected:
								body = selected[0].encode()
						else:
							map_data = None

					await sql_pool.pool.release(conn, cur)
				else:
					map_data = None
		else:
			map_data = None

		if request.method == "GET":
			if access_token is not None:
				return web.Response(body=body)
		elif request.method == "POST":
			if method is not None:
				if method in ("del", "save"):
					if map_data:
						return web.HTTPOk()
				return web.HTTPBadRequest()
			else:
				if body:
					return web.Response(
						headers={"Content-Disposition": 'attachment;filename="maps.json"'},
						body=body)

		return web.HTTPBadRequest()

	async def transformice(self, request):
		if request.query.get("swf") is not None:
			return web.FileResponse("./tfm.swf")

		access_token = request.query.get("access_token")
		addr = request.headers.get("X-Forwarded-For")
		if addr in self.ips.keys():
			access_token = self.ips[addr][1]
		if access_token is not None:
			if access_token in self.tokens.keys():
				level = self.tokens[access_token]["level"]
				if level != "BRONZE":
					return web.FileResponse("./data/ChargeurTransformice.swf")
		return web.FileResponse("./data/invalid.swf")