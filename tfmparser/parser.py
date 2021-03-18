from typing import Dict, Optional

from .bypasscode import BypassCode
from .chat import Chat
from .frameloop import FrameLoop
from .mapclass import Map
from .moveclass import MoveClass
from .packethandler import PacketHandler
from .packetout import PacketOut
from .player import Player
from .playercheese import PlayerCheese
from .playerclip import PlayerClip
from .playerid import PlayerID
from .playerlist import PlayerList
from .playername import PlayerName
from .playerphysics import PlayerPhysics
from .playertitle import PlayerTitle
from .shamanobj import ShamanObj
from .socket import Socket
from .timerclass import Timer
from .uiscoreboard import UIScoreBoard
from .swf import Swf

import aiofiles
import aiohttp
import asyncio
import subprocess

class Parser:
	def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

		self.dumpscript: List = []

		self.fetched: Dict = {"menu_title": "DisneyClient - Menu"}
		self.target_names: Dict = {
			"FREE": ("bypass_code", "chat_class_name", "chat_container", "chat_instance",
					"chat_class_name2", "chat_message2", "chat_text_field", "chat_message",
					"menu_title", "player_list", "player_name", "player", "player_clip",
					"player_id", "is_dead", "event_chat_text", "chat_is_upper", "chat_shift", "player_cheese"),
			"GOLD": ("crouch", "move_class_name", "move_free", "player_title",
					"player_name_color", "timer_class_name", "timer_prop",
					"tfm_obj_container", "remove_shaman_obj", "shaman_obj_list", "shaman_obj_var",
					"ui_scoreboard_class_name", "socket_class_name", "bulle_socket_instance",
					"event_socket_data", "socket_name", "data_id", "data_offset", "data_len",
					"socket_data", "main_socket_instance", "read_data", "data_sender",
					"command_packet_name", "timer_instance", "timer_popup", "packet_handler_class_name",
					"packet_handler", "animation_course", "is_down", "static_animation", "frame_loop_class_name",
					"victory_time", "jump", "player_moving_right", "player_moving_left", "player_physics",
					"x_form", "b2vec2", "physics_state", "physics_state_vx", "physics_state_vy",
					"crouch_packet_name", "static_side", "map_class_name", "map_instance", "obj_container",
					"hole_list", "clip_fromage", "packet_out_name", "packet_out_bytes"),
			"PLATINUM": ("cipher", )
		}

		self.downloaded_swf: str = "Transformice.swf"
		self.output_swf: str = "tfm.swf"

		self.bypass_code: BypassCode = BypassCode()
		self.chat: Chat = Chat()
		self.frame_loop: FrameLoop = FrameLoop()
		self.map_class: Map = Map()
		self.move_class: MoveClass = MoveClass()
		self.packet_handler: PacketHandler = PacketHandler()
		self.packet_out: PacketOut = PacketOut()
		self.player: Player = Player()
		self.player_cheese: PlayerCheese = PlayerCheese()
		self.player_clip: PlayerClip = PlayerClip()
		self.player_id: PlayerID = PlayerID()
		self.player_list: PlayerList = PlayerList()
		self.player_name: PlayerName= PlayerName()
		self.player_physics: PlayerPhysics = PlayerPhysics()
		self.player_title: PlayerTitle = PlayerTitle()
		self.shaman_obj: ShamanObj = ShamanObj()
		self.socket_class: Socket = Socket()
		self.timer_class: Timer = Timer()
		self.ui_scoreboard: UIScoreBoard = UIScoreBoard()

	def keys(self) -> Dict:
		result = {}
		for k, v in self.target_names.items():
			result[k] = {}
			for _v in v:
				name = self.fetched.get(_v)
				if name is None:
					print(f"Key {_v} missing")
				else:
					result[k][_v] = name
		return result

	def run_console(self, target: str):
		self.dumpscript *= 0

		console = subprocess.Popen(["tools/swfdump", "-a", target], shell=False,
			stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in console.stdout:
			self.dumpscript.append(line.decode().rstrip())

	async def download_swf(self):
		print("Downloading Transformice.swf")

		async with aiohttp.ClientSession() as session:
			async with session.get("https://www.transformice.com/Transformice.swf") as response:
				if response.status == 200:
					async with aiofiles.open(self.downloaded_swf, "wb") as f:
						await f.write(await response.read())

	async def start(self):
		await self.loop.create_task(self.download_swf())
		self.run_console(self.downloaded_swf)

		swf = Swf(self.downloaded_swf, self.output_swf)
		await swf.parse_content(self.dumpscript)

		self.run_console(self.output_swf)

		names = ("socket_class", "bypass_code", "chat", "frame_loop",
				"map_class", "move_class", "packet_handler", "packet_out", "player_list",
				"player_clip", "player_name", "player_id", "player_cheese", "player_title",
				"player_physics", "player", "shaman_obj", "timer_class", "ui_scoreboard")
		for result in await asyncio.gather(*[(getattr(self, name)).fetch(self.dumpscript) for name in names]):
			self.fetched.update(result)

		print("Parser data has been updated.")