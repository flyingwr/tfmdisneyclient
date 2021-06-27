from aiohttp import web
from discordbot import _bot

async def discord_handler(request):
	return web.Response(text=_bot.discord_name or "patati#9627")