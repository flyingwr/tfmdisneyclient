from .regex import CALL_PROPVOID, FIND_PROPSTRICT, SET_PROPERTY, find_one
from typing import Dict, List

class Mass(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "findpropstrict" in content:
				if "constructprop" in dumpscript[line + 1]:
					if "coerce" in dumpscript[line + 2]:
						if "setlocal r21" in dumpscript[line + 3]:
							if "getlocal r21" in dumpscript[line + 4]:
								found = False

								for w in range(line + 4, line + 15):
									if "setproperty" in dumpscript[w]:
										if "getlocal r21" in dumpscript[w + 1]:
											if "findpropstrict" in dumpscript[w + 2]:
												for x in range(w + 2, w + 15):
													if "callproperty" in dumpscript[x]:
														for y in range(x, x + 15):
															if "constructprop" in dumpscript[y]:
																if "setproperty" in dumpscript[y + 1]:
																	if "getlocal r21" in dumpscript[y + 2]:
																		for z in range(y + 2, y + 15):
																			if "setproperty" in dumpscript[z]:
																				if "getlocal r20" in dumpscript[z + 1]:
																					if "getlocal r21" in dumpscript[z + 2]:
																						if "callpropvoid" in dumpscript[z + 3]:
																							self["b2massdata"] = (await find_one(FIND_PROPSTRICT, content)).group(1)
																							self["mass"] = (await find_one(SET_PROPERTY, dumpscript[w])).group(1)
																							self["center"] = (await find_one(SET_PROPERTY, dumpscript[y + 1])).group(1)
																							self["I"] = (await find_one(SET_PROPERTY, dumpscript[z])).group(1)
																							self["set_mass"] = (await find_one(CALL_PROPVOID, dumpscript[z + 3])).group(1)
																							found = True
																							break

								if found:
									break
		return self