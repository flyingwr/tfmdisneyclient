from datetime import datetime
from discord import Embed, NotFound
from discord.ext import commands

from typing import Any, Dict, Optional, Union

import poolhandler

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix="!")

		self.log_channel = None
		self.discord_name = None

	async def log(
		self,
		method: str,
		response: Dict,
		status: int,
		addr: Optional[str] = None,
		key: Optional[str] = None,
		token: Optional[str] = None,
		browser: Optional[str] = None
	):
		if self.log_channel is not None:
			access_token = response.get("access_token") or token
			sleep = f"(:timer: {response.get('sleep', 0)} min)"
			success = status == 200

			embed = Embed(title=f"Log - {method}",
				description=f":computer: IP address: {addr}\n"
				f":mag: Browser: {browser}\n"
				f":placard: Status: {status} {':white_check_mark:' if success else ':x:'}\n"
				f":warning: Error: {response.get('error')}\n\n"
				f":credit_card: Key: {key}\n"
				f":credit_card: Token: {access_token} {sleep if response.get('sleep') is not None else ''}",
				colour=0x00FF00 if success else 0xFF0000
			)
			await self.log_channel.send(embed=embed)
		else:
			print("[Discord] Invalid channel")

bot = Bot()

@bot.event
async def on_ready():
	print("[Discord] Logged in.")

	bot.log_channel = bot.get_channel(829368194812346448)
	try:
		bot.discord_name = str(await bot.fetch_user(429991854348566538))
	except NotFound:
		bot.discord_name = "rennan#3148"
		
@bot.command()
async def addkey(ctx, *args):
	try:
		conn = await poolhandler.pool.acquire()
		cur = await conn.cursor()

		data = []
		for s in args:
			info = s.split(":")
			level = "SILVER"
			if len(info) > 1:
				level = info[1].upper()
			data.append((info[0], level))

		await cur.executemany("INSERT INTO `users` (`id`, `level`) VALUES (%s, %s)", data)
		await cur.close()
		await poolhandler.pool.release(conn)
		await ctx.reply("Database updated")
	except Exception as e:
		print(e)
		await ctx.reply("Query failed")

@bot.command()
async def changekeylevel(ctx, key: str, level: str = "SILVER"):
	try:
		conn = await poolhandler.pool.acquire()
		cur = await conn.cursor()
		await cur.execute(
			"UPDATE `users` SET `level`='{}' WHERE `id`='{}'"
			.format(level.upper(), key))
		await cur.close()
		await poolhandler.pool.release(conn)
		await ctx.reply("Database updated")
	except Exception as e:
		print(e)
		await ctx.reply("Query failed")

@bot.command()
async def delkey(ctx, *args):
	try:
		conn = await poolhandler.pool.acquire()
		cur = await conn.cursor()
		await cur.executemany(
			"DELETE FROM `users` WHERE `id`=%s", [(key, ) for key in args])
		await cur.close()
		await poolhandler.pool.release(conn)
		await ctx.reply("Database updated")
	except Exception as e:
		print(e)
		await ctx.reply("Query failed")

@bot.command()
async def addkeymaps(ctx, *args):
	try:
		conn = await poolhandler.pool.acquire()
		cur = await conn.cursor()
		await cur.execute(
			"SELECT `json` FROM `maps` WHERE `id`='rsuon55s'")
		selected = await cur.fetchone()
		data = [(key, selected[0]) for key in args]
		await cur.executemany(
			"INSERT INTO `maps` (`id`, `json`) VALUES (%s, %s)", data)
		await cur.close()
		await poolhandler.pool.release(conn)
		await ctx.reply("Database updated")
	except Exception as e:
		print(e)
		await ctx.reply("Query failed")

@bot.command()
async def delkeymaps(ctx, *args):
	try:
		conn = await poolhandler.pool.acquire()
		cur = await conn.cursor()
		data = [(key, ) for key in args]
		await cur.executemany(
			"DELETE FROM `maps` WHERE `id`=%s", data)
		await cur.close()
		await poolhandler.pool.release(conn)
		await ctx.reply("Database updated")
	except Exception as e:
		print(e)
		await ctx.reply("Query failed")

@bot.command()
async def transferkeymaps(ctx, _from: str, to: str):
	try:
		conn = await poolhandler.pool.acquire()
		cur = await conn.cursor()
		await cur.execute(
			"SELECT `json` FROM `maps` WHERE `id`='{}'"
			.format(_from))
		selected = await cur.fetchone()
		if selected:
			await cur.execute(
				"INSERT INTO `maps` (`id`, `json`) VALUES ('{}', '{}')"
				.format(to, selected[0]))
		await cur.close()
		await poolhandler.pool.release(conn)

		if not selected:
			await ctx.reply(f"Key `{_from}` not found in database")
			raise Exception("Key not found")
	except Exception as e:
		print(e)
		await ctx.reply("Query failed")
	else:
		await ctx.reply("Database updated")