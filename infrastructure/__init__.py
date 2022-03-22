from aiohttp import ClientSession
from collections import defaultdict
from discordbot import Bot
from typing import ByteString, Dict

import asyncio
import os

is_local: bool = "C:" in os.getcwd()

parser_url: str = os.getenv("TFM_PARSER_ENDPOINT")
tfm_parser_token: str = os.getenv("TFM_PARSER_API_TOKEN")

config: Dict = None
discord: Bot = None
records_data: ByteString = None

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
session: ClientSession = ClientSession()

auth_attempts: defaultdict = defaultdict(int)
blacklisted_ips: Dict = {}
ips: Dict = {}
tokens: Dict = {}
