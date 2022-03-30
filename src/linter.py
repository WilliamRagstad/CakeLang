
from termcolor import colored as c

from .types.error import CakeError

from .compiler import printProgram, printTokens, printTypeCheck

from .util import path_filename, path_normalize, path_validate, print_bug, print_error
from .lexer import tokenize
from .parser import parse
from .checker import check


def lint(filepath: str, debug: bool = False):
	filepath = path_normalize(filepath)
	filename = path_filename(filepath)
	path_validate(filepath)
	print(c(f"Linting ", "cyan") +
	c(f"'{filename}'", "yellow") + c(f"...", "cyan"))
	try:
		tokens = tokenize(filepath, debug)
		if debug:
			printTokens(tokens)
		program = parse(tokens, debug)
		if debug:
			printProgram(program)
		check(program, debug)
		if debug:
			printTypeCheck()
		# Success
		print(c(f"Successfully linted file, all checks passed!\n", "green"))
	except CakeError as e:
		print_error(e, filename, not debug)
		if debug:
			raise e
	except Exception as e:
		print_bug(e)
