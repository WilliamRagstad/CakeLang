import sys
from termcolor import colored as c
from src.compiler import compile
from src.linter import lint

# === Global variables ===

VERSION = '1.0.0-Alpha'
USAGE = f"""{c(f"Welcome to the Cake 🎂 compiler version {VERSION}!", "yellow")}
{c("Usage:", "cyan")} cake (options) [file.c|.cake]

{c("Options:", "cyan")}
	-h, --help      Print this help message and exit.
	-v, --version   Print version information and exit.
	-l, --lint      Lint the source file.
	--debug         Print debug information.

{c("Examples:", "cyan")}
	cake file.c
	cake -l file.cake
	cake -v
	cake --help

 ____________________________________________________________________
|                                                                    |
| {c("Wiki and Documentation", "cyan")}                                             |
| View the wiki at {c("https://github.com/WilliamRagstad/CakeLang/wiki", "blue")}.  |
|                                                                    |
| {c("Author", "cyan")}                                                             |
| Developed by {c("@WilliamRagstad", "blue", attrs=["underline"])}, a.k.a Dotch.                         |
|____________________________________________________________________|\n"""

# === Helper functions ===
def print_error(msg: str):
	print(c(f"{msg}, try -h or --help to show usage.", "red"))
	sys.exit(1)

# === Main ===

def main(args: list):
	debug = False
	if '--debug' in args:
		debug = True
		args.remove('--debug')
	if len(args) == 0 or '-h' in args or '--help' in args:
		print(USAGE)
	elif '-v' in args or '--version' in args:
		print(c(f"Cake {VERSION}", "yellow"))
	elif '-l' in args or '--lint' in args:
		if len(args) == 1:
			print_error("Missing file to lint")
		elif len(args) > 2:
			print_error("Too many files specified")
		else:
			lint(args[-1], debug)
	# Compile
	elif len(args) > 1:
		print_error("Too many arguments")
	elif len(args) == 1:
		compile(args[-1], debug)
	else:
		print_error("Unknown option")

if __name__ == '__main__':
	# Call main with args
	main(sys.argv[1:])