from .regex import CALL_PROPVOID, GET_LEX, find_one
from typing import Dict, List

class PacketHandler(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "readBytes, 3 params" in content:
				if "getlex" in dumpscript[line + 1]:
					if "getlocal_0" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "callpropvoid" in dumpscript[line + 4]:
								self["packet_handler_class_name"] = (await find_one(GET_LEX, dumpscript[line + 1])).group(1)
								self["packet_handler"] = (await find_one(CALL_PROPVOID, dumpscript[line + 4])).group(1)
								break
		return self