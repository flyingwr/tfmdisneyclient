from aiohttp import web


import infrastructure


async def discord_handler(request):
	return web.json_response({"names": infrastructure.discord.discord_names or ["renan#9093", "pekfto#0689", "styleking#6666"]})
