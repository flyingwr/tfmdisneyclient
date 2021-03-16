from .regex import SET_PROPERTY, find_one
from typing import Dict, List

class PlayerID(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "equals" in content:
				if "setproperty" in dumpscript[line + 1]:
					if "getlocal r5" in dumpscript[line + 2]:
						if "getlocal_1" in dumpscript[line + 3]:
							if "getproperty" in dumpscript[line + 4]:
								if "setproperty" in dumpscript[line + 5]:
									if "getlocal r5" in dumpscript[line + 6]:
										if "getlocal r4" in dumpscript[line + 7]:
											if "setproperty" in dumpscript[line + 8]:
												self["player_id"] = (await find_one(SET_PROPERTY, dumpscript[line + 8])).group(1)
												break
		return self