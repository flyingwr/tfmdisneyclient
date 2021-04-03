from .regex import GET_LEX, GET_PROPERTY, find_one
from typing import Dict, List

class JumpClass(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "convert_i" in content:
				if "setlocal_2" in dumpscript[line + 1]:
					if "getlocal_2" in dumpscript[line + 2]:
						if "getlocal_1" in dumpscript[line + 3]:
							if "getproperty" in dumpscript[line + 4]:
								if "subtract" in dumpscript[line + 5]:
									if "getlex" in dumpscript[line + 6]:
										if "getproperty" in dumpscript[line + 7]:
											self["jump_class_name"] = (await find_one(GET_LEX, dumpscript[line + 6])).group(1)
											self["num_to_add"] = (await find_one(GET_PROPERTY, dumpscript[line + 7])).group(2)
											break
		return self