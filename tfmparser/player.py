from .regex import GET_PROPERTY, SET_PROPERTY, find_one
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
		for line, content in enumerate(dumpscript):
			if 'pushstring "AnimAttaque' in content:
				setproperty = (await find_one(SET_PROPERTY, dumpscript[line + 1])).group(1)
				for x in range(len(dumpscript)):
					if f"getproperty <q>[public]::{setproperty}" in dumpscript[x]:
						for y in range(x, x + 60):
							if "scaleX" in dumpscript[y]:
								for z in range(y, 0, -1):
									if "getlocal_0" in dumpscript[z] and "getproperty" in dumpscript[z + 1]:
										self["player_bitmap"] = (await find_one(GET_PROPERTY, dumpscript[z + 1])).group(2)
										for i in range(len(dumpscript)):
											if f"getproperty <q>[public]::{self['player_bitmap']}" in dumpscript[i]:
												if "visible" in dumpscript[i + 3]:
													for j in range(i + 3, i + 18):
														if "getslot" in dumpscript[j] and "addChild" in dumpscript[j + 1]:
															for k in range(j, 0, -1):
																if "setproperty" in dumpscript[k]:
																	self["has_image"] = (
																		await find_one(SET_PROPERTY, dumpscript[k])).group(1)
																	break
															break
													else:
														continue
													break
										break
								break
						break
				break
		return self