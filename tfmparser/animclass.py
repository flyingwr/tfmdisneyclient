from .regex import ANIM_CLASS_REQ, CLASS, PUBLIC_METHOD, find_one
from typing import Dict, List

class AnimClass(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		found = 0

		for line, content in enumerate(dumpscript):
			if "pushscope" in content:
				if "pushnan" in dumpscript[line + 1]:
					if "setlocal r" in dumpscript[line + 2]:
						setlocal = (await find_one(ANIM_CLASS_REQ, dumpscript[line + 2]))
						if setlocal is not None:
							n = setlocal.group(1)
							if n == "5":
								if "pushnan" in dumpscript[line + 3]:
									if "setlocal r8" in dumpscript[line + 4]:
										if "pushnull" in dumpscript[line + 5]:
											if "coerce" in dumpscript[line + 6]:
												if "setlocal r9" in dumpscript[line + 7]:
													if "getlocal_1" in dumpscript[line + 8]:
														self["update_coord"] = (await find_one(PUBLIC_METHOD, dumpscript[line - 4])).group(1)
														for x in range(line, 0, -1):
															if "class" in dumpscript[x]:
																self["anim_class_name"] = (await find_one(CLASS, dumpscript[x])).group(1)
																found += 1
																break
							elif n == "7":
								if "pushnull" in dumpscript[line + 3]:
									if "coerce" in dumpscript[line + 4]:
										if "setlocal r8" in dumpscript[line + 5]:
											if "getlocal_1" in dumpscript[line + 6]:
												self["update_coord2"] = (await find_one(PUBLIC_METHOD, dumpscript[line  - 4])).group(1)
												found += 1
			if found == 2:
				break
			
		return self