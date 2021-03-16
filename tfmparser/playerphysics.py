from .regex import CALL_PROPVOID, FIND_PROPSTRICT, GET_PROPERTY, SET_PROPERTY, find_one
from typing import Dict, List

class PlayerPhysics(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		_last_line, last_line = 0, 0

		for line, content in enumerate(dumpscript):
			if "not" in content:
				if "iffalse" in dumpscript[line + 1]:
					if "getlocal_2" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "convert_b" in dumpscript[line + 4]:
								if "setlocal r17" in dumpscript[line + 5]:
									if "getlocal_2" in dumpscript[line + 6]:
										if "getproperty" in dumpscript[line + 7]:
											if "convert_b" in dumpscript[line + 8]:
												if "setlocal r18" in dumpscript[line + 9]:
													self["player_moving_right"] = (await find_one(GET_PROPERTY, dumpscript[line + 3])).group(2)
													self["player_moving_left"] = (await find_one(GET_PROPERTY, dumpscript[line + 7])).group(2)

													last_line = line + 15
													break

		if last_line:
			for x in range(last_line, len(dumpscript)):
				if "getlocal_2" in dumpscript[x]:
					if "getproperty" in dumpscript[x + 1]:
						if "coerce" in dumpscript[x + 2]:
							if "setlocal r7" in dumpscript[x + 3]:
								self["player_physics"] = (await find_one(GET_PROPERTY, dumpscript[x + 1])).group(2)

								for y in range(x, len(dumpscript)):
									if "getlex" in dumpscript[y]:
										if "getlocal r7" in dumpscript[y + 1]:
											if "getproperty" in dumpscript[y + 2]:
												self["x_form"] = (await find_one(GET_PROPERTY, dumpscript[y + 2])).group(2)
									elif "findpropstrict" in dumpscript[y]:
										self["b2vec2"] = (await find_one(FIND_PROPSTRICT, dumpscript[y])  ).group(1)
									elif "convert_d" in dumpscript[y]:
										if "setlocal r9" in dumpscript[y + 1]:
											if "getlocal r7" in dumpscript[y + 2]:
												if "getproperty" in dumpscript[y + 3]:
													if "getlocal" in dumpscript[y + 4]:
														if "setproperty" in dumpscript[y + 5]:
															self["physics_state"] = (await find_one(GET_PROPERTY, dumpscript[y + 3])).group(2)
															self["physics_state_vx"] = (await find_one(SET_PROPERTY, dumpscript[y + 5])).group(1)

															for z in range(y + 5, (y + 5) + 5):
																if "getproperty" in dumpscript[z] \
 																and self["physics_state"] in dumpscript[z]:
																	if "getlocal" in dumpscript[z + 1]:
																		if "setproperty" in dumpscript[z + 2]:
																			self["physics_state_vy"] = (await find_one(SET_PROPERTY, dumpscript[z + 2])).group(1)

																			for w in range(z + 2, z + 50):
																				if "pushtrue" in dumpscript[w]:
																					if "getlocal r16" in dumpscript[w + 1]:
																						if "getproperty" in dumpscript[w + 2]:
																							if "callpropvoid" in dumpscript[w + 3]:
																								self["jump"] = (await find_one(CALL_PROPVOID, dumpscript[w + 3])).group(1)

																								_last_line = w + 3
																								break
																			break
															break
								break

			for x in range(_last_line, len(dumpscript)):
				if "pushtrue" in dumpscript[x]:
					if "callpropvoid" in dumpscript[x + 1]:
						if "getlocal_2" in dumpscript[x + 2]:
							if "getlex" in dumpscript[x + 3]:
								if "getproperty" in dumpscript[x + 4]:
									if "setproperty" in dumpscript[x + 5]:
										if "getlex" in dumpscript[x + 6]:
											if "getproperty" in dumpscript[x + 7]:
												if "convert_b" in dumpscript[x + 8]:
													self["animation_course"] = (await find_one(CALL_PROPVOID, dumpscript[x + 1])).group(1)
													self["is_down"] = (await find_one(SET_PROPERTY, dumpscript[x + 5])).group(1)

													_last_line = x + 8
													break
			
			for x in range(_last_line, len(dumpscript)):
				if "getlocal r17" in dumpscript[x]:
					if "convert_b" in dumpscript[x + 1]:
						if "dup" in dumpscript[x + 2]:
							if "iftrue" in dumpscript[x + 3]:
								if "pop" in dumpscript[x + 4]:
									if "getlocal r18" in dumpscript[x + 5]:
										if "convert_b" in dumpscript[x + 6]:
											if "iffalse" in dumpscript[x + 7]:
												if "callpropvoid" in dumpscript[x + 10]:
													self["static_animation"] = (await find_one(CALL_PROPVOID, dumpscript[x + 10])).group(1)
													break
		return self