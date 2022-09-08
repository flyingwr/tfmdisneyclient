from aiohttp import ClientSession
from collections import defaultdict
from discordbot import Bot
from typing import ByteString, Dict

import asyncio
import os

is_local: bool = "DYNO" not in os.environ
if is_local:
	from dotenv import load_dotenv
	load_dotenv()

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
sessions: Dict = {}
tokens: Dict = {}

tfm_swf_expected_len: int = 0