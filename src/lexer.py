from io import TextIOWrapper
from termcolor import colored

from .types.error import CakeSyntaxError
from .types.token import OperatorToken, Token

# === Global variables ===

filepath = None
line: int = 1
column: int = 0
tokens = []
debug = False

# === Helper functions ===

def dprint(*args):
	global debug
	if debug: print(*args)

def next(file: TextIOWrapper) -> str | None:
	global line, column
	c = file.read(1)
	column += 1
	if c == '\n':
		line += 1
		column = 0
	elif c == '':
		return None
	return c


# === Lexing ===

def read_number(first: str, f: TextIOWrapper):
	global line, column
	startLine = line
	startColumn = column
	number = first
	c = next(f)
	while c.isdigit():
		number += c
		c = next(f)
	return Token('Number', int(number), startLine, startColumn, line, column, c)

def read_identifier(first: str, f: TextIOWrapper):
	global line, column
	startLine = line
	startColumn = column
	identifier = first
	c = next(f)
	while c.isalpha() or c.isdigit() or c == '_':
		identifier += c
		c = next(f)
	if identifier in ['true', 'false']:
		return Token('Boolean', identifier == 'true', startLine, startColumn, line, column, c)
	elif identifier in ['macro', 'function', 'comp', 'if', 'else', 'while', 'for', 'import', 'from', 'as', 'repeat', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new', 'typeof', 'in', 'of']:
		return Token('Keyword', identifier, startLine, startColumn, line, column, c)
	else: return Token('Identifier', identifier, startLine, startColumn, line, column, c)

def read_string(f: TextIOWrapper):
	global line, column, filepath
	startLine = line
	startColumn = column
	string = ''
	c = next(f)
	while c != '"':
		if c == '\n':
			raise CakeSyntaxError(f"Unexpected newline in string at line {line} column {column}", filepath)
		string += c
		c = next(f)
	return Token('String', string, startLine, startColumn, line, column, c)

def read_comment(f: TextIOWrapper):
	global line, column
	startLine = line
	startColumn = column
	comment = ''
	c = next(f)
	while c != '\n' and c != None:
		comment += c
		c = next(f)
	return Token('Comment', comment.strip(), startLine, startColumn, line, column, c)

def tokenize(_filepath: str, _debug: bool = False) -> list[Token]:
	global line, column, tokens, debug, filename
	tokens = []
	line = 1
	column = 0
	debug = _debug
	filepath = _filepath
	dprint('>',colored("Tokenizing...", "cyan"))
	with open(filepath, 'r', encoding='utf8') as f:
		readNext = True
		c = None
		while True:
			if readNext:
				c = next(f)
			readNext = True
			if not c:
				break # End of file
			if c in [' ', '\t', '\r', '\n']:
				continue
			# If c is a digit, read until non-digit
			if c.isdigit():
				t = read_number(c, f)
				tokens.append(t)
				c = t.next
				readNext = False
				continue
			elif c.isalpha() or c == '@' or c == '_':
				t = read_identifier(c, f)
				tokens.append(t)
				c = t.next
				readNext = False
				continue
			elif c == '"':
				t = read_string(f)
				tokens.append(t)
				continue
			elif c == '=':
				tokens.append(OperatorToken('Assignment', c, line, column, line, column + 1))
				continue
			elif c in ['+', '-', '*', '/', '%', '!', '<', '>', ':', '&', '|', '^']:
				nc = next(f)
				if nc == '=':
					tokens.append(OperatorToken('Infix', c + nc, line, column, line, column + 2))
					continue
				else:
					tokens.append(OperatorToken('Infix', c, line, column, line, column + 1))
					c = nc
					readNext = False
					continue
			elif c in ['(', ')', '{', '}', '[', ']', ',']:
				tokens.append(Token('Separator', c, line, column, line, column + 1, None))
				continue
			elif c == '#':
				t = read_comment(f)
				tokens.append(t)
				continue
			else:
				raise CakeSyntaxError(f"Unexpected character '{c}' at line {line} column {column}-{column + 1}", filepath)
	return tokens
