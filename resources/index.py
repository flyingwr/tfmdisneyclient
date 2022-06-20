from aiohttp import web
from utils.gentoken import gen_browser_token

async def index(request: web.Request):
    response = web.FileResponse("./public/index/index.html")

    cookies = request.cookies
    if not (browser_access_token := cookies.get("browser_access_token")) or browser_access_token == "None":
        response.set_cookie("browser_access_token", gen_browser_token(), max_age=365 * 24 * 60 * 60)

    return response