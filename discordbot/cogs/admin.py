from string import ascii_lowercase, digits
chars = ascii_lowercase + digits

from discord.ext import commands

from data import client
from discord import Embed
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
			keys_msg = f" | Key gerada: `{', '.join(keys)}`" if keys else ""
			await self.bot.priv_channel.send(f"`{ctx.author}` usou o comando: `{ctx.message.content}`{keys_msg}")

	@commands.command(help="Gerar uma key específica")
	@commands.has_role("admin")
	async def setkey(self, ctx, key: str, level: Optional[str] = "GOLD_II"):
		client.set_user(key, level)
		await ctx.reply(f"Nova key gerada: `{key}`")

	@commands.command(help="Adicionar mapas para a key")
	@commands.has_role("admin")
	async def setmaps(self, ctx, *args):
		if not self.map_data:
			async with aiofiles.open("./public/maps.json", "rb") as f:
				self.map_data = await f.read()

		result = []
		for key in args:
			if (_map := client.find_map_by_key(key, check_exists=True)) is None:
				client.set_map(key, self.map_data)

				result.append(key)

		await ctx.reply(f"Mapas adicionados: `{', '.join(result)}`")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def hidekey(self, key: str, state: Optional[bool] = True):
		if (user := client.find_user_by_key(key)) is not None:
			user.key_hidden = state
			client.commit()

			await ctx.reply(f"Status hidden da key: `{state}`")
		else:
			await ctx.reply("Key não encontrada")

	@commands.command(help="Deletar key")
	@commands.has_role("admin")
	async def delkey(self, ctx, *args):
		result = []
		for key in args:
			if (user := client.find_user_by_key(key, check_exists=True)) is not None:
				client.delete(user)

				result.append(key)
		if result:
			client.commit()

		await ctx.reply(f"Keys deletadas: `{', '.join(result)}`")

	@commands.command(hidden=True, help="Deletar mapas da key")
	@commands.is_owner()
	async def delmaps(self, ctx, *args):
		result = []
		for key in args:
			if (_map := client.find_map_by_key(key, check_exists=True)) is not None:
				client.delete(_map)

				result.append(key)
		if result:
			client.commit()

		await ctx.reply(f"Mapas deletados: `{', '.join(result)}`")

	@commands.command(hidden=True, help="Resetar mapas da key")
	@commands.is_owner()
	async def resetmaps(self, ctx, *args):
		result = []
		for key in args:
			if (_map := client.find_map_by_key(key)) is not None:
				_map.data = b""

				result.append(key)
		if result:
			client.commit()

		await ctx.reply(f"Mapas resetados: `{', '.join(result)}`")

	@commands.command(help="Transferir mapas de uma key pra outra")
	@commands.has_role("admin")
	async def transfermaps(self, ctx, _from: str, to: str):
		if (from_user := client.find_user_by_key(_from)) is not None:
			if (from_maps := client.find_map_by_key(_from)) is not None:
				if (user := client.find_user_by_key(to)) is not None:
					client.set_map(to, from_maps.data)
					await ctx.reply(f"Mapas da key `{_from}` transferidos para `{to}`")
				else:
					await ctx.reply(f"Key `{to}` não encontrada")
			else:
				await ctx.reply(f"Key `{_from}` não tem mapas")
		else:
			await ctx.reply(f"Key `{_from}` não encontrada")

	@commands.command(help="Transferir mapas do modo soft de uma key pra outra")
	@commands.has_role("admin")
	async def transfersoft(self, ctx, _from: str, to: str):
		if _from in infrastructure.config["soft_forbidden_keys"]:
			for role in ctx.author.roles:
				if role.id == infrastructure.config["discord_major_role_id"]:
					break
			else:
				await ctx.reply(f"Key `{_from}` não encontrada")
				return

		if (from_user := client.find_user_by_key(_from)) is not None:
			if (from_soft := client.find_soft_by_key(_from)) is not None:
				if (user := client.find_user_by_key(to)) is not None:
					if user.level == "PLATINUM":
						client.set_soft(to, from_soft.maps)
						await ctx.reply(f"Mapas soft da key `{_from}` transferidos para `{to}`")
					else:
						await ctx.reply(f"Key `{key}` não tem o nível para mapas soft")
				else:
					await ctx.reply(f"Key `{to}` não encontrada")
			else:
				await ctx.reply(f"Key `{_from}` não tem mapas soft")
		else:
			await ctx.reply(f"Key `{_from}` não encontrada")

	@commands.command(hidden=True)
	@commands.has_role("kpopper")
	async def lssoft(self, ctx, key: Optional[str] = "all", more_than: Optional[int] = None):
		embed = Embed(title=f"Lista de soft - {key}")
		if key == "all":			
			embed.description = "\n".join([f"{soft.key} - {'vazio' if not maps_len else '{} mapas'.format(maps_len)}" for soft in client.load_soft(more_than) if (maps_len := len(soft.maps))])
		elif (soft := client.find_soft_by_key(key)) is not None:
			embed.description = f"{maps_len} mapas" if (maps_len := len(soft.maps)) else "vazio"
		await ctx.reply(embed=embed)

	@commands.command(help="Resetar config da key")
	@commands.has_role("admin")
	async def resetconfig(self, ctx, key: str):
		client.set_config(key, None)

		await ctx.reply(f"Configuração resetada")

	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def resetbrowser(self, ctx, key: str):
		if (user := client.set_user_browser_token(key)) is not None:
			await ctx.reply("Browser resetado")
		else:
			await ctx.reply("Key não encontrada")

	@commands.command(hidden=True)
	@commands.has_role("admin")
	async def resetflash(self, ctx, key: str):
		if (user := client.set_flash_token(key)) is not None:
			await ctx.reply("Flash resetado")
		else:
			await ctx.reply("Key não encontrada")

	@commands.command(help="Dar permissão pra key ser usada em navegador")
	@commands.has_role("admin")
	async def setbrowserperm(self, ctx, key: str, perm: Optional[bool] = True):
		if (user := client.find_user_by_key(key)) is not None:
			user.browser_access = perm
			client.commit()

			await ctx.reply("Permissão atualizada")
		else:
			await ctx.reply(f"Key não encontrada")

	@commands.command(help="Resetar mapas soft da key")
	@commands.is_owner()
	async def resetsoft(self, ctx, *args):
		result = []
		for key in args:
			if (soft := client.find_soft_by_key(key)) is not None:
				soft.maps = {}

				result.append(key)

		if result:
			client.commit()

		await ctx.reply(f"Mapas resetados: `{', '.join(result)}`")

	@commands.command(help="Mudar limite de ip da key")
	@commands.has_role("admin")
	async def setconnlimit(self, ctx, key: str, limit: Optional[int] = 1):
		if (user := client.find_user_by_key(key)) is not None:
			user.connection_limit = limit if limit > 0 else 1
			client.commit()

			await ctx.reply("Limite atualizado")
		else:
			await ctx.reply("Key não encontrada")


	@commands.command(hidden=True)
	@commands.has_role("kpopper")
	async def delunusedmaps(self, ctx):
		result = []
		for _map in client.load_maps_keys():
			if client.find_user_by_key((key := _map.key)) is None:
				client.delete(_map)

				result.append(key)
		if result:
			client.commit()

		await ctx.reply(f"Mapas deletados: `{', '.join(result)}`")

	@commands.command(hidden=True)
	@commands.has_role("kpopper")
	async def delunusedsoft(self, ctx):
		result = []
		for soft in client.load_soft(only_keys=True):
			if client.find_user_by_key((key := soft.key)) is None:
				client.delete(soft)

				result.append(key)
		if result:
			client.commit()

		await ctx.reply(f"Mapas deletados: `{', '.join(result)}`")

	@commands.command(help="Gerar nova key", usage="`newkey [quantidade] [nível]`")
	@commands.has_role("admin")
	async def newkey(self, ctx, quant: Optional[int] = 1, level: Optional[str] = "GOLD_II"):
		keys = []

		for _ in range(quant):
			while True:
				key = "".join(random.sample(chars, 8))
				if (user := client.find_user_by_key(key)) is None:
					client.set_user(key=key, level=level)

					keys.append(key)
					break

		setattr(ctx, "_keys", keys)
		await ctx.reply(f"Nova key gerada: `{', '.join(keys)}`")

	@commands.command(help="Resetar acesso da key")
	@commands.has_role("admin")
	async def resetkey(self, ctx, key: str):
		if (user := client.find_user_by_key(key)) is not None:
			user.browser_access = True
			user.browser_access_token = None
			user.flash_token = None
			client.commit()

			await ctx.reply("Acesso resetado")
		else:
			await ctx.reply("Key não encontrada")

def setup(bot):
	bot.add_cog(Admin(bot))