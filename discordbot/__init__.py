import sql_pool

from discord import NotFound
from discord.ext import commands

from .bot import Bot
_bot = Bot()

@_bot.event
async def on_ready():
	print("[Discord] Logged in.")

	_bot.log_channel = _bot.get_channel(829368194812346448)
	_bot.log_channel2 = _bot.get_channel(840653124561534996)
	try:
		_bot.discord_name = str(await _bot.fetch_user(429991854348566538))
	except NotFound:
		_bot.discord_name = "patati#0017"
		
@_bot.command()
@commands.is_owner()
async def addkey(ctx, *args):
	try:
		data = []
		for s in args:
			info = s.split(":")
			level = "SILVER"
			if len(info) > 1:
				level = info[1].upper()
			data.append((info[0], level))

		conn, cur = await sql_pool.pool.exec("INSERT INTO `users` (`id`, `level`) VALUES (%s, %s)", True, data)
		await sql_pool.pool.release(conn, cur)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
@commands.is_owner()
async def addkeymaps(ctx, *args):
	try:
		await sql_pool.pool.add_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
@commands.is_owner()
async def changekeylevel(ctx):
	try:
		await sql_pool.pool.change_key_level(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
@commands.is_owner()
async def delkey(ctx, *args):
	try:
		await sql_pool.pool.del_key(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
@commands.is_owner()
async def delkeymaps(ctx, *args):
	try:
		await sql_pool.pool.del_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
@commands.is_owner()
async def transferkeymaps(ctx, *args):
	try:
		await sql_pool.pool.transfer_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")