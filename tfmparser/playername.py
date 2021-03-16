from .regex import INIT_PROPERTY, find_one
from typing import Dict, List

class PlayerName(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "returnvoid" in content:
				if "getlocal_0" in dumpscript[line + 1]:
					if "getlocal_1" in dumpscript[line + 2]:
						if "callproperty <q>[public]::readUTF, 0 params" in dumpscript[line + 3]:
							if "initproperty" in dumpscript[line + 4]:
								if "getlocal_0" in dumpscript[line + 5]:
									if "getlocal_1" in dumpscript[line + 6]:
										if "callproperty <q>[public]::readInt, 0 params" in dumpscript[line + 7]:
											if "initproperty" in dumpscript[line + 8]:
												if "getlocal_0" in dumpscript[line + 9]:
													self["player_name"] = (await find_one(INIT_PROPERTY, dumpscript[line + 4])).group(1)
													break

		for line, content in enumerate(dumpscript):
			if "getlocal_1" in content:
				if "callproperty <q>[public]::readInt, 0 params" in dumpscript[line + 1]:
					if "initproperty" in dumpscript[line + 2]:
						if "getlocal_0" in dumpscript[line + 3]:
							if "getlocal_1" in dumpscript[line + 4]:
								if "callproperty <q>[public]::readInt, 0 params" in dumpscript[line + 5]:
									if "initproperty" in dumpscript[line + 6]:
										if "getlocal_0" in dumpscript[line + 7]:
											if "getlocal_1" in dumpscript[line + 8]:
												if "callproperty <q>[public]::readInt, 0 params" in dumpscript[line + 9]:
													if "initproperty" in dumpscript[line + 10]:
														if "returnvoid" in dumpscript[line + 11]:
															self["player_name_color"] = (await find_one(INIT_PROPERTY, dumpscript[line + 6])).group(1)
															break

		return self