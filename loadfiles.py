import cryptjson
import os

data = {}

def add_child(obj, parent, child, content=None):
	if parent in obj.keys():
		obj[parent][child] = content or {}
		return

	for subkey in obj.values():
		if isinstance(subkey, dict):
			add_child(subkey, parent, child, content)

def read_files(dirname):
	def parse_file(file):
		with open(file, "rb") as f:
			return cryptjson.text_encode(f.read()).decode()

	for root, dirs, files in os.walk(dirname):
		if root == dirname:
			for _dir in dirs:
				data[_dir] = {}
			for file in files:
				data[file] = "" # parse_file(os.path.join(root, file))
		else:
			family = root.split("\\")
			if len(family) >= 2:
				parent = family[-1]
				for _dir in dirs:
					add_child(data, parent, _dir)
				for file in files:
					add_child(data, parent, file, "") # parse_file(os.path.join(root, file)))
