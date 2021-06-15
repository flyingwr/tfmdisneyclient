from typing import List, Optional

import aiomysql, asyncio

pool = None

class Pool:
	def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.pool: aiomysql.Pool = None
		self.cursor: aiomysql.Cursor = None

		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

	async def acquire(self) -> aiomysql.Connection:
		try:
			conn = await self.pool.acquire()
		except Exception:
			conn = None
		return conn

	async def exec(self, query: str, many: Optional[bool] = False, data: Optional[List] = None) -> aiomysql.Cursor:
		conn = await self.pool.acquire()
		cur = await conn.cursor()
		if many:
			if data:
				await cur.executemany(query, data)
		else:
			await cur.execute(query)
		return conn, cur

	async def release(self, conn: aiomysql.Connection, cursor: Optional[aiomysql.Cursor] = None):
		if cursor is not None:
			await cursor.close()
		await self.pool.release(conn)

	async def add_key_maps(self, *args):
		conn, cur = await self.exec("SELECT `json` FROM `maps` WHERE `id`='rsuon55s'")
		selected = await cur.fetchone()
		await cur.executemany(
			"INSERT INTO `maps` (`id`, `json`) VALUES (%s, %s)", [(key, selected[0]) for key in args])
		await self.release(conn, cur)

	async def browser_auth_perm(self, key: str, perm: bool):
		conn, cur = await self.exec(
			"UPDATE `users` SET `browser_access`=%s WHERE `id`=%s",
			(int(perm), key))
		await self.release(conn, cur)

	async def change_key_level(self, key: str, level: str = "SILVER"):
		conn, cur = await self.exec(
			"UPDATE `users` SET `level`=%s WHERE `id`=%s",
			(level.upper(), key))
		await self.release(conn, cur)

	async def del_key(self, *args):
		conn, cur = await self.exec("DELETE FROM `users` WHERE `id`=%s", many=True, data=[(key, ) for key in args])
		await self.release(conn, cur)

	async def del_key_maps(self, *args):
		conn, cur = await self.exec("DELETE FROM `maps` WHERE `id`=%s", True, [(key, ) for key in args])
		await self.release(conn, cur)

	async def transfer_key_maps(self, _from: str, to: str):
		conn, cur = await self.exec(
			"SELECT `json` FROM `maps` WHERE `id`=%s",
			(_from, ))
		selected = await cur.fetchone()
		if selected:
			await cur.execute(
				"SELECT `id` FROM `maps` WHERE `id`=%s",
				(to, ))
			_selected = await cur.fetchone()
			if _selected:
				await cur.execute(
					"UPDATE `maps` SET `json`=%s WHERE `id`=%s",
					(selected[0], to))
			else:
				await cur.execute(
					"INSERT INTO `maps` (`id`, `json`) VALUES (%s, %s)",
					(to, selected[0]))
		await self.release(conn, cur)

		if not selected:
			raise Exception(f"Key `{_from}` not found")

	async def start(self):
		try:
			self.pool = await aiomysql.create_pool(host="remotemysql.com",
				user="iig9ez4StJ", password="M93f3gN3ZP",
				db="iig9ez4StJ", loop=self.loop,
				autocommit=True)
			print("[Pool] Connected to remotemysql")
		except aiomysql.OperationalError:
			print("[Pool] Error: can't connect to remotemysql")