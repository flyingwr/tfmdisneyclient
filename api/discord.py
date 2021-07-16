from aiohttp import web


import infrastructure


async def discord_handler(request):
	return web.Response(text=infrastructure.discord.discord_name or "patati#9627")
