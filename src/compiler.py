"""Public compiler entry points. Errors propagate to the CLI."""
from .lexer import tokenize
from .parser import parse
from .checker import check

def analyze(filepath, debug=False):
    program = parse(tokenize(filepath), str(filepath))
    check(program, str(filepath))
    if debug:
        print(program)
    return program

def compile(filepath, debug=False):
    return analyze(filepath, debug)
