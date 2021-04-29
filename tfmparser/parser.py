from typing import Dict, Optional

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

import aiofiles
import aiohttp
import asyncio

class Parser:
	def __init__(self, is_local: bool = False, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

		self.dumpscript: List = []

		self.fetched: Dict = {"menu_title": "DisneyClient - Menu"}
		self.target_names: Dict = {
			"FREE": ("bypass_code", "chat_class_name", "chat_container", "chat_instance",
					"chat_class_name2", "chat_message2", "chat_text_field", "chat_message",
					"menu_title", "player_list", "player_name", "player", "player_clip",
					"player_id", "is_dead", "event_chat_text", "chat_is_upper", "chat_shift", "player_cheese"),
			"SILVER": ("crouch", "crouch2", "move_class_name", "move_free", "player_title",
					"player_name_color", "timer_class_name", "timer_prop",
					"tfm_obj_container", "remove_shaman_obj", "shaman_obj_list", "shaman_obj_var",
					"ui_scoreboard_class_name", "socket_class_name", "bulle_socket_instance",
					"event_socket_data", "socket_name", "data_id", "data_offset", "data_len",
					"socket_data", "main_socket_instance", "read_data", "data_sender",
					"command_packet_name", "timer_instance", "timer_popup", "packet_handler_class_name",
					"packet_handler", "animation_course", "is_down", "static_animation", "jump",
					"player_moving_right", "player_moving_left", "player_physics",
					"b2vec2", "physics_state", "physics_state_vx", "physics_state_vy",
					"crouch_packet_name", "static_side", "map_class_name", "map_instance",
					"obj_container", "hole_list", "clip_fromage", "packet_out_name", "packet_out_bytes",
					"get_x_form", "get_linear_velocity", "pos_x", "pos_y", "current_frame", "is_jumping"),
			"GOLD": ("frame_loop_class_name", "victory_time", "anim_class_name",
					"update_coord", "update_coord2", "checker_class_name", "check_pos",
					"mouse_info_class_name", "mouse_info_instance", "jump_height", "change_player_physic",
					"change_player_physic2", "physic_motor_class_name", "mouse_speed", "b2circledef",
					"density", "radius", "friction", "restitution", "jump_class_name", "num_to_add",
					"ui_element_class_name", "set_box", "set_draggable","set_prep_ui", "prep_ui_class_name",
					"get_definition", "domain_manager_class_name", "load_img", "ui_manager_class_name",
					"on_mouse_box", "add_ui_element", "ui_sprite_class_name", "ui_sprite2_class_name",
					"on_mouse_click", "prep_ui4_instance", "main_ui_class_name", "add_ui", "set_shape",
					"ui_button_class_name", "ui_check_box_class_name", "check_box_callback", "prep_ui1_instance",
					"set_scrollable", "ui_input_class_name", "text_field", "set_display_text", "ui_check_button_class_name",
					"text_field2", "is_selected", "set_state"),
			"PLATINUM": ("cipher", )
		}

		self.is_local: bool = is_local

		self.downloaded_swf: str = "Transformice.swf"
		self.output_swf: str = "tfm.swf"

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
			"tools/swfdump" if self.is_local else "swfdump", "-a", target,
			stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)

		while True:
			line = await proc.stdout.readline()
			if not line:
				break
			self.dumpscript.append(line.decode().rstrip())

		await proc.wait()

	async def download_swf(self):
		print("Downloading Transformice.swf")

		async with aiohttp.ClientSession() as session:
			async with session.get("https://www.transformice.com/Transformice.swf") as response:
				if response.status == 200:
					async with aiofiles.open(self.downloaded_swf, "wb") as f:
						await f.write(await response.read())

	async def start(self):
		try:
			await self.download_swf()
			await self.run_console(self.downloaded_swf)
		except Exception:
			print("Failed to parse Transformice SWF")
		else:
			swf = Swf(self.downloaded_swf, self.output_swf)
			await self.loop.create_task(swf.parse_content(self.dumpscript))
			await self.run_console(self.output_swf)

			names = ("socket_class", "bypass_code", "chat", "frame_loop", "checker",
					"map_class", "move_class", "packet_handler", "packet_out", "player_list",
					"player_clip", "player_name", "player_id", "player_cheese", "player_title",
					"player_physics", "player", "shaman_obj", "timer_class", "ui_scoreboard",
					"anim_class", "mouse_info", "physic_motor", "jump_class", "player_info",
					"ui_element")
			for result in await asyncio.gather(*[(getattr(self, name)).fetch(self.dumpscript) for name in names]):
				self.fetched.update(result)

			print("Parser data has been updated.")