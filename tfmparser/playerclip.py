from .regex import GET_PROPERTY, find_one
from typing import Dict, List

class PlayerClip(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "getproperty" in content:
				if "bitor" in dumpscript[line + 1]:
					if "bitand" in dumpscript[line + 2]:
						if "iffalse" in dumpscript[line + 3]:
							if "jump" in dumpscript[line + 4]:
								if "getlocal_2" in dumpscript[line + 5]:
									if "callproperty" in dumpscript[line + 6]:
										if "iffalse" in dumpscript[line + 7]:
											if "jump" in dumpscript[line + 8]:
												if "getlocal_2" in dumpscript[line + 9]:
													if "getproperty" in dumpscript[line + 10]:
														self["player_clip"] = (await find_one(GET_PROPERTY, dumpscript[line + 10])).group(2)
														break
		return self