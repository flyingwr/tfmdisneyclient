from .regex import CALL_PROPVOID, CLASS, CONSTRUCTOR, GET_LEX, GET_PROPERTY, PUBLIC_METHOD, find_one
from typing import Dict, List

class UiElement(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "=(<q>[public]::int = 0, <q>[public]::int = 0)(2 params, 2 optional)" in content:
				for x in range(line, len(dumpscript)):
					if "return" in dumpscript[x]:
						if "addChild, 1 params" in dumpscript[x - 1]:
							self["ui_element_class_name"] = (await find_one(CONSTRUCTOR, content)).group(1)

							found = 0
							for y in range(x, len(dumpscript)):
								if "=(<q>[public]::String, <q>[public]::Function = null, <q>[public]::int = 10" in dumpscript[y]:
									if found == 0:
										self["set_box"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
										found = 1
								elif "override" in dumpscript[y] and "=(<q>[public]::Boolean = true)" in dumpscript[y]:
									if "need_rest" in dumpscript[y + 1]:
										if found == 1:
											self["set_draggable"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
											break
							break
				else:
					continue
				break

		for line, content in enumerate(dumpscript):
			if "=(<q>[public]::String, <q>[public]::String)(2 params, 0 optional)" in content:
				for x in range(line, line + 20):
					if "findpropstrict" in dumpscript[x] and self["ui_element_class_name"] in dumpscript[x]:
						for y in range(x, x + 50):
							if "callpropvoid" in dumpscript[y] and "2 params" in dumpscript[y]:
								self["set_prep_ui"] = (await find_one(CALL_PROPVOID, dumpscript[y])).group(1)
								for z in range(y, 0, -1):
									if "getlocal_0" in dumpscript[z]:
										if "getlex" in dumpscript[z + 2]:
											if "getproperty" in dumpscript[z + 3]:
												self["prep_ui_class_name"] = (await find_one(GET_LEX, dumpscript[z + 2])).group(1)
												self["prep_ui_instance"] = (await find_one(GET_PROPERTY, dumpscript[z + 3])).group(2)
												break
								break
						break
				else:
					continue
				break

		for line, content in enumerate(dumpscript):
			if "method <q>[public]flash.display::MovieClip" in content \
			and "(<q>[public]::String, <q>[public]::Boolean = false)(2 params, 1 optional)" in content:
				self["get_definition"] = (await find_one(PUBLIC_METHOD, dumpscript[line])).group(1)
				for x in range(line, 0, -1):
					if "class" in dumpscript[x]:
						self["domain_manager_class_name"] = (await find_one(CLASS, dumpscript[x])).group(1)
						for y in range(x, len(dumpscript)):
							if "flash.display::Bitmap" in dumpscript[y] \
							and "http://www.transformice.com/images/)(2 params, 1 optional)" in dumpscript[y] \
							and "recupImageDistante" not in dumpscript[y]:
								self["load_img"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
								break
						break
				break
		return self