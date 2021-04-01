from typing import Optional, Tuple

import aiomysql
import asyncio

class Pool:
	def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.pool: aiomysql.Pool = None
		self.cursor: aiomysql.Cursor = None

		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

		loop.create_task(self.start())

	async def acquire(self) -> Tuple[aiomysql.Connection, aiomysql.Cursor]:
		conn = await self.pool.acquire()
		return (conn, await conn.cursor())

	async def start(self):
		self.pool = await aiomysql.create_pool(host="remotemysql.com",
			user="iig9ez4StJ", password="v0TNEk0vsI",
			db="iig9ez4StJ", loop=self.loop,
			autocommit=True
		)

		print("[Pool] Connected to remotemysql")