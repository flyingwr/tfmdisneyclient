from aiohttp import web
from utils.gentoken import gen_token

async def index(request: web.Request):
    response = web.FileResponse("./public/index/index.html")

    cookies = request.cookies
    if not cookies.get("browser_access_token"):
        response.set_cookie("browser_access_token", gen_token(True), max_age=365 * 24 * 60 * 60)

    return response