from .regex import GET_LEX, GET_PROPERTY, SET_PROPERTY, find_one
from typing import Dict, List

class MouseInfo(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "getlocal_2" in content:
				if "getproperty" in dumpscript[line + 1]:
					if "iffalse" in dumpscript[line + 2]:
						if "getlex" in dumpscript[line + 3]:
							if "getproperty" in dumpscript[line + 4]:
								if "getlocal_1" in dumpscript[line + 5]:
									if "callproperty <q>[public]::readUnsignedByte, 0 params" in dumpscript[line + 6]:
										for x in range(line + 5, line + 12):
											if "divide" in dumpscript[x]:
												if "setproperty" in dumpscript[x + 1]:
													self["mouse_info_class_name"] = (
														await find_one(GET_LEX, dumpscript[line + 3])
													).group(1)
													self["mouse_info_instance"] = (
														await find_one(GET_PROPERTY, dumpscript[line + 4])
													).group(2)
													self["jump_height"] = (
														await find_one(SET_PROPERTY, dumpscript[x + 1])
													).group(1)
													break
										else:
											continue
										break
		return self