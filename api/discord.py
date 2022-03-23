from aiohttp import web


import infrastructure


async def discord_handler(request):
	return web.json_response({"names": infrastructure.discord.discord_names or infrastructure.config["discord_names"]})
