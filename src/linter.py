
from termcolor import colored as c

from .compiler import printAST, printTokens

from .util import path_filename, path_normalize, path_validate, print_error
from .lexer import tokenize
from .parser import parse
from .checker import check


def lint(filepath: str, debug: bool = False):
    filepath = path_normalize(filepath)
    filename = path_filename(filepath)
    path_validate(filepath)
    print(c(f"Linting ", "cyan") +
    c(f"'{filename}'", "yellow") + c(f"...", "cyan"))
    errorType = "Unknown"
    try:
        errorType = "Syntax"
        tokens = tokenize(filepath, debug)
        if debug:
            printTokens(tokens)
        errorType = "Semantic"
        program = parse(tokens, debug)
        if debug:
            printAST(program)
        errorType = "Type"
        check(program, debug)
        if debug:
            print("Type checking successful!")
        # Success
        print(c(f"Successfully linted file, all checks passed!\n", "green"))
    except Exception as e:
        print_error(errorType, filename, e)
