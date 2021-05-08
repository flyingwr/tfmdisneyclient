from .regex import CALL_PROPERTY, CALL_PROPVOID, CLASS, CONSTRUCTOR, CONSTRUCT_PROP, FIND_PROPSTRICT, \
	GET_LEX, GET_PROPERTY, INIT_PROPERTY, PUBLIC_METHOD, SET_PROPERTY, SLOT, find_one
from typing import Dict, List

class UiElement(dict):
	def __missing__(self, key) -> str:
		return ""

	async def fetch(self, dumpscript: List) -> Dict[str, str]:
		for line, content in enumerate(dumpscript):
			if "constructor" in content and "=(<q>[public]::int = 0, <q>[public]::int = 0)(2 params, 2 optional)" in content:
				for x in range(line, len(dumpscript)):
					if "return" in dumpscript[x]:
						if "addChild, 1 params" in dumpscript[x - 1]:
							self["ui_element_class_name"] = (await find_one(CONSTRUCTOR, content)).group(1)

							found = 0
							for y in range(x, len(dumpscript)):
								if "<q>[public]__AS3__.vec::Vector" in dumpscript[y] \
								and "=(<q>[public]::Boolean = false)(1 params, 1 optional)" in dumpscript[y]:
									self["reset_ui"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
									found += 1
								elif "=(<q>[public]::String, <q>[public]::Function = null, <q>[public]::int = 10" in dumpscript[y]:
									self["set_box"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
									found += 1
								elif "override" in dumpscript[y] and "=(<q>[public]::Boolean = true)" in dumpscript[y]:
									if "need_rest" in dumpscript[y + 1]:
										self["set_draggable"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
										found += 1
								elif "method <q>[public]flash.display::Shape" in dumpscript[y]:
									self["set_shape"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
									found += 1
								elif "(<q>[public]::Boolean, <q>[public]::int = 60, <q>[public]::Boolean = false)" in dumpscript[y]:
									self["set_scrollable"] = (await find_one(PUBLIC_METHOD, dumpscript[y])).group(1)
									found += 1
								if found >= 5:
									break

							for x in range(len(dumpscript)):
								if f"{self['ui_element_class_name']})(4 params, 0 optional)" in dumpscript[x]:
									for y in range(x, x + 65):
										if "constructprop" in dumpscript[y]:
											self["ui_sprite2_class_name"] = (await find_one(CONSTRUCT_PROP, dumpscript[y])).group(1)
											for z in range(len(dumpscript)):
												if "class" in dumpscript[z] and self["ui_sprite2_class_name"] in dumpscript[z]:
													self["ui_sprite_class_name"] = (await find_one(CLASS, dumpscript[z])).group(2)
													break
										elif "setlocal r7" in dumpscript[y] and "getlocal r7" in dumpscript[y + 1]:
											if "getlocal_3" in dumpscript[y + 2] and "callpropvoid" in dumpscript[y + 3]:
												self["on_mouse_click"] = (await find_one(CALL_PROPVOID, dumpscript[y + 3])).group(1)
										elif "getlex" in dumpscript[y] and "getlocal r7" in dumpscript[y + 1]:
											self["ui_manager_class_name"] = (await find_one(GET_LEX, dumpscript[y])).group(1)
											for z in range(y, y + 10):
												if "callpropvoid" in dumpscript[z]:
													self["on_mouse_box"] = (await find_one(CALL_PROPVOID, dumpscript[z])).group(1)
													break
										elif "iffalse" in dumpscript[y]:
											if "getlocal r7" in dumpscript[y + 2] and "callpropvoid" in dumpscript[y + 3]:
												self["add_ui_element"] = (await find_one(CALL_PROPVOID, dumpscript[y + 3])).group(1)
												break
									for y in range(x, 0, -1):
										if "class" in dumpscript[y]:
											for z in range(y, len(dumpscript)):
												if "(<q>[public]::Boolean, <q>[public]::int)" in dumpscript[z]:
													for i in range(z, z + 50):
														if "findpropstrict" in dumpscript[i] and "Sprite" not in dumpscript[i]:
															findpropstrict = await find_one(FIND_PROPSTRICT, dumpscript[i])
															self["ui_button_class_name"] = findpropstrict.group(1)
															for j in range(len(dumpscript)):
																if f"method <q>[public]::{self['ui_button_class_name']}" in dumpscript[j] \
																and "=(<q>[public]::Boolean)(1 params, 0 optional)" in dumpscript[j]:
																	for k in range(j, j + 25):
																		if "initproperty" in dumpscript[k]:
																			self["button_state"] = (
																				await find_one(INIT_PROPERTY, dumpscript[k])).group(1)
																		elif "mouseEnabled" in dumpscript[k]:
																			self["set_button_state"] = (
																				await find_one(PUBLIC_METHOD, dumpscript[j])).group(1)
																			break
																	else:
																		continue
																	break
															break
													break
											break
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
												for i in range(len(dumpscript)):
													if "class" in dumpscript[i] and self["prep_ui_class_name"] in dumpscript[i]:
														for j in range(i, i + 100):
															if "slot" in dumpscript[j]:
																slot = (await find_one(SLOT, dumpscript[j]))
																self[f"prep_ui{slot.group(1)}_instance"] = slot.group(2)
																if slot.group(1) == "7":
																	break
														break
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
		for line, content in enumerate(dumpscript):
			if "<q>[public]::int = 1, <q>[public]::Boolean = false)(3 params, 2 optional)" in content:
				self["add_ui"] = (await find_one(PUBLIC_METHOD, dumpscript[line])).group(1)
				for x in range(line, 0, -1):
					if "class" in dumpscript[x]:
						self["main_ui_class_name"] = (await find_one(CLASS, dumpscript[x])).group(1)
						break
				break
		for line, content in enumerate(dumpscript):
			if 'pushstring "$interface.tribu.bouton.membresConnectes' in content:
				setproperty = (await find_one(SET_PROPERTY, dumpscript[line + 1])).group(1)
				for x in range(len(dumpscript)):
					if f"getproperty <q>[public]::{setproperty}" in dumpscript[x]:
						for y in range(x, x - 8, -1):
							if "findpropstrict" in dumpscript[y]:
								self["ui_check_box_class_name"] = (await find_one(FIND_PROPSTRICT, dumpscript[y])).group(1)
						for y in range(x, x + 100):
							if "3 params" in dumpscript[y]:
								self["check_box_callback"] = (await find_one(CALL_PROPVOID, dumpscript[y])).group(1)
								break
						break
		for line, content in enumerate(dumpscript):
			if 'pushstring "$Loupe' in content:
				setproperty = (await find_one(SET_PROPERTY, dumpscript[line + 1])).group(1)
				for x in range(len(dumpscript)):
					if f"getproperty <q>[public]::{setproperty}" in dumpscript[x]:
						_found = False
						for y in range(x, x - 8, -1):
							if "constructprop" in dumpscript[y]:
								self["ui_input_class_name"] = (await find_one(CONSTRUCT_PROP, dumpscript[y])).group(1)
								for z in range(x, x + 35):
									if "setproperty <q>[public]::maxChars" in dumpscript[z]:
										for i in range(z, z - 10, -1):
											if "getlocal_0" in dumpscript[i]:
												self["text_field"] = (await find_one(GET_PROPERTY, dumpscript[i + 2])).group(2)
											elif "callpropvoid" in dumpscript[i]:
												self["set_display_text"] = (await find_one(CALL_PROPVOID, dumpscript[i])).group(1)
												_found = True
												break
										break
								break
						if _found:
							break
		for line, content in enumerate(dumpscript):
			if "constructor" in content and "(<q>[public]::Function = null, <q>[public]::Object = null)" in content:
				self["ui_check_button_class_name"] = (await find_one(CONSTRUCTOR, content)).group(1)
				for x in range(line, len(dumpscript)):
					if "slot 0: var" in dumpscript[x]:
						if "flash.text::TextField" in dumpscript[x]:
							self["text_field2"] = (await find_one(SLOT, dumpscript[x])).group(2)
						elif "Boolean = false" in dumpscript[x]:
							self["is_selected"] = (await find_one(SLOT, dumpscript[x])).group(2)
					elif "=(<q>[public]flash.events::Event)(1 params, 0 optional)" in dumpscript[x]:
						self["check_button_exec"] = (await find_one(PUBLIC_METHOD, dumpscript[x])).group(1)
						break
				break
		for line, content in enumerate(dumpscript):
			if 'pushstring "$ModeDeJeu' in content:
				setproperty = (await find_one(SET_PROPERTY, dumpscript[line + 1])).group(1)
				for x in range(len(dumpscript)):
					if f"getproperty <q>[public]::{setproperty}" in dumpscript[x]:
						for y in range(x, x + 12):
							if "initproperty" in dumpscript[y] and "callproperty" in dumpscript[y - 1]:
								callproperty = (await find_one(CALL_PROPERTY, dumpscript[y - 1])).group(3)

								_found = 0
								for z in range(len(dumpscript)):
									if f"{callproperty}=(" in dumpscript[z]:
										for i in range(z, z + 50):
											if "returnvalue" in dumpscript[i] or _found > 1:
												for j in range(len(dumpscript)):
													if f"method <q>[public]::{self['ui_items_list_class_name']}" in dumpscript[j] \
													and "(<q>[public]::int)(1 params, 0 optional)" in dumpscript[j]:
														self["select_item"] = (
															await find_one(PUBLIC_METHOD, dumpscript[j])).group(1)
														break
												break
											if "findpropstrict" in dumpscript[i]:
												self[f"{'ui_text_field_class_name' if _found < 1 else 'ui_items_list_class_name'}"] = (
													await find_one(FIND_PROPSTRICT, dumpscript[i])).group(1)
												_found += 1
										break
							elif 'pushstring "Transformice"' in dumpscript[y] and "newfunction" in dumpscript[y + 1]:
								if "callpropvoid" in dumpscript[y + 4]:
									self["add_to_list"] = (await find_one(CALL_PROPVOID, dumpscript[y + 4])).group(1)
									break
						break		
				break		
		return self
