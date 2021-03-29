from aiohttp import ClientSession, web
from gentoken import generate_token
from tfmparser import Parser

from typing import Dict, Optional

import aiofiles
import aiomysql
import asyncio
import cryptjson
import datetime
import loadfiles
import os
import re
import ujson

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

class Api:
	def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.ips: Dict = {}
		self.tokens: Dict = {}

		self.is_local: bool = "Windows 7" in os.getcwd()

		self.pool: aiomysql.Pool = None

		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
		self.parser: Parser = Parser(is_local=self.is_local)

	async def del_token(self, ip: str, token: str):
		await asyncio.sleep(3600)

		if ip in self.ips.keys():
			del self.ips[ip]
		if token in self.tokens.keys():
			del self.tokens[token]

	async def fetch(self):
		while True:
			await self.parser.start()
			await asyncio.sleep(180)
		
	async def update(self):
		self.pool = await aiomysql.create_pool(host="remotemysql.com",
			user="iig9ez4StJ", password="v0TNEk0vsI",
			db="iig9ez4StJ", loop=self.loop,
			autocommit=True
		)

		async with aiofiles.open("config.json") as f, \
		aiofiles.open("./public/mapstorage/index.html") as _f, \
		aiofiles.open("protectedmaps.json") as __f:
			config = ujson.loads(await f.read())
			self.vip_list = config["vip_list"]
			self.update_url = config["update_url"]
			self.version = config["version"]

			self.mapstorage_index = await _f.read()
			self.protectedmaps_data = await __f.read()

		async with aiofiles.open("./data/ChargeurTransformice.swf", "rb") as f, \
		aiofiles.open("./data/invalid.swf", "rb") as _f:
			self.chargeur_swf = await f.read()
			self.invalid_swf = await _f.read()

		print("Endpoint data has been updated.")

		self.loop.create_task(self.fetch())
		
	async def auth(self, request):
		response = {}
		response['success'] = False
		status = 401

		key = request.query.get("key")
		client_version = request.query.get("version")
		addrr = request.headers.get("X-Forwarded-For")
		if self.is_local:
			addrr = "127.0.0.1"

		if key is not None:
			if key in self.vip_list.keys():
				if client_version == self.version:
					response['success'] = True

					access_token = ""

					if addrr is not None:
						if addrr not in self.ips.keys():
							access_token = generate_token()
							self.ips[addrr] = (datetime.datetime.now().timestamp(), access_token)
							self.loop.create_task(self.del_token(addrr, access_token))
							self.tokens[access_token] = {"key": key, "level": self.vip_list[key], "ips": []}
						else:
							access_token = self.ips[addrr][1]
							response['contains'] = True
						response['sleep'] = datetime.datetime.fromtimestamp(
							datetime.datetime.now().timestamp() - self.ips[addrr][0]).timetuple().tm_min

					response['access_token'] = access_token
					status = 200
				else:
					response['error'] = 'outdated version'
					response['update_url'] = self.update_url
					status = 406
			else:
				response['error'] = 'invalid key'
		else:
			response['error'] = 'invalid query'

		return web.json_response(response, status=status)

	async def data(self, request):
		text = ""
		status = 401

		access_token = request.query.get("access_token")
		if access_token is not None:
			addrr = request.headers.get("X-Forwarded-For")
			if addrr in self.ips.keys():
				access_token = self.ips[addrr][1]
			if access_token in self.tokens.keys():
				status = 200

		if request.method == "GET":
			if status == 200:
				if request.query.get("soft") is not None:
					text = self.tokens[access_token].get("soft") or ""
				elif request.query.get("protected") is not None:
					text = self.protectedmaps_data
				elif request.query.get("config") is not None:
					async with self.pool.acquire() as conn:
						async with conn.cursor() as cur:
							await cur.execute(
								"SELECT `text` FROM `config` WHERE `id`={}"
								.format(self.tokens[access_token]["key"])
							)
							selected = await cur.fetchone()
							if selected:
								text = selected[0]

		elif request.method == "POST":
			if status == 200:
				post = await request.post()
				soft = post.get("soft")
				if soft is not None:
					level = self.tokens[access_token]["level"]
					if level in ("SILVER", "GOLD", "PLATINUM"):
						self.tokens[access_token]["soft"] = soft

				config = post.get("config")
				if config is not None:
					async with self.pool.acquire() as conn:
						async with conn.cursor() as cur:
							await cur.execute(
								"SELECT `text` FROM `config` WHERE `id`='{}'"
								.format(self.tokens[access_token]["key"])
							)
							selected = await cur.fetchone()
							if selected:
								await cur.execute(
									"UPDATE `config` SET `text`='{}' WHERE `id`='{}'"
									.format(config, self.tokens[access_token]["key"])
								)
							else:
								await cur.execute(
									"INSERT INTO `config` (`id`, `text`) VALUES ('{}', '{}'')"
									.format(self.tokens[access_token]["key"], config)
								)

		return web.Response(text=text, status=status)

	async def get_keys(self, request):
		response = {}
		response['success'] = False
		status = 401

		access_token = request.query.get("access_token")
		addrr = request.headers.get("X-Forwarded-For")
		if access_token is not None:
			if addrr in self.ips.keys():
				access_token = self.ips[addrr][1]
			if access_token in self.tokens.keys():
				level = self.tokens[access_token]["level"]
				limit = 10 if level == "PLATINUM" else 3
				if len(self.tokens[access_token]["ips"]) < limit:
					if addrr not in self.tokens[access_token]["ips"]:
						self.tokens[access_token]["ips"].append(addrr)

					response['success'] = True

					keys = self.parser.keys()
					
					if level == "FREE":
						del keys["SILVER"]
						del keys["GOLD"]
						del keys["PLATINUM"]
					elif level == "SILVER":
						del keys["GOLD"]
						del keys["PLATINUM"]
					elif level == "GOLD":
						del keys["PLATINUM"]

					response["keys"] = {"premium_level": level}
					for v in keys.values():
						response["keys"].update(v)
					
					status = 200
				else:
					response['error'] = 'max connection limit exceeded'
					del self.tokens[access_token]
			else:
				response['error'] = 'expired/invalid access_token'
		else:
			response['error'] = 'invalid query'

		return web.json_response(response, status=status)

	async def mapstorage(self, request):
		data = await request.post()
		key = data.get("key")

		access_token = request.query.get("access_token")
		if access_token is not None:
			addrr = request.headers.get("X-Forwarded-For")
			if addrr in self.ips.keys():
				access_token = self.ips[addrr][1]
			if access_token in self.tokens.keys():
				key = self.tokens[access_token].get("key")
			else:
				return web.HTTPUnauthorized()
		method = request.query.get("method")

		map_data = data.get("map_data")

		body = b""
		if key is not None:
			level = self.vip_list.get(key)
			if level in ("SILVER", "GOLD", "PLATINUM"):
				async with self.pool.acquire() as conn:
					async with conn.cursor() as cur:
						await cur.execute(
							"SELECT `json` FROM `maps` WHERE `id`='{}'"
							.format(key)
						)
						selected = await cur.fetchone()
						if selected:
							body = selected[0].encode()
						else:
							if not map_data:
								await cur.execute(
									"SELECT `json` FROM `maps` WHERE `id`='{}'"
									.format("rsuon55s")
								)
								selected = await cur.fetchone()
								if selected:
									body = selected[0].encode()

						if map_data:
							if selected:
								try:
									sel_decoded = cryptjson.text_decode(selected).decode()
									data_decoded = cryptjson.text_decode(map_data).split(":")
									if data_decoded[0] in sel_decoded:
										if method == "save":
											sel_decoded = re.sub(
												r"{0}:.*(#?)".format(data_decoded[0]),
												r"{0}:{1}\1".format(data_decoded[0], data_decoded[1]),
												sel_decoded
											)
										elif method == "delete":
											sel_decoded = re.sub(r"{0}:.*(#?)".format(data_decoded[0]), r"\1", sel_decoded)
									else:
										if method == "save":
											sel_decoded += f"#{':'.join(data_decoded)}"
									await cur.execute(
										"UPDATE `maps` SET `json`='{}' WHERE `id`='{}'"
										.format(cryptjson.text_encode(sel_decoded), key)
									)
								except Exception:
									map_data = {}

		if request.method == "GET":
			if access_token is not None:
				return web.Response(body=body)
		elif request.method == "POST":
			if method in ("delete", "save"):
				if map_data:
					return web.HTTPOk()
				else:
					return web.HTTPBadRequest()
			else:
				if body:
					return web.Response(
						headers={"Content-Disposition": 'attachment;filename="maps.json"'},
						body=body
					)

		return web.Response(text=self.mapstorage_index, content_type="text/html")

	async def transformice(self, request):
		body = self.invalid_swf
		content_type = "application/x-shockwave-flash"

		access_token = request.query.get("access_token")
		if access_token is not None:
			if request.query.get("access_token") in self.tokens.keys():
				body = self.chargeur_swf
			return web.Response(body=body, content_type=content_type)
		if request.query.get("swf") is not None:
			return web.FileResponse("./tfm.swf")
		return web.Response(body=body, content_type=content_type)

async def main():
	app = web.Application()
	endpoint = Api(loop)
	await endpoint.update()

	app.router.add_get('/auth', endpoint.auth)
	app.router.add_get('/get_keys', endpoint.get_keys)
	app.router.add_get('/data', endpoint.data)
	app.router.add_post('/data', endpoint.data)
	app.router.add_get('/mapstorage', endpoint.mapstorage)
	app.router.add_post('/mapstorage', endpoint.mapstorage)
	app.router.add_get('/transformice', endpoint.transformice)

	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, "0.0.0.0", os.getenv("PORT"))
	await site.start()

if __name__ ==  '__main__':
	loop.create_task(main())
	loop.run_forever()