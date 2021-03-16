from .regex import CALL_PROPVOID, GET_PROPERTY, find_one
from typing import Dict, List

class ShamanObj(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "callpropvoid" in content:
				if "jump" in dumpscript[line + 1]:
					if "getlex" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "getproperty" in dumpscript[line + 4]:
								if "getproperty <q>[public]::length" in dumpscript[line + 5]:
									if "convert_i" in dumpscript[line + 6]:
										if "setlocal r5" in dumpscript[line + 7]:
											if "getlex" in dumpscript[line + 8]:
												self["shaman_obj_list"] = (await find_one(GET_PROPERTY, dumpscript[line + 4])).group(2)
												for x in range(line + 8, line + 50):
													if "getproperty" in dumpscript[x] \
 													and self["shaman_obj_list"] in dumpscript[x]:
														if "getlocal r6" in dumpscript[x + 1]:
															if "getproperty" in dumpscript[x + 2]:
																if "getproperty" in dumpscript[x + 3]:
																	if "callpropvoid" in dumpscript[x + 4]:
																		self["remove_shaman_obj"] = (await find_one(CALL_PROPVOID, content)).group(1)
																		self["shaman_obj_var"] = (await find_one(GET_PROPERTY, dumpscript[x + 3])).group(2)
																		break
												else:
													continue
												break
		return self