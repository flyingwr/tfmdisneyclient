from aiohttp import web
from endpoint import Api

import api, asyncio, os
loop = asyncio.get_event_loop()

async def main():
	app = web.Application()
	endpoint = Api(loop)
	await endpoint.update()

	app.router.add_get('/', endpoint.index)
	app.router.add_get('/get_keys', endpoint.get_keys)
	app.router.add_get('/tfmlogin', endpoint.tfmlogin)
	app.router.add_get('/transformice', endpoint.transformice)

	app.router.add_routes([web.get("/auth", endpoint.auth, name="auth"),
							web.post("/auth", endpoint.auth, name="auth")])
	app.router.add_routes([web.get("/data", endpoint.data),
							web.post("/data", endpoint.data),
							web.put("/data", endpoint.data)])
	app.router.add_routes([web.get("/mapstorage", endpoint.mapstorage),
							web.post("/mapstorage", endpoint.mapstorage)])

	app.router.add_get("/api/discord", api.discord_handler)
	app.router.add_get("/api/auth", api.Auth)
	
	app.router.add_static('/images', './images')
	app.router.add_static('/public', './public')

	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, "0.0.0.0", os.getenv("PORT"))
	await site.start()

if __name__ ==  '__main__':
	loop.create_task(main())
	loop.run_forever()