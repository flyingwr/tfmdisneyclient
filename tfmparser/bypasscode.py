from .regex import INIT_PROPERTY, find_one
from typing import Dict, List

class BypassCode(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		found = 0
		for line, content in enumerate(dumpscript):
			if "loaderInfo" in content:
				if "bytes" in dumpscript[line + 1] and "stage" in dumpscript[line - 1]:
					if "length" in dumpscript[line + 2]:
						self["bypass_code"] = (await find_one(INIT_PROPERTY, dumpscript[line + 3])).group(1)
						found += 1
				elif "loaderURL" in dumpscript[line + 1] and "initproperty" in dumpscript[line + 2]:
					self["loader_url"] = (await find_one(INIT_PROPERTY, dumpscript[line + 2])).group(1)
					found += 1
			if found >= 2:
				break
		return self