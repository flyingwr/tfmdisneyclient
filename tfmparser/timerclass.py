from .regex import GET_LEX, GET_PROPERTY, INIT_PROPERTY, SET_PROPERTY, find_one
from typing import Dict, List

class Timer(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "equals" in content:
				if "dup" in dumpscript[line + 1]:
					if "iftrue" in dumpscript[line + 2]:
						if "pop" in dumpscript[line + 3]:
							if "getlocal_1" in dumpscript[line + 4]:
								if "getlex" in dumpscript[line + 5]:
									if "getproperty" in dumpscript[line + 6]:
										if "equals" in dumpscript[line + 7]:
											if "iffalse" in dumpscript[line + 8]:
												if "getlex" in dumpscript[line + 9]:
													if "getproperty" in dumpscript[line + 10]:
														if "iftrue" in dumpscript[line + 11]:
															self["timer_class_name"] = (await find_one(GET_LEX, dumpscript[line + 9])).group(1)
															self["timer_prop"] = (await find_one(GET_PROPERTY, dumpscript[line + 10])).group(2)
															break

		for line, content in enumerate(dumpscript):
			if content.endswith("::_C"):
				if "initproperty" in dumpscript[line + 1]:
					if "getlocal_0" in dumpscript[line + 2]:
						self["timer_popup"] = (await find_one(INIT_PROPERTY, dumpscript[line + 1])).group(1)

						for x in range(line, 0, -1):
							if "getlex" in dumpscript[x]:
								if "getlocal_0" in dumpscript[x + 1]:
									if "setproperty" in dumpscript[x + 2]:
										self["timer_instance"] = (await find_one(SET_PROPERTY, dumpscript[x + 2])).group(1)
										break
						break

		return self