
import sys
from termcolor import colored as c

def path_normalize(path: str):
	return path.replace('\\', '/')

def path_filename(path: str):
	return path[path.rindex('/') + 1:]

def path_validate(path: str):
	ext = path[path.rindex('.') + 1:]
	if not (ext == 'cake' or ext == 'c'):
		print(c(f"The specified file '{path}' is not a valid cake file. Must end with .cake or .c", "red"))
		sys.exit(1)
	return

def print_error(type: str, file: str, exception: Exception):
	print(c(f"\n{type} Error", "red", attrs=["bold"]) + c(f" in ", "red") + c(f"'{file}'", "yellow") + c(f":\n    {e}", "red"))
	sys.exit(1)