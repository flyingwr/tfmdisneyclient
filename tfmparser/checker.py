from .regex import GET_LEX, GET_PROPERTY, find_one
from typing import Dict, List

class Checker(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "setlocal r12" in content:
				if "getlex <q>[public]::" in dumpscript[line + 1]:
					getlex = (await find_one(GET_LEX, dumpscript[line + 1])).group(1)
					if "getproperty" in dumpscript[line + 2]:
						if "iffalse" in dumpscript[line + 3]:
							if "getlex" in dumpscript[line + 4] and getlex in dumpscript[line + 4]:
								if "getproperty" in dumpscript[line + 5]:
									if "iffalse" in dumpscript[line + 6]:
										for x in range(line + 6, line + 12):
											if "getlocal r5" in dumpscript[x]:
												self["checker_class_name"] = getlex
												self["check_pos"] = (await find_one(GET_PROPERTY, dumpscript[line + 5])).group(2)
												break
										else:
											continue
										break
		return self