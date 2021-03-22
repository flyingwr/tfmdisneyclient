from .regex import CALL_PROPVOID, find_one
from typing import Dict, List

class SetV(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "ifne" in content:
				if "getlocal_0" in dumpscript[line + 1]:
					if "getlocal_1" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "getlex" in dumpscript[line + 4]:
								if "astypelate" in dumpscript[line + 5]:
									if "initproperty" in dumpscript[line + 6]:
										if "getlocal_0" in dumpscript[line + 7]:
											if "getproperty" in dumpscript[line + 8]:
												if "getlocal_0" in dumpscript[line + 9]:
													if "getproperty" in dumpscript[line + 10]:
														if "getproperty" in dumpscript[line + 11]:
															if "callpropvoid" in dumpscript[line + 12]:
																self["set_v"] = (await find_one(CALL_PROPVOID, dumpscript[line + 12])).group(1)
																break
		return self