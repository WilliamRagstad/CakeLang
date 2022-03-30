
from termcolor import colored as c

from .util import path_filename, path_normalize, path_validate, print_error
from .lexer import tokenize
from .parser import parse
from .checker import check


def lint(filepath: str):
    filepath = path_normalize(filepath)
    filename = path_filename(filepath)
    path_validate(filepath)
    print(c(f"Linting ", "cyan") +
    c(f"'{filename}'", "yellow") + c(f"...", "cyan"))
    errorType = "Unknown"
    try:
        errorType = "Syntax"
        tokens = tokenize(filepath)
        # printTokens(tokens)
        errorType = "Semantic"
        program = parse(tokens)
        # print("=== AST ===")
        # print(program)
        errorType = "Type"
        check(program)
        errorType = "Generate"
        output = generate(program)
        print("=== Commands ===")
        print(output)
        # TOTO: Output to file
    except Exception as e:
        print_error(errorType, filename, e)