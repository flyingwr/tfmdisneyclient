import re

CALL_PROPVOID = re.compile(r"callpropvoid <q>\[public\]::(.*?), (\d+) params$")
CALL_PROPERTY = re.compile(r"callproperty <q>\[(private|public)\](NULL|)::(.*?), \d+ params")
CLASS = re.compile(r"class <q>\[public\]::(.*?) extends .*?::(.*?)\{")
CONSTRUCTOR = re.compile(r"constructor \* <q>\[public\]::(.*?)=\(")
CONSTRUCT_PROP = re.compile(r"constructprop <q>\[public\]::(.*?), (\d+) params")
EXPORT = re.compile(r"(\s+)exports (\d+) as \"(.*?)_(.*?)\"")
FIND_PROPSTRICT = re.compile(r"findpropstrict <q>\[public\]::(.*?)$")
GET_LEX = re.compile(r"getlex <q>\[public\]::(.*?)$")
GET_PROPERTY = re.compile(r"getproperty (.*?)::(.*?)$")
INIT_PROPERTY = re.compile(r"initproperty <q>\[public\]::(.*?)$")
NEW_FUNCTION = re.compile(r'newfunction \[method (.*?) ]')
OBJECT = re.compile(r"<q>\[public\]::Object <q>\[private\]NULL::(.*?)=\(\)\(0 params, 0 optional\)")
PUBLIC_METHOD = re.compile(r"method <q>\[public\].*?<q>\[public\]::(.*?)=\(")
PUSH_NUM = re.compile(r"push(byte|short|int) (-?\d+)$")
PUSH_STRING = re.compile(r"findproperty <q>\[(private|public)\](NULL|)(.*?)\n(.*?)pushstring \"(.*?)\"")
SET_PROPERTY = re.compile(r"setproperty <q>\[public\]::(.*?)$")
SLOT = re.compile(r"slot (\d+):.*?<q>\[public\]::(.*?):<q>\[public\]")

PLAYER_CHEESE_REQ = re.compile(r"setlocal r(135|136)")
ANIM_CLASS_REQ = re.compile(r"setlocal r(5|7)")

async def find_one(patt, s):
	return patt.search(s)

def find_all(patt, s):
	r = re.compile(patt)
	result = r.findall(s)
	if len(result) > 0:
		return result
	return None