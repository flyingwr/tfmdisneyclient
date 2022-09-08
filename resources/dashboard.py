from aiohttp import web

import infrastructure

async def dashboard(request: web.Request):
    if (session_token := request.cookies.get("session")) is None or infrastructure.sessions.get(session_token) is None:
        raise web.HTTPUnauthorized()
    return web.FileResponse("./public/dashboard/index.html")