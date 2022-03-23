from string import ascii_lowercase, digits
chars = ascii_lowercase + digits

from data import client
from discord.ext import commands
from typing import ByteString, Optional
from utils import cryptjson

import aiofiles
import infrastructure
import random
import re

class Admin(commands.Cog, name="admin"):
	"""
		Ademir comandos
	"""
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot

		self.map_data: ByteString = b""

	async def cog_after_invoke(self, ctx):
		if not ctx.command_failed:
			keys = getattr(ctx, "_keys", None)
			keys_msg = f" | Key gerada: {', '.join(keys)}" if keys else ""
			await self.bot.priv_channel.send(f"`{ctx.author}` usou o comando: `{ctx.message.content}`{keys_msg}")

	@commands.command(help="Gerar uma key específica")
	@commands.has_role("admin")
	async def setkey(self, ctx, key: str, level: Optional[str] = "GOLD_II"):
		user = client.set_user(key, level)
		await ctx.reply(f"Nova key gerada: `{key}`")

	@commands.command(help="Adicionar mapas para a key")
	@commands.has_role("admin")
	async def setmaps(self, ctx, *args):
		if not self.map_data:
			async with aiofiles.open("./public/maps.json", "rb") as f:
				self.map_data = await f.read()

		for arg in args:
			_map = client.find_map_by_key(arg)
			if not _map:
				client.set_map(arg, self.map_data)

		await ctx.reply("Mapas adicionados")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def hidekey(self, key: str, state: Optional[bool] = True):
		user = client.find_user_by_key(key)
		if user:
			user.key_hidden = state
			client.commit()

			await ctx.reply(f"Status hidden da key: `{state}`")
		else:
			await ctx.reply("Key não encontrada")

	@commands.command(help="Deletar key")
	@commands.has_role("admin")
	async def delkey(self, ctx, *args):
		for arg in args:
			user = client.find_user_by_key(arg)
			if user:
				client.delete(user)
		client.commit()

		suf = "s" if len(args) > 1 else ""
		await ctx.reply(f"Key{suf} deletada{suf}")

	@commands.command(hidden=True, help="Deletar mapas da key")
	@commands.is_owner()
	async def delmaps(self, ctx, *args):
		for arg in args:
			client.delete(client.find_map_by_key(arg))
		client.commit()

		await ctx.reply("Mapas deletados")

	@commands.command(hidden=True, help="Resetar mapas da key")
	@commands.is_owner()
	async def resetmaps(self, ctx, *args):
		for arg in args:
			_map = client.find_map_by_key(arg)
			if _map:
				_map.data = b""
		client.commit()

		await ctx.reply("Mapas resetados")

	@commands.command(help="Transferir mapas de uma key pra outra")
	@commands.has_role("admin")
	async def transfermaps(self, ctx, _from: str, to: str):
		from_maps = client.find_map_by_key(_from)
		if from_maps:
			user = client.find_user_by_key(to)
			if user:
				client.set_map(to, from_maps.data)
				await ctx.reply(f"Mapas da key `{_from}` transferidos para `{to}`")
			else:
				await ctx.reply(f"Key `{to}` não encontrada")
		else:
			await ctx.reply(f"Key `{_from}` não tem mapas")

	@commands.command(help="Transferir mapas do modo soft de uma key pra outra")
	@commands.has_role("admin")
	async def transfersoft(self, ctx, _from: str, to: str):
		from_soft = client.find_soft_by_key(_from)
		if from_soft:
			user = client.find_user_by_key(to)
			if user:
				if user.level == "PLATINUM":
					client.set_soft(to, from_soft.maps)
					await ctx.reply(f"Mapas soft da key `{_from}` transferidos para `{to}`")
				else:
					await ctx.reply(f"Key `{key}` não tem o nível para mapas soft")
			else:
				await ctx.reply(f"Key `{to}` não encontrada")
		else:
			await ctx.reply(f"Key `{_from}` não tem mapas soft")

	@commands.command(help="Resetar config da key")
	@commands.has_role("admin")
	async def resetconfig(self, ctx, key: str):
		client.set_config(key, None)

		await ctx.reply(f"Configuração resetada")

	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def resetbrowser(self, ctx, key: str):
		user = client.set_user_browser_token(key)
		if user:
			await ctx.reply("Browser resetado")
		else:
			await ctx.reply(f"Key não encontrada")

	@commands.command(help="Dar permissão pra key ser usada em navegador")
	@commands.has_role("admin")
	async def setbrowserperm(self, ctx, key: str, perm: Optional[bool] = True):
		user = client.find_user_by_key(key)
		if user:
			user.browser_access = perm
			client.commit()

			await ctx.reply("Permissão atualizada")
		else:
			await ctx.reply(f"Key não encontrada")

	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def resetsoft(self, ctx, key: str):
		user = client.find_user_by_key(key)
		if user:
			if user.level == "PLATINUM":
				client.set_soft(key)
				await ctx.reply("Mapas soft resetados")
			else:
				await ctx.reply(f"Key `{key}` não tem o nível para mapas soft")
		else:
			await ctx.reply("Key não encontrada")

	@commands.command(help="Mudar limite de ip da key")
	@commands.has_role("admin")
	async def setconnlimit(self, ctx, key: str, limit: Optional[int] = 1):
		user = client.find_user_by_key(key)
		if user:
			user.connection_limit = limit if limit > 0 else 1
			client.commit()

			await ctx.reply("Limite atualizado")
		else:
			await ctx.reply("Key não encontrada")


	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def delunusedmaps(self, ctx: commands.Context):
		maps = []
		for _map in client.load_only_keys():
			key = _map.key
			if not client.find_user_by_key(key):
				client.delete(_map)

				maps.append(key)
		client.commit()

		await ctx.reply(f"Mapas removidos: `{', '.join(maps)}`")

	@commands.command(help="Gerar nova key", usage="`newkey [quantidade] [nível]`")
	@commands.has_role("admin")
	async def newkey(self, ctx, quant: Optional[int] = 1, level: Optional[str] = "GOLD_II"):
		keys = []

		for _ in range(quant):
			while True:
				key = "".join(random.sample(chars, 8))
				user = client.find_user_by_key(key)
				if not user:
					client.set_user(key=key, level=level)

					keys.append(key)
					break

		setattr(ctx, "_keys", keys)
		await ctx.reply(f"Nova key gerada: `{', '.join(keys)}`")

	@commands.command(help="Resetar acesso da key")
	@commands.has_role("admin")
	async def resetkey(self, ctx, key: str):
		user = client.find_user_by_key(key)
		if user:
			user.browser_access = True
			user.browser_access_token = None
			client.commit()

			await ctx.reply("Acesso resetado")
		else:
			await ctx.reply("Key não encontrada")

def setup(bot):
	bot.add_cog(Admin(bot))