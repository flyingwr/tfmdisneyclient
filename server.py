from aiohttp import web
from endpoint import Api

import asyncio
import discordbot
import os

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

async def main():
	app = web.Application()
	endpoint = Api(loop)
	await endpoint.update()

	app.router.add_get('/auth', endpoint.auth)
	app.router.add_get('/get_keys', endpoint.get_keys)
	app.router.add_get('/data', endpoint.data)
	app.router.add_post('/data', endpoint.data)
	app.router.add_get('/mapstorage', endpoint.mapstorage)
	app.router.add_post('/mapstorage', endpoint.mapstorage)
	app.router.add_get('/transformice', endpoint.transformice)

	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, "0.0.0.0", os.getenv("PORT"))
	await site.start()

if __name__ ==  '__main__':
	loop.create_task(discordbot.bot.start("Nzk4MDE3OTk3ODY4MjM2ODAw.X_u6LQ.oMaIDqWJFkrzw1RTAWQZZbhvpuE"))
	loop.create_task(main())
	loop.run_forever()