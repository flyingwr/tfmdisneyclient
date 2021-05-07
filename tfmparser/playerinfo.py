from .regex import CALL_PROPERTY, GET_PROPERTY, find_one
from typing import Dict, List

class PlayerInfo(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "<q>[public]::int = 0)(3 params, 3 optional)" in content:
				found = 0
				for x in range(line, len(dumpscript)):
					if "setlocal r5" in dumpscript[x]:
						if "callproperty" in dumpscript[x - 2]:
							self["get_x_form"] = (await find_one(CALL_PROPERTY, dumpscript[x - 2])).group(3)
					elif "setlocal r6" in dumpscript[x]:
						if "callproperty" in dumpscript[x - 2]:
							self["get_linear_velocity"] = (await find_one(CALL_PROPERTY, dumpscript[x - 2])).group(3)
					elif "getproperty <q>[public]::position" in dumpscript[x] and found < 2:
						self["pos_x" if not found else "pos_y"] = (await find_one(GET_PROPERTY, dumpscript[x + 1])).group(2)
						found += 1
					elif "constructprop" in dumpscript[x] and "10 params" in dumpscript[x]:
						if "getproperty" in dumpscript[x - 2] and "getproperty" in dumpscript[x - 5]:
							self["current_frame"] = (await find_one(GET_PROPERTY, dumpscript[x - 2])).group(2)
							self["is_jumping"] = (await find_one(GET_PROPERTY, dumpscript[x - 5])).group(2)
					elif "returnvoid" in dumpscript[x]:
						break
				break
		return self