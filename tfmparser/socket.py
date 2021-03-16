from .regex import CALL_PROPVOID, FIND_PROPSTRICT, GET_LEX, GET_PROPERTY, SET_PROPERTY, find_one
from typing import Dict, List

class Socket(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "callpropvoid <q>[public]::reset, 0 params" in content:
				if "getlocal_0" in dumpscript[line + 1]:
					if "getlex" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "initproperty" in dumpscript[line + 4]:
								if "getlex" in dumpscript[line + 5]:
									self["socket_class_name"] = (await find_one(GET_LEX, dumpscript[line + 5])).group(1)
									if "getlocal_0" in dumpscript[line + 6]:
										if "setproperty" in dumpscript[line + 7]:
											if "getlocal_0" in dumpscript[line + 8]:
												if "getscopeobject 1" in dumpscript[line + 9]:
													for x in range(line + 9, line + 15):
														if "getlex" in dumpscript[x] \
  														and self["socket_class_name"] in dumpscript[x]:
															if "getlocal_0" in dumpscript[x + 1]:
																if "setproperty" in dumpscript[x + 2]:
																	self["main_socket_instance"] = (await find_one(SET_PROPERTY, dumpscript[x + 2])).group(1)
																	self["bulle_socket_instance"] = (await find_one(SET_PROPERTY, dumpscript[line + 7])).group(1)
																	break
													else:
														continue
													break

		for line, content in enumerate(dumpscript):
			if "constructprop" in content:
				if "callpropvoid" in dumpscript[line + 1]:
					if "jump" in dumpscript[line + 2]:
						if "getlex" in dumpscript[line + 3]:
							if self["main_socket_instance"] in dumpscript[line + 4] \
  							and "getproperty" in dumpscript[line + 4]:
								if "findpropstrict" in dumpscript[line + 5]:
									if "getlocal_1" in dumpscript[line + 6]:
										if "constructprop" in dumpscript[line + 7]:
											if "callpropvoid" in dumpscript[line + 8]:
												if "returnvoid" in dumpscript[line + 9]:
													self["data_sender"] = (await find_one(CALL_PROPVOID, dumpscript[line + 8])).group(1)
													self["command_packet_name"] = (await find_one(FIND_PROPSTRICT, dumpscript[line + 5])).group(1)
													break

		for line, content in enumerate(dumpscript):
			if "pushscope" in content:
				if "getlocal_1" in dumpscript[line + 1]:
					if "callpropvoid" in dumpscript[line + 2]:
						if "getlex" in dumpscript[line + 3]:
							if "getproperty" in dumpscript[line + 4] \
  							and self["bulle_socket_instance"] in dumpscript[line + 4]:
								if "findpropstrict" in dumpscript[line + 5]:
									if "getlex" in dumpscript[line + 6]:
										self["crouch_packet_name"] = (await find_one(FIND_PROPSTRICT, dumpscript[line + 5])).group(1)

										for x in range(0, len(dumpscript)):
											if "getproperty" in dumpscript[x]:
												if "getproperty" in dumpscript[x + 1]:
													if "getproperty" in dumpscript[x + 2]:
														if "callpropvoid" in dumpscript[x + 3]:
															if "getlex" in dumpscript[x + 4]:
																if "getproperty" in dumpscript[x + 5] \
  																and self["bulle_socket_instance"] in dumpscript[x + 5]:
																	if "findpropstrict" in dumpscript[x + 6] \
  																	and self["crouch_packet_name"] in dumpscript[x + 6]:
																		self["crouch"] = (await find_one(CALL_PROPVOID, dumpscript[x + 3])).group(1)
																		self["static_side"] = (await find_one(GET_PROPERTY, dumpscript[x + 2])).group(2)
																		break
										else:
											continue
										break

		for line, content in enumerate(dumpscript):
			if "callpropvoid <q>[public]::addEventListener, 2 params" in content:
				if "getlocal_0" in dumpscript[line + 1]:
					if "getproperty" in dumpscript[line + 2]:
						if "getlex <q>[public]flash.events::ProgressEvent" in dumpscript[line + 3]:
							if "getproperty <q>[public]::SOCKET_DATA" in dumpscript[line + 4]:
								if "getlocal_0" in dumpscript[line + 5]:
									if "getproperty" in dumpscript[line + 6]:
										self["socket_name"] = (await find_one(GET_PROPERTY, dumpscript[line + 2])).group(2)
										self["event_socket_data"] = await find_one(GET_PROPERTY, dumpscript[line + 6])
										break

		if self["event_socket_data"] is not None:
			self["event_socket_data"] = self["event_socket_data"].group(2)

			for line, content in enumerate(dumpscript):
				if self["event_socket_data"] + "=(<q>[public]flash.events::ProgressEvent = null, <q>[public]::Boolean = false" in content:
					for x in range(line, len(dumpscript)):
						if "iffalse" in dumpscript[x]:
							if "getlocal_0" in dumpscript[x + 1]:
								if "dup" in dumpscript[x + 2]:
									if "setlocal r4" in dumpscript[x + 3]:
										if "getproperty" in dumpscript[x + 4]:
											if "increment_i" in dumpscript[x + 5]:
												self["data_id"] = (await find_one(GET_PROPERTY, dumpscript[x + 4])).group(2)
						elif "pushshort 255" in dumpscript[x]:
							if "bitand" in dumpscript[x + 1]:
								if "getproperty" in dumpscript[x + 5]:
									self["data_len"] = (await find_one(GET_PROPERTY, dumpscript[x + 5])).group(2)
						elif "initproperty" in dumpscript[x]:
							if "getlocal_0" in dumpscript[x + 1]:
								if "dup" in dumpscript[x + 2]:
									if "setlocal r4" in dumpscript[x + 3]:
										if "getproperty" in dumpscript[x + 4]:
											if "increment_i" in dumpscript[x + 5]:
												self["data_offset"] = (await find_one(GET_PROPERTY, dumpscript[x + 4])).group(2)
								elif "getproperty" in dumpscript[x + 2]:
									if "iftrue" in dumpscript[x + 3]:
										if "jump" in dumpscript[x + 4]:
											if "label" in dumpscript[x + 5]:
												self["read_data"] = (await find_one(GET_PROPERTY, dumpscript[x + 2])).group(2)
						elif "getlocal_0" in dumpscript[x]:
							if "getproperty" in dumpscript[x + 1]:
								if "callpropvoid <q>[public]::clear, 0 params" in dumpscript[x + 2]:
									self["socket_data"] = (await find_one(GET_PROPERTY, dumpscript[x + 1])).group(2)
									break
					break
		return self