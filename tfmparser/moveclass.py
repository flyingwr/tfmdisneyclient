from .regex import GET_LEX, GET_PROPERTY, find_one
from typing import Dict, List

class MoveClass(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "convert_d" in content:
				if "setlocal r25" in dumpscript[line + 1]:
					if "getlocal_3" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "not" in dumpscript[line + 4]:
								if "dup" in dumpscript[line + 5]:
									if "iffalse" in dumpscript[line + 6]:
										if "pop" in dumpscript[line + 7]:
											if "getlex" in dumpscript[line + 8]:
												if "getproperty" in dumpscript[line + 9]:
													self["move_class_name"] = (await find_one(GET_LEX, dumpscript[line + 8])).group(1)
													self["move_free"] = (await find_one(GET_PROPERTY, dumpscript[line + 9])).group(2)
													break
		return self