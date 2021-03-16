from .regex import CLASS, GET_PROPERTY, find_one
from typing import Dict, List

class UIScoreBoard(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		_class = None

		for line, content in enumerate(dumpscript):
			if "getlocal_0" in content:
				if "pushscope" in dumpscript[line + 1]:
					if "getlocal_0" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "getlocal_1" in dumpscript[line + 4]:
								if "setproperty <q>[public]::visible" in dumpscript[line + 5]:
									if "returnvoid" in dumpscript[line + 6]:
										for x in range(line, 0, -1):
											if "class <q>[public]::" in dumpscript[x]:
												_class = await find_one(CLASS, dumpscript[x])
												self["ui_scoreboard_class_name"] = _class.group(1)
												break
										else:
											continue
										break

		if _class is not None:
			for line, content in enumerate(dumpscript):
				if "findpropstrict" in content and _class.group(1) in content:
					self["tfm_obj_container"] = (await find_one(GET_PROPERTY, dumpscript[line - 1])).group(2)
					break

		return self