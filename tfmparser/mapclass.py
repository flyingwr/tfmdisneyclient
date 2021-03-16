from .regex import GET_LEX, GET_PROPERTY, find_one
from typing import Dict, List

class Map(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "getlocal_0" in content:
				if "pushscope" in dumpscript[line + 1]:
					if "pushbyte 0" in dumpscript[line + 2]:
						if "setlocal r5" in dumpscript[line + 3]:
							if "pushbyte 0" in dumpscript[line + 4]:
								if "setlocal r6" in dumpscript[line + 5]:
									for x in range(line + 5, line + 50):
										if "getlex" in dumpscript[x]:
											if "getproperty" in dumpscript[x + 1]:
												getlex = await find_one(GET_LEX, dumpscript[x])
												if getlex is not None:
													self["map_class_name"] = getlex.group(1)
													self["map_instance"] = (await find_one(GET_PROPERTY, dumpscript[x + 1])).group(2)
										elif "getproperty" in dumpscript[x]:
											if "getproperty" in dumpscript[x + 1]:
												if "coerce <q>[public]__AS3__.vec::Vector" in dumpscript[x + 2]:
													self["obj_container"] = (await find_one(GET_PROPERTY, dumpscript[x])).group(2)
													self["hole_list"] = (await find_one(GET_PROPERTY, dumpscript[x + 1])).group(2)
													break
									else:
										continue
									break

		for line, content in enumerate(dumpscript):
			if "getlocal r8" in content:
				if "getlex" in dumpscript[line + 1]:
					if "getproperty" in dumpscript[line + 2]:
						if "setproperty <q>[public]::cacheAsBitmap" in dumpscript[line + 3]:
							if "getlocal_0" in dumpscript[line + 4]:
								if "getproperty" in dumpscript[line + 5]:
									if "iftrue" in dumpscript[line + 6]:
										if "getlocal_0" in dumpscript[line + 7]:
											self["clip_fromage"] = (await find_one(GET_PROPERTY, dumpscript[line + 5])).group(2)
											break
		return self