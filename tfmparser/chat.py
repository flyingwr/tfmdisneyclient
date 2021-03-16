from .regex import CALL_PROPVOID, CLASS, GET_LEX, GET_PROPERTY, find_one
from typing import Dict, List

class Chat(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if 'pushstring \"Navigateur : ' in content:
				if "getlocal_0" in dumpscript[line - 1]:
					if "callpropvoid" in dumpscript[line - 2]:
						self["chat_message"] = (await find_one(CALL_PROPVOID, dumpscript[line - 2])).group(1)
						break

		for line, content in enumerate(dumpscript):
			if "getlex <q>[public]::stage" in content:
				if "getlocal_0" in dumpscript[line + 1]:
					if "getproperty" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "setproperty <q>[public]::focus" in dumpscript[line + 4]:
								if "jump" in dumpscript[line + 5]:
									if "getlocal_0" in dumpscript[line + 6]:
										self["chat_container"] = (await find_one(GET_PROPERTY, dumpscript[line + 2])).group(2)
										self["chat_text_field"] = (await find_one(GET_PROPERTY, dumpscript[line + 3])).group(2)
										for x in range(line, 0, -1):
											if "class <q>[public]::" in dumpscript[x]:
												self["chat_class_name"] = (await find_one(CLASS, dumpscript[x])).group(1)

												for y in range(x, len(dumpscript)):
													if "getlex" in dumpscript[y] \
 													and self["chat_class_name"] in dumpscript[y]:
														if "getproperty" in dumpscript[y + 1]:
															if "getlocal_0" in dumpscript[y + 2]:
																if "getproperty" in dumpscript[y + 3]:
																	if "getlocal_0" in dumpscript[y + 4]:
																		self["chat_instance"] = (await find_one(GET_PROPERTY, dumpscript[y + 1])).group(2)
																		break

												for y in range(x, len(dumpscript)):
													if "getlocal_0" in dumpscript[y]:
														if "getlocal_0" in dumpscript[y + 1]:
															if "getproperty" in dumpscript[y + 2]:
																if "not" in dumpscript[y + 3]:
																	if "callpropvoid" in dumpscript[y + 4]:
																		if "returnvoid" in dumpscript[y + 5]:
																			self["chat_is_upper"] = (await find_one(GET_PROPERTY, dumpscript[y + 2])).group(2)
																			self["chat_shift"] = (await find_one(CALL_PROPVOID, dumpscript[y + 4])).group(1)
																			break

												for y in range(x, len(dumpscript)):
													if "getlocal_0" in dumpscript[y]:
														if "getproperty" in dumpscript[y + 1]:
															if "addEventListener, 2 params" in dumpscript[y + 2]:
																if "returnvoid" in dumpscript[y + 3]:
																	self["event_chat_text"] = (await find_one(GET_PROPERTY, dumpscript[y + 1])).group(2)
																	break
												break
										break

		for line, content in enumerate(dumpscript):
			if "setlocal r92" in content:
				if "getlex" in dumpscript[line + 1]:
					if "getproperty" in dumpscript[line + 2]:
						if "callproperty" in dumpscript[line + 3]:
							if "iffalse" in dumpscript[line + 4]:
								if "getlex" in dumpscript[line + 5]:
									for x in range(line + 5, line + 50):
										if "getlocal r91" in dumpscript[x]:
											if "callpropvoid" in dumpscript[x + 1]:
												self["chat_class_name2"] = (await find_one(GET_LEX, dumpscript[line + 5])).group(1)
												self["chat_message2"] = (await find_one(CALL_PROPVOID, dumpscript[x + 1])).group(1)
												break
									break

		return self