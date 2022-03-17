from aiohttp import web
from utils.gentoken import gen_token


async def index(request: web.Request):
    response = web.FileResponse("./public/index/index.html")

    agent = request.headers.get("User-Agent")
    cookies = request.cookies

    if "disneyclient/" in agent:
        if not cookies.get("uuid2"):
            response.set_cookie("uuid2", gen_token(True), max_age=365 * 24 * 60 * 60)
    else:
        if not cookies.get("browser_access_token"):
            response.set_cookie("browser_access_token", gen_token(True), max_age=365 * 24 * 60 * 60)

    return response
