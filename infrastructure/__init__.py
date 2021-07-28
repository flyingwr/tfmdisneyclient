from aiohttp import ClientSession
from discordbot import Bot
from typing import ByteString, Dict


import asyncio
import os


is_local: bool = "C:" in os.getcwd()

parser_url: str = "https://tfmdisneyparser.herokuapp.com"
tfm_parser_token: str = os.getenv("TFM_PARSER_API_TOKEN")

config: Dict = None
discord: Bot = None
records_data: ByteString = None

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
session: ClientSession = ClientSession()

ips: Dict = {}
tokens: Dict = {}
