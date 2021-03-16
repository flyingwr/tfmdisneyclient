from .regex import INIT_PROPERTY, find_one
from typing import Dict, List

class BypassCode(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "stage" in content:
				if "loaderInfo" in dumpscript[line + 1]:
					if "bytes" in dumpscript[line + 2]:
						if "length" in dumpscript[line + 3]:
							self["bypass_code"] = (await find_one(INIT_PROPERTY, dumpscript[line + 4])).group(1)
							break
		return self