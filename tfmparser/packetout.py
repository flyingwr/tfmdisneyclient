from .regex import CONSTRUCTOR, INIT_PROPERTY, SLOT, find_one
from typing import Dict, List

class PacketOut(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "(<q>[public]::int, <q>[public]::int = -1)" in content:
				if "getlocal_0" in dumpscript[line + 5]:
					if "constructsuper" in dumpscript[line + 6]:
						if "findpropstrict <q>[public]flash.utils::ByteArray" in dumpscript[line + 8]:
							if "initproperty" in dumpscript[line + 10]:
								self["packet_out_name"] = (await find_one(CONSTRUCTOR, content)).group(1)
								self["packet_out_bytes"] = (await find_one(INIT_PROPERTY, dumpscript[line + 10])).group(1)

								for x in range(line, line + 50):
									if "slot" in dumpscript[x] and ":<q>[public]::Boolean = false" in dumpscript[x]:
										self["cipher"] = (await find_one(SLOT, dumpscript[x])).group(1)
										break
								else:
									continue
								break
		return self