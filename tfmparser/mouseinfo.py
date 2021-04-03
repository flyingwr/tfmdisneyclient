from .regex import CALL_PROPVOID, GET_LEX, GET_PROPERTY, INIT_PROPERTY, SET_PROPERTY, find_one
from typing import Dict, List

class MouseInfo(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "getlocal_2" in content:
				if "getproperty" in dumpscript[line + 1]:
					if "iffalse" in dumpscript[line + 2]:
						if "getlex" in dumpscript[line + 3]:
							if "getproperty" in dumpscript[line + 4]:
								if "getlocal_1" in dumpscript[line + 5]:
									if "callproperty <q>[public]::readUnsignedByte, 0 params" in dumpscript[line + 6]:
										for x in range(line + 5, line + 12):
											if "divide" in dumpscript[x]:
												if "setproperty" in dumpscript[x + 1]:
													self["mouse_info_class_name"] = (
														await find_one(GET_LEX, dumpscript[line + 3])
													).group(1)
													self["mouse_info_instance"] = (
														await find_one(GET_PROPERTY, dumpscript[line + 4])
													).group(2)
													self["jump_height"] = (
														await find_one(SET_PROPERTY, dumpscript[x + 1])
													).group(1)
													break
										else:
											continue
										break

		mouse_info_class = self.get("mouse_info_class_name")
		if mouse_info_class is not None:
			for line, content in enumerate(dumpscript):
				if "class <q>[public]::" + mouse_info_class in content:
					for x in range(line, len(dumpscript)):
						if "=(<q>[public]::int, <q>[public]::int)(2 params, 0 optional)" in dumpscript[x]:
							if "pushbyte 0" in dumpscript[x + 5]:
								if "setlocal_3" in dumpscript[x + 6]:
									if "pushnull" in dumpscript[x + 7]:
										if "coerce <q>[public]flash.display::MovieClip" in dumpscript[x + 8]:
											if "setlocal r4" in dumpscript[x + 9]:
												for y in range(x + 9, x + 20):
													if "initproperty" in dumpscript[y]:
														self["mouse_speed"] = (
															await find_one(INIT_PROPERTY, dumpscript[y])
														).group(1)
														break
												break
		for line, content in enumerate(dumpscript):
			if "callproperty <q>[public]::readByte, 0 params" in content:
				if "convert_i" in dumpscript[line + 1]:
					if "setlocal_3" in dumpscript[line + 2]:
						if "getlocal_2" in dumpscript[line + 3]:
							if "iffalse" in dumpscript[line + 4]:
								if "getlex" in dumpscript[line + 5]:
									if "getproperty" in dumpscript[line + 6]:
										if "getlocal_2" in dumpscript[line + 7]:
											if "getlocal_3" in dumpscript[line + 8]:
												if "callpropvoid" in dumpscript[line + 9]:
													self["change_player_physic2"] = (
														await find_one(CALL_PROPVOID, dumpscript[line + 9])
													).group(1)
													break
		return self