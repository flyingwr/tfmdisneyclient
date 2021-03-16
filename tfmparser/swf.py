from .stream import Stream
from .regex import *

from io import BytesIO
from shutil import copyfile
from struct import unpack
from zlib import decompress

import aiofiles

as_tags = {
	0: "End",
	1: "ShowFrame",
	2: "DefineShape",
	4: "PlaceObject",
	5: "RemoveObject",
	6: "DefineBits",
	7: "DefineButton",
	8: "JPEGTables",
	9: "SetBackgroundColor",
	10: "DefineFont",
	11: "DefineText",
	12: "DoAction",
	13: "DefineFontInfo",
	14: "DefineSound",
	15: "StartSound",
	17: "DefineButtonSound",
	18: "SoundStreamHead",
	19: "SoundStreamBlock",
	20: "DefineBitsLossless",
	21: "DefineBitsJPEG2",
	22: "DefineShape2",
	23: "DefineButtonCxform",
	24: "Protect",
	26: "PlaceObject2",
	28: "RemoveObject2",
	32: "DefineShape3",
	33: "DefineText2",
	34: "DefineButton2",
	35: "DefineBitsJPEG3",
	36: "DefineBitsLossless2",
	37: "DefineEditText",
	39: "DefineSprite",
	43: "FrameLabel",
	45: "SoundStreamHead2",
	46: "DefineMorphShape",
	48: "DefineFont2",
	56: "ExportAssets",
	57: "ImportAssets",
	58: "EnableDebugger",
	59: "DoInitAction",
	60: "DefineVideoStream",
	61: "VideoFrame",
	62: "DefineFontInfo2",
	64: "EnableDebugger2",
	65: "ScriptLimits",
	66: "SetTabIndex",
	69: "FileAttributes",
	70: "PlaceObject3",
	71: "ImportAssets2",
	73: "DefineFontAlignZones",
	74: "CSMTextSettings",
	75: "DefineFont3",
	76: "SymbolClass",
	77: "Metadata",
	78: "DefineScalingGrid",
	82: "DoABC",
	83: "DefineShape4",
	84: "DefineMorphShape2",
	86: "DefineSceneAndFrameLabelData",
	87: "DefineBinaryData",
	88: "DefineFontName",
	89: "StartSound2",
	90: "DefineBitsJPEG4",
	91: "DefineFont4"
}

def get_byte(src):
	return unpack("<B", src.read(1))[0]

def get_short(src):
	return unpack("<H", src.read(2))[0]

def get_int(src):
	return unpack("<I", src.read(4))[0]

class Swf:
	def __init__(self, download, output):
		self.buf = None

		self.header = {"Version": 0, "Sign": 0}
		self.tags = {}

		self.frame_size = ()

		self.frame_count = 0
		self.frame_rate = 0

		self.download = download
		self.output = output

	def read(self, file):
		self.buf = open(file, "rb")
		self.get_header()
		self.get_tags()

	def get_rect_struct(self):
		stream = Stream(self.buf)
		_bin = stream.get_bin(5)
		return tuple(stream.calc_bin(_bin) for _ in range(4))

	def get_header(self):
		sig = "".join(chr(get_byte(self.buf)) for _ in range(3))
		self.header["Sign"] = sig
		self.header["Version"] = get_byte(self.buf)

		_int = get_int(self.buf)
		if sig[0] == "C":
			unzip = decompress(self.buf.read())
			if len(unzip) + 8 != _int:
				raise ValueError("Invalid compressed content")
			self.buf = BytesIO(unzip)

		self.frame_size = self.get_rect_struct()
		self.frame_rate, self.frame_count = get_short(self.buf), get_short(self.buf)

	def get_tags(self):
		a = 0
		while 1:
			b = get_short(self.buf)
			c = b >> 6
			if c == 0:
				break

			d = b & 0x3f
			if d == 0x3f:
				d = get_int(self.buf)
			e = self.buf.read(d)
			if c in as_tags.keys():
				self.tags[a] = [as_tags[c], e]
			a += 1

	async def decode_hash(self, code, hash_script):
		swf = self.read_swf(self.download)

		offset = {}
		for module in find_all(EXPORT, code):
			name = int(module[1])
			_super = module[3]
			offset[_super] = name
		keys = find_all("writeBytes({0})".format("|".join(offset.keys())), hash_script)
		async with aiofiles.open(self.output, "w+b") as f:
			await f.write(b"".join([swf[int(offset[key])] for key in keys]))

	async def find_crypto_keys(self, lines, crypto_key):
		keys = {}
		for line, content in enumerate(lines):
			if "<q>[public]::Object <q>[private]NULL::" in content:
				key = await find_one(OBJECT, content)
				if key is not None:
					push = await find_one(PUSH_NUM, lines[line + 6])
					if push is not None:
						push = int(push.group(2))
						keys[key.group(1)] = crypto_key[push]
		return keys

	async def find_hash(self, line):
		_hash = await find_one(PUSH_STRING, line)
		if _hash is not None:
			return (_hash.group(3), _hash.group(5))
		return ("", "")

	async def find_var_lines(self, lines, var_keys):
		result = ""
		for line, content in enumerate(lines):
			if "getlocal_0" in content:
				callproperty = await find_one(CALL_PROPERTY, lines[line + 1])
				if callproperty is not None:
					result += var_keys[callproperty.group(3)]
		return result

	def read_swf(self, swf_file):
		self.read(swf_file)

		handle = False
		length = 1

		data = {}
		for n in self.tags:
			tag = self.tags[n]
			if "DefineBinaryData" in tag[0]:
				handle = True
				data[length] = tag[1][6:]
			if handle:
				length += 1
		return data

	async def parse_content(self, dumpscript_list):
		dumpscript = "\n".join(dumpscript_list)
		if len(dumpscript) > 500000:
			copyfile(self.output, self.download)

		_hash, content = await self.find_hash(dumpscript)
		if len(content) < 16:
			raise Exception("Invalid crypto hash")
		var_keys = await self.find_crypto_keys(dumpscript_list, content)
		if len(var_keys) < 10:
			raise Exception("Invalid var keys")
		await self.decode_hash(dumpscript, await self.find_var_lines(dumpscript_list, var_keys))