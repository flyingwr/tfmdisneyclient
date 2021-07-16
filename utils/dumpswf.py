import subprocess
console = subprocess.Popen(["tools/swfdump", "-a", "tfm.swf"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
with open("swfdump.txt", "w+b") as f:
	f.write(console.stdout.read())