from datetime import datetime
from discord.ext import commands
# from pasteee import new_paste

from typing import Dict, Optional, Union

import asyncio
import discord

loop = asyncio.get_event_loop()
bot = commands.Bot(command_prefix=".")

channel = None

@bot.event
async def on_ready():
	print("[Discord] Logged in.")

	global channel
	channel = bot.get_channel(829368194812346448)

async def log(
	method: str,
	response: Dict,
	status: int,
	addr: Optional[str] = None,
	key: Optional[str] = None,
	token: Optional[str] = None
):
	if channel is not None:
		access_token = response.get("access_token") or token
		sleep = f"(:timer: {response.get('sleep', 0)} min)"
		success = status == 200

		embed = discord.Embed(title=f"Log - {method}",
			description=f":computer: IP address: {addr}\n"
			f":placard: Status: {status} {':white_check_mark:' if success else ':x:'}\n"
			f":warning: Error: {response.get('error')}\n\n"
			f":credit_card: Key: {key}\n"
			f":credit_card: Token: {access_token} {sleep if response.get('sleep') is not None else ''}",
			colour=0x00FF00 if success else 0xFF0000
		)
		await channel.send(embed=embed)
	else:
		print("[Discord] Invalid channel")