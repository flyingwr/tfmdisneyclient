from .regex import GET_PROPERTY, find_one
from typing import Dict, List

class Player(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "convert_b" in content:
				if "dup" in dumpscript[line + 1]:
					if "iffalse" in dumpscript[line + 2]:
						if "pop" in dumpscript[line + 3]:
							if "getlex" in dumpscript[line + 4]:
								if "getproperty" in dumpscript[line + 5]:
									if "getproperty" in dumpscript[line + 6]:
										if "getproperty" in dumpscript[line + 7]:
											if "parent" not in dumpscript[line + 7]:
												if "not" in dumpscript[line + 8]:
													if "iffalse" in dumpscript[line + 9]:
														self["player"] = (await find_one(GET_PROPERTY, dumpscript[line + 6])).group(2)
														self["is_dead"] = (await find_one(GET_PROPERTY, dumpscript[line + 7])).group(2)
														break
		return self