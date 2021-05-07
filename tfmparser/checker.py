from .regex import GET_LEX, GET_PROPERTY, PUBLIC_METHOD, SET_PROPERTY, SLOT, find_one
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
												for y in range(len(dumpscript)):
													if f'class <q>[public]::{getlex}' in dumpscript[y]:
														found = 0
														for z in range(y, len(dumpscript)):
															if "slot" in dumpscript[z] and "Timer" in dumpscript[z]:
																slot = await find_one(SLOT, dumpscript[z])
																if slot is not None:
																	self["check_timer"] = slot.group(2)
																	found += 1
															elif "constructprop <q>[public]::Date" in dumpscript[z]:
																for i in range(z, z + 15):
																	if "returnvoid" in dumpscript[i] \
																	and "setproperty" in dumpscript[i - 1] \
																	and "subtract" in dumpscript[i - 2]:
																		self["check_timestamp"] = (
																			await find_one(SET_PROPERTY, dumpscript[i - 1])).group(1)
																		found += 1
																		break
															elif "(<q>[public]::int)" in dumpscript[z]:
																for i in range(z, z + 20):
																	if "setproperty" in dumpscript[i]:
																		self["check_id"] = (
																			await find_one(SET_PROPERTY, dumpscript[i])).group(1)
																		found += 1
																		break
															if found >= 3:
																break
														break
												break
										else:
											continue
										break
		return self