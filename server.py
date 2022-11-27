import infrastructure

from aiohttp import web
from data.user import User
from typing import Dict
from utils import cryptjson, gentoken, records

import aiofiles
import api
import asyncio
import datetime
import discordbot
import os
import resources
import ujson

loop = infrastructure.loop

async def swf_downloader():
	while True:
		try:
			async with infrastructure.session.get(
				f"{infrastructure.parser_url}/transformice?swf&d={datetime.datetime.now().timestamp()}"
			) as response:
				if response.ok:
					infrastructure.tfm_swf_expected_len = response.content_length
					
					async with aiofiles.open("./tfm.swf", "wb") as f:
						await f.write(await response.read())
		except Exception as e:
			print(f"Failed to download Transformice SWF: {e}")
		await asyncio.sleep(8.0)

def check_conn(access_token: str, addr: str, **kwargs):
	if access_token is not None:
		if addr in infrastructure.ips:
			access_token = infrastructure.ips[addr][1]
	else:
		return None

	if access_token in infrastructure.tokens:
		if (flash_token := kwargs.get("flash_token")) is not None:
			if infrastructure.tokens[access_token]["user"].flash_token != flash_token:
				return False
		if (session_token := kwargs.get("session_token")) is not None:
			if infrastructure.sessions.get(session_token) is None:
				return False
		return access_token
	return False

def store_access(key: str, addr: str, user: User, session_token: str) -> Dict:
	result = {}

	if addr:
		now = datetime.datetime.now().timestamp()

		if addr not in infrastructure.ips:
			access_token = gentoken.gen_token()
			infrastructure.ips[addr] = (now, access_token)			
			infrastructure.tokens[access_token] = temp = { "key": key, "user": user, "level": user.level, "ips": [addr], "conn_limit": user.connection_limit }
			infrastructure.sessions[session_token] = (key, user, access_token)
			loop.create_task(del_token(addr, access_token))
		else:
			access_token = infrastructure.ips[addr][1]
			result["contains"] = True

		result.update(dict(
			access_token=access_token, level=user.level,
			sleep=datetime.datetime.fromtimestamp(now - infrastructure.ips[addr][0]).timetuple().tm_min))

	return result

async def del_token(ip: str, token: str):
	await asyncio.sleep(10800.0)

	if ip in infrastructure.ips:
		del infrastructure.ips[ip]

	if token in infrastructure.tokens:
		del infrastructure.tokens[token]

async def unblock_addr(addr: str):
	await asyncio.sleep(240.0)

	if addr in infrastructure.auth_attempts:
		del infrastructure.auth_attempts[addr]

async def main():
	async with aiofiles.open("./config.json") as f:
		infrastructure.config = ujson.loads(await f.read())

	# if not infrastructure.is_local:
	# 	infrastructure.records_data = cryptjson.json_zip({
	# 		"new": records.read_spreadsheet("1xoPZXT5apgKm1Z5J-YEv-sXTQ6BjB0vnPgrWLxhRpaU"),
	# 		"old": records.read_spreadsheet("1l3D-tmUAgwqNPjR3qa1rKqNkNYImPLC3dhgHUD3gLjo")
	# 	})

	app = web.Application()
	app.router.add_get("/", resources.index)
	# app.router.add_get("/auth", api.Auth)
	# app.router.add_get("/dashboard", resources.dashboard)
	# app.router.add_get("/get_keys", api.GetKeys)
	# app.router.add_get("/tfmlogin", api.TfmLogin)
	# app.router.add_get("/transformice", api.Transformice)

	# app.router.add_routes([web.get("/data", api.Data),
	# 						web.get("/data/soft", api.Soft),
	# 						web.get("/mapstorage", api.MapStorage),
	# 						web.post("/data", api.Data),
	# 						web.post("/mapstorage", api.MapStorage)])

	app.router.add_get("/api/discord", api.discord_handler)
	# app.router.add_get("/api/auth", api.Auth)
	# app.router.add_get("/api/fetch", api.Fetch)
	app.router.add_get("/api/update", api.Update)
	
	app.router.add_static("/images", "./images")
	app.router.add_static("/public", "./public")

	runner = web.AppRunner(app)
	await runner.setup()

	site = web.TCPSite(runner, "0.0.0.0", os.getenv("PORT"))
	await site.start()

	infrastructure.discord = discordbot.Bot("old!")
	
	# loop.create_task(swf_downloader())
	loop.create_task(infrastructure.discord.start(os.getenv("DISCORD_API_TOKEN")))

if __name__ ==  "__main__":
	loop.create_task(main())
	loop.run_forever()