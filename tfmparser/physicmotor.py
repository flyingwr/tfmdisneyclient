from .regex import CALL_PROPVOID, CLASS, FIND_PROPSTRICT, PUBLIC_METHOD, SET_PROPERTY, find_one
from typing import Dict, List

class PhysicMotor(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "<q>[public]::int, <q>[public]::Number = 1, <q>[public]::Boolean = true)(4 params, 2 optional)" in content:
				self["change_player_physic"] = (await find_one(PUBLIC_METHOD, content)).group(1)
				for x in range(line, 0, -1):
					if "class" in dumpscript[x]:
						self["physic_motor_class_name"] = (await find_one(CLASS, dumpscript[x])).group(1)
						break
				for x in range(line, len(dumpscript)):
					if "jump" in dumpscript[x]:
						if "getlocal r9" in dumpscript[x + 1]:
							if "setproperty" in dumpscript[x + 4]:
								if "findpropstrict" in dumpscript[x + 5]:
									self["b2circledef_class_name"] = (await find_one(FIND_PROPSTRICT, dumpscript[x + 5])).group(1)
									if "setlocal r11" in dumpscript[x + 8]:
										if "getlocal r11" in dumpscript[x + 9]:
											last_line = 0
											for y in range(x + 9, x + 25):
												if "multiply" in dumpscript[y]:
													if "setproperty" in dumpscript[y + 1]:
														self["radius"] = (await find_one(SET_PROPERTY, dumpscript[y + 1])).group(1)
														last_line = y + 2
														break
											if "getlocal r11" in dumpscript[last_line]:
												for y in range(last_line, last_line + 10):
													if "setproperty" in dumpscript[y]:
														self["density"] = (await find_one(SET_PROPERTY, dumpscript[y])).group(1)
														last_line = y + 1
														break
												if "getlocal_1" in dumpscript[last_line]:
													if "getproperty" in dumpscript[last_line + 1]:
														if "iffalse" in dumpscript[last_line + 2]:
															if "getlocal r11" in dumpscript[last_line + 3]:
																found_friction = False
																for y in range(last_line + 3, last_line + 25):
																	if "setproperty" in dumpscript[y]:
																		if not found_friction:
																			self["friction"] = (
																				await find_one(SET_PROPERTY, dumpscript[y])
																			).group(1)
																			found_friction = True
																		elif self["friction"] in dumpscript[y]:
																			continue
																		else:
																			self["restitution"] = (
																				await find_one(SET_PROPERTY, dumpscript[y])
																			).group(1)
																			for z in range(y, y + 50):
																				if "getlocal r12" in dumpscript[z]:
																					if "getlocal r10" in dumpscript[z + 1]:
																						if "callpropvoid" in dumpscript[z + 2]:
																							self["change_player_physic2"] = (
																								await find_one(CALL_PROPVOID, dumpscript[z + 2])
																							).group(1)
																							break
																			break
					elif "returnvoid" in dumpscript[x]:
						break
				break
		return self