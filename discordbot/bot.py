from discord import Embed
from discord.ext import commands

from typing import Any, Dict, Optional, Union

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