from typing import Dict

import aiofiles
import cryptjson
import os

def add_child(obj, parent, child, content=None):
	if parent in obj.keys():
		obj[parent][child] = content or {}
		return

	for subkey in obj.values():
		if isinstance(subkey, dict):
			add_child(subkey, parent, child, content)

async def parse_file(file) -> str:
	async with aiofiles.open(file, "rb") as f:
		return cryptjson.text_encode(await f.read()).decode()

async def read_files(dirname) -> Dict:
	result = {}

	for root, dirs, files in os.walk(dirname):
		if root == dirname:
			for _dir in dirs:
				result[_dir] = {}
			for file in files:
				result[file] = await parse_file(os.path.join(root, file))
		else:
			family = root.split("/")
			if len(family) >= 2:
				parent = family[-1]
				for _dir in dirs:
					add_child(result, parent, _dir)
				for file in files:
					add_child(result, parent, file, await parse_file(os.path.join(root, file)))

	return result