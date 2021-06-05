from discord import NotFound
from sql_pool import pool

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
async def addkey(ctx, *args):
	try:
		data = []
		for s in args:
			info = s.split(":")
			level = "SILVER"
			if len(info) > 1:
				level = info[1].upper()
			data.append((info[0], level))

		conn, cur = await pool.exec("INSERT INTO `users` (`id`, `level`) VALUES (%s, %s)", True, data)
		await pool.release(conn, cur)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
async def addkeymaps(ctx, *args):
	try:
		await pool.add_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
async def changekeylevel(ctx):
	try:
		await pool.change_key_level(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
async def delkey(ctx, *args):
	try:
		await pool.del_key(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
async def delkeymaps(ctx, *args):
	try:
		await pool.del_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")

@_bot.command()
async def transferkeymaps(ctx, *args):
	try:
		await pool.transfer_key_maps(*args)
	except Exception as e:
		await ctx.reply(f"Query failed ({e})")
	else:
		await ctx.reply("Database updated")