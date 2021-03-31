from .regex import GET_PROPERTY, PLAYER_CHEESE_REQ, find_one
from typing import Dict, List

class PlayerCheese(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "getlocal r5" in content:
				if "dup" in dumpscript[line + 1]:
					if "setlocal r" in dumpscript[line + 2]:
						setlocal = (await find_one(PLAYER_CHEESE_REQ, dumpscript[line + 2]))
						if setlocal is not None:
							if "getproperty" in dumpscript[line + 3]:
								if "increment_i" in dumpscript[line + 4]:
									if f"setlocal r{int(setlocal.group(1)) + 1}" in dumpscript[line + 5]:
										if f"getlocal r{setlocal.group(1)}" in dumpscript[line + 6]:
											self["player_cheese"] = (await find_one(GET_PROPERTY, dumpscript[line + 3])).group(2)
											break
		return self