from discordbot import Bot
from tfmparser import Parser
from typing import ByteString, Dict


import asyncio
import os
import ujson

with open("./config.json") as f:
	config = ujson.load(f)

is_local: bool = "C:" in os.getcwd()

discord: Bot = None
records_data: ByteString = None

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
parser: Parser = Parser(is_local, loop)

ips: Dict = {}
tokens: Dict = {}
