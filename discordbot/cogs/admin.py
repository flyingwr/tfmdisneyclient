from string import ascii_lowercase, digits
chars = ascii_lowercase + digits

from discord.ext import commands
from services.mongodb import find_map_by_key, find_user_by_key, \
	set_config, set_map, set_soft, set_user, set_user_browser_token, set_blacklist, \
	del_blacklist
from typing import Optional


from data.map import Map
from data.user import User


import aiofiles
import random


class Admin(commands.Cog, name="admin"):
	"""
		Ademir comandos
	"""


	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot


	@commands.command(hidden=True)
	@commands.is_owner()
	async def setkey(self, ctx, key: str, level: Optional[str] = "GOLD_II"):
		set_user(key, level)

		await ctx.reply("Database updated")


	@commands.command(hidden=True)
	@commands.is_owner()
	async def setkeymaps(self, ctx, *args):
		async with aiofiles.open("./public/maps.json", "rb") as f:
			map_data = await f.read()

		for arg in args:
			_map = find_map_by_key(arg)
			if not _map:
				set_map(arg, map_data)

		await ctx.reply("Database updated")


	@commands.command(help="Deletar key")
	@commands.has_role("admin")
	async def delkey(self, ctx, *args):
		for arg in args:
			User.objects(key=arg).delete()

		await ctx.reply("Database updated")


	@commands.command(help="Deletar mapas da key")
	@commands.has_role("admin")
	async def delkeymaps(self, ctx, *args):
		for arg in args:
			Map.objects(key=arg).delete()

		await ctx.reply("Database updated")


	@commands.command(help="Transferir mapas de uma key pra outra")
	@commands.has_role("admin")
	async def transferkeymaps(self, ctx, _from: str, to: str):
		from_maps = find_map_by_key(_from)
		if from_maps:
			set_map(to, from_maps.data)

		await ctx.reply("Database updated")


	@commands.command(help="Resetar config da key")
	@commands.has_role("admin")
	async def resetconfig(self, ctx, key: str):
		set_config(key, None)

		await ctx.reply("Database updated")


	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def resetbrowsertoken(self, ctx, key: str):
		if key == "all":
			for user in User.objects:
				user.update(browser_access=True, browser_access_token=None)
		else:
			set_user_browser_token(key)

		await ctx.reply("Database updated")

	@commands.command(help="Dar permissão pra key ser usada em navegador")
	@commands.has_role("admin")
	async def setbrowserperm(self, ctx, key: str, perm: Optional[bool] = True):
		if key == "all":
			for user in User.objects:
				user.update(browser_access=perm)
		else:
			user = find_user_by_key(key)
			if user:
				user.update(browser_access=perm)

		await ctx.reply("Database updated")


	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def resetsoftmaps(self, ctx, key: str):
		set_soft(key)

		await ctx.reply("Database updated")


	@commands.command(help="Mudar limite de ip da key")
	@commands.has_role("admin")
	async def setconnlimit(self, ctx, key: str, limit: Optional[int] = 1):
		user = find_user_by_key(key)
		if user:
			user.update(connection_limit=limit if limit > 0 else 1)
			await ctx.reply("Database updated")
		else:
			await ctx.reply("User not found")


	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def delunusedmaps(self, ctx: commands.Context):
		maps = []

		for _map in Map.objects().only("key"):
			key = _map.key
			if not find_user_by_key(key):
				_map.delete()

				maps.append(key)

		await ctx.reply(f"Maps removed: `{''.join(maps)}`")


	@commands.command(help="Add ip na blacklist")
	@commands.has_role("admin")
	async def blacklist(self, ctx, addr: str):
		set_blacklist(addr)

		await ctx.reply("Database updated")


	@commands.command(help="Tirar ip da blacklist")
	@commands.has_role("admin")
	async def delblacklist(self, ctx, addr: str):
		del_blacklist(addr)

		await ctx.reply("Database updated")

	@commands.command(help="Gerar nova key", usage="`newkey [quantidade]`")
	@commands.has_role("admin")
	async def newkey(self, ctx, level: Optional[str] = "GOLD_II", quant: Optional[int] = 1):
		keys = []

		for _ in range(quant):
			while True:
				key = "".join(random.sample(chars, 8))
				user = User.objects(key=key).first()
				if not user:
					User(key=key, premium_level=level).save()

					keys.append(key)
					break

		await ctx.reply(f"New key generated: `{', '.join(keys)}`")

	@commands.command(help="Resetar acesso da key")
	@commands.has_role("admin")
	async def resetkey(self, ctx, key: str):
		user = find_user_by_key(key)
		if user:
			user.update(browser_access_token=None, uuid=None)

		await ctx.reply("Database updated")

def setup(bot):
	bot.add_cog(Admin(bot))
