from aiohttp import web


async def index(_):
    return web.FileResponse("./public/index/index.html")
