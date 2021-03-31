from .regex import CLASS, PUBLIC_METHOD, find_one
from typing import Dict, List

class PhysicMotor(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "<q>[public]::int, <q>[public]::Number = 1, <q>[public]::Boolean = true)(4 params, 2 optional)" in content:
				self["change_player_physic"] = (await find_one(PUBLIC_METHOD, content)).group(1)
				for x in range(line, 0, -1):
					if "class" in dumpscript[x]:
						self["physic_motor_class_name"] = (await find_one(CLASS, dumpscript[x])).group(1)
						break
				break
		return self