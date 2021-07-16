from .animclass import AnimClass
from .bypasscode import BypassCode
from .chat import Chat
from .checker import Checker
from .frameloop import FrameLoop
from .gameui import UiElement
from .jumpclass import JumpClass
from .mapclass import Map
from .mass import Mass
from .moveclass import MoveClass
from .mouseinfo import MouseInfo
from .physicmotor import PhysicMotor
from .packethandler import PacketHandler
from .packetout import PacketOut
from .player import Player
from .playercheese import PlayerCheese
from .playerclip import PlayerClip
from .playerid import PlayerID
from .playerinfo import PlayerInfo
from .playerlist import PlayerList
from .playername import PlayerName
from .playerphysics import PlayerPhysics
from .playertitle import PlayerTitle
from .setv import SetV
from .shamanobj import ShamanObj
from .socket import Socket
from .timerclass import Timer
from .uiscoreboard import UIScoreBoard
from .swf import Swf

from typing import Dict, List, Optional

import aiofiles
import aiohttp
import asyncio
import os

class Parser:
	def __init__(self, is_local: bool = False, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

		self.dumpscript: List = []

		self.fetched: Dict = {"menu_title": "DisneyClient - Menu"}
		self.target_names: Dict = {
			"FREE": ("bypass_code", "loader_url", "chat_class_name", "chat_container", "chat_instance",
					"chat_class_name2", "chat_message2", "chat_text_field", "chat_message",
					"menu_title", "player_list", "player_name", "player", "player_clip",
					"player_id", "is_dead", "event_chat_text", "chat_is_upper", "chat_shift", "player_cheese",
					"ui_element_class_name", "set_box", "set_draggable","set_prep_ui", "prep_ui_class_name",
					"get_definition", "domain_manager_class_name", "load_img", "ui_manager_class_name",
					"on_mouse_box", "add_ui_element", "ui_sprite_class_name", "ui_sprite2_class_name",
					"on_mouse_click", "prep_ui4_instance", "main_ui_class_name", "add_ui", "set_shape",
					"ui_button_class_name", "ui_check_box_class_name", "check_box_callback", "prep_ui1_instance",
					"set_scrollable", "ui_input_class_name", "text_field", "set_display_text", "ui_check_button_class_name",
					"text_field2", "is_selected", "check_button_exec", "reset_ui", "ui_text_field_class_name", 
					"ui_items_list_class_name", "add_to_list", "set_button_state", "button_state", "select_item",
					"player_bitmap", "check_timer", "check_timestamp", "check_id", "event_main_socket_close",
					"event_bulle_socket_close"),
			"BRONZE": ("packet_handler_class_name", "packet_handler", "player_moving_right",
						"socket_class_name", "bulle_socket_instance", "event_socket_data",
						"socket_name", "data_id", "data_offset", "data_len", "socket_data",
						"main_socket_instance", "read_data", "data_sender", "checker_class_name",
						"check_pos", "packet_out_class_name", "packet_out_bytes",
						"map_class_name", "map_instance", "obj_container", "hole_list", "clip_fromage"),
			"SILVER": ("crouch", "crouch2", "move_class_name", "move_free", "player_title",
					"player_name_color", "timer_class_name", "timer_prop",
					"tfm_obj_container", "remove_shaman_obj", "shaman_obj_list", "shaman_obj_var",
					"ui_scoreboard_class_name", "command_packet_class_name", "timer_instance",
					"timer_popup", "animation_course", "is_down", "static_animation",
					"jump", "player_moving_left", "player_physics",
					"b2vec2", "physics_state", "physics_state_vx", "physics_state_vy",
					"crouch_packet_class_name", "static_side", "get_x_form", "get_linear_velocity",
					"pos_x", "pos_y", "current_frame", "is_jumping"),
			"GOLD": ("frame_loop_class_name", "victory_time", "anim_class_name", "update_coord", "update_coord2",
					"mouse_info_class_name", "mouse_info_instance", "jump_height",
					"mouse_speed", "change_player_speed1", "change_player_speed2", "player_is_shaman",
					"shaman_handler_class_name", "jump_timestamp"),
			"PLATINUM": ("cipher", )
		}

		self.is_local: bool = is_local

		self.downloaded_swf: str = "Transformice.swf"
		self.output_swf: str = "tfm.swf"

		self.last_swf_length: int = 0

		self.anim_class: AnimClass = AnimClass()
		self.bypass_code: BypassCode = BypassCode()
		self.chat: Chat = Chat()
		self.checker: Checker = Checker()
		self.frame_loop: FrameLoop = FrameLoop()
		self.jump_class: JumpClass = JumpClass()
		self.map_class: Map = Map()
		self.mass: Mass = Mass()
		self.move_class: MoveClass = MoveClass()
		self.mouse_info: MouseInfo = MouseInfo()
		self.packet_handler: PacketHandler = PacketHandler()
		self.packet_out: PacketOut = PacketOut()
		self.physic_motor: PhysicMotor = PhysicMotor()
		self.player: Player = Player()
		self.player_cheese: PlayerCheese = PlayerCheese()
		self.player_clip: PlayerClip = PlayerClip()
		self.player_id: PlayerID = PlayerID()
		self.player_info: PlayerInfo = PlayerInfo()
		self.player_list: PlayerList = PlayerList()
		self.player_name: PlayerName= PlayerName()
		self.player_physics: PlayerPhysics = PlayerPhysics()
		self.player_title: PlayerTitle = PlayerTitle()
		self.set_v: SetV = SetV()
		self.shaman_obj: ShamanObj = ShamanObj()
		self.socket_class: Socket = Socket()
		self.timer_class: Timer = Timer()
		self.ui_element: UiElement = UiElement()
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
					result[k][_v] = name.replace("\\", "")
		return result

	async def run_console(self, target: str):
		self.dumpscript *= 0

		proc = await asyncio.create_subprocess_exec(
			os.path.join(os.getcwd(), "tools", "swfdump.exe") if self.is_local else "swfdump", "-a", target,
			stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)

		while True:
			line = await proc.stdout.readline()
			if not line:
				break
			self.dumpscript.append(line.decode().rstrip())

		await proc.wait()

	async def download_swf(self):
		update = False

		try:
			async with aiohttp.ClientSession() as session:
				async with session.get("https://www.transformice.com/Transformice.swf") as response:
					length = int(response.headers.get("Content-Length", 0))
					if response.status == 200:
						if length != self.last_swf_length:
							print("Downloading Transformice.swf")

							async with aiofiles.open(self.downloaded_swf, "wb") as f:
								await f.write(await response.read())
							self.last_swf_length = length
							update = True
					else:
						self.last_swf_length = 0
		except Exception:
			print("Failed to download Transformice SWF")

		return update

	async def start(self):
		update = await self.download_swf()
		if update:
			try:
				await self.run_console(self.downloaded_swf)
				swf = Swf(self.downloaded_swf, self.output_swf)
				await self.loop.create_task(swf.parse_content(self.dumpscript))
				await self.run_console(self.output_swf)
			except Exception as e:
				print(f"Failed to parse Transformice SWF: {e}")
			else:
				names = ("socket_class", "bypass_code", "chat", "frame_loop", "checker",
						"map_class", "move_class", "packet_handler", "packet_out", "player_list",
						"player_clip", "player_name", "player_id", "player_cheese", "player_title",
						"player_physics", "player", "shaman_obj", "timer_class", "ui_scoreboard",
						"anim_class", "mouse_info", "jump_class", "player_info", "ui_element")
				for result in await asyncio.gather(*[(
					getattr(self, name)).fetch(self.dumpscript) for name in names
				]):
					self.fetched.update(result)

				print("Parser data has been updated.")