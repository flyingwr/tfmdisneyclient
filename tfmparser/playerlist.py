from .regex import GET_PROPERTY, find_one
from typing import Dict, List

class PlayerList(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "callproperty" in content:
				if "convert_i" in dumpscript[line + 1]:
					if "setlocal_2" in dumpscript[line + 2]:
						if "getlex" in dumpscript[line + 3]:
							if "getproperty" in dumpscript[line + 4]:
								if "getproperty" in dumpscript[line + 5]:
									if "getlocal_2" in dumpscript[line + 6]:
										if "getproperty" in dumpscript[line + 7]:
											if "coerce" in dumpscript[line + 8]:
												if "setlocal_3" in dumpscript[line + 9]:
													if "getlocal_3" in dumpscript[line + 10]:
														self["player_list"] = (await find_one(GET_PROPERTY, dumpscript[line + 5])).group(2)
														break
		return self