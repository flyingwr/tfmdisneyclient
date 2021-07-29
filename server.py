from dotenv import load_dotenv
load_dotenv()


from aiohttp import web
from typing import Dict, Optional
from utils import cryptjson, gentoken, records


import aiofiles
import api
import asyncio
import datetime
import discordbot
import infrastructure
import os
import resources
import ujson


loop = infrastructure.loop


async def swf_downloader():
	while True:
		async with infrastructure.session.get("https://tfmdisneyparser.herokuapp.com/transformice?swf") as response:
			async with aiofiles.open("./tfm.swf", "wb") as f:
				await f.write(await response.read())

		await asyncio.sleep(8.0)


def check_conn(access_token: str, addr: str):
	if access_token is not None:
		if addr in infrastructure.ips:
			access_token = infrastructure.ips[addr][1]
	else:
		return None

	return access_token if (
		access_token is not None and access_token in infrastructure.tokens
	) else False

def store_access(key: str, level: str, addr: Optional[str] = None) -> Dict:
	result = {}

	if addr:
		if addr not in infrastructure.ips:
			access_token = gentoken.generate_token()
			infrastructure.ips[addr] = (datetime.datetime.now().timestamp(), access_token)			
			infrastructure.tokens[access_token] = {"key": key, "level": level, "ips": [addr]}
			loop.create_task(del_token(addr, access_token))
		else:
			access_token = infrastructure.ips[addr][1]
			result["contains"] = True

		result.update(dict(
			access_token=access_token, level=level,
			sleep=datetime.datetime.fromtimestamp(
				datetime.datetime.now().timestamp() - infrastructure.ips[addr][0]).timetuple().tm_min))

	return result

async def del_token(ip: str, token: str):
	await asyncio.sleep(3600)

	if ip in infrastructure.ips:
		del infrastructure.ips[ip]

	if token in infrastructure.tokens:
		del infrastructure.tokens[token]

async def del_lsmap(token: str):
	await asyncio.sleep(240)

	if token in infrastructure.tokens:
		infrastructure.tokens[token]["lsmap"] = ""

async def main():
	async with aiofiles.open("./config.json") as f:
		infrastructure.config = ujson.loads(await f.read())

	if not infrastructure.is_local:
		records.update_wr_list()
		infrastructure.records_data = cryptjson.json_zip(records.wr_list)

	app = web.Application()
	app.router.add_get("/", resources.index)
	app.router.add_get("/auth", api.Auth)
	app.router.add_get("/get_keys", api.GetKeys)
	app.router.add_get("/tfmlogin", api.TfmLogin)
	app.router.add_get("/transformice", api.Transformice)

	app.router.add_routes([web.get("/data", api.Data),
							web.get("/data/soft", api.Soft),
							web.get("/mapstorage", api.MapStorage),
							web.post("/data", api.Data),
							web.post("/mapstorage", api.MapStorage)])
							
	app.router.add_get("/api/discord", api.discord_handler)
	app.router.add_get("/api/auth", api.Auth)
	app.router.add_get("/api/update", api.Update)
	
	app.router.add_static("/images", "./images")
	app.router.add_static("/public", "./public")

	runner = web.AppRunner(app)
	await runner.setup()

	site = web.TCPSite(runner, "0.0.0.0", os.getenv("PORT"))
	await site.start()

	infrastructure.discord = discordbot.Bot()
	
	loop.create_task(swf_downloader())
	loop.create_task(infrastructure.discord.start(os.getenv("DISCORD_API_TOKEN")))

if __name__ ==  "__main__":
	loop.create_task(main())
	loop.run_forever()