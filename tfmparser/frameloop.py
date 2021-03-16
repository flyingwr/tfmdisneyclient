from .regex import GET_LEX, GET_PROPERTY, find_one
from typing import Dict, List

class FrameLoop(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "pop" in content:
				if "getlocal r6" in dumpscript[line + 1]:
					if "getlex" in dumpscript[line + 2]:
						if "getproperty" in dumpscript[line + 3]:
							if "subtract" in dumpscript[line + 4]:
								for x in range(line + 4, line + 20):
									if "greaterthan" in dumpscript[x]:
										if "iffalse" in dumpscript[x + 1]:
											self["frame_loop_class_name"] = (await find_one(GET_LEX, dumpscript[line + 2])).group(1)
											if "getlex" in dumpscript[x + 2] \
  											and self["frame_loop_class_name"] in dumpscript[x + 2]:
												if "getlocal r6" in dumpscript[x + 3]:
													if "setproperty" in dumpscript[x + 4]:
														if "getlocal r5" in dumpscript[x + 5]:
															self["victory_time"] = (await find_one(GET_PROPERTY, dumpscript[line + 3])).group(2)
															break
								else:
									continue
								break
		return self