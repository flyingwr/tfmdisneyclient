from datetime import datetime
from discord import Embed, NotFound
from discord.ext import commands

from typing import Any, Dict, Optional, Union

import poolhandler

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix="!")

		self.log_channel = None
		self.log_channel2 = None
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

	async def log2(self, username: str, key: str, token: str):
		if self.log_channel2 is not None:
			await self.log_channel2.send(f"Account `{username}` connected using token `{token}` from key `{key}`")
		else:
			print("[Discord] Invalid channel (2)")

bot = Bot()

@bot.event
async def on_ready():
	print("[Discord] Logged in.")

	bot.log_channel = bot.get_channel(829368194812346448)
	bot.log_channel2 = bot.get_channel(840653124561534996)
	try:
		bot.discord_name = str(await bot.fetch_user(429991854348566538))
	except NotFound:
		bot.discord_name = "patati#0017"
		
@bot.command()
async def addkey(ctx, *args):
	try:
		data = []
		for s in args:
			info = s.split(":")
			level = "SILVER"
			if len(info) > 1:
				level = info[1].upper()
			data.append((info[0], level))

		conn, cur = await poolhandler.exec("INSERT INTO `users` (`id`, `level`) VALUES (%s, %s)", True, data)
		await poolhandler.pool.release(conn, cur)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@bot.command()
async def addkeymaps(ctx, *args):
	try:
		await self.poolhandler.add_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@bot.command()
async def changekeylevel(ctx):
	try:
		await self.poolhandler.change_key_level(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@bot.command()
async def delkey(ctx, *args):
	try:
		await self.poolhandler.del_key(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@bot.command()
async def delkeymaps(ctx, *args):
	try:
		await self.poolhandler.del_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@bot.command()
async def transferkeymaps(ctx, *args):
	try:
		await self.poolhandler.transfer_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")