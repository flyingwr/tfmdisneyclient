from .regex import SET_PROPERTY, find_one
from typing import Dict, List

class JumpClass(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "getlocal_1" in content:
				if "findpropstrict" in dumpscript[line + 1] and "getTimer" in dumpscript[line + 1]:
					if "callproperty" in dumpscript[line + 2] and "getTimer" in dumpscript[line + 2]:
						if "setproperty" in dumpscript[line + 3] and "returnvoid" in dumpscript[line + 4]:
							self["jump_timestamp"] = (await find_one(SET_PROPERTY, dumpscript[line + 3])).group(1)
							break
		return self