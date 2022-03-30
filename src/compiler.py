from os import write
from termcolor import colored as c
from .util import path_filename, path_normalize, path_validate, print_error
from .lexer import tokenize
from .parser import parse
from .checker import check
from .generator import generate

def printTokens(tokens: list):
    print("=== Tokens ===")
    for t in tokens:
        print(t['type'], "\t", t['value'])

def printAST(ast):
    print("=== AST ===")
    print(ast)

def printCommands(commands):
    print("=== Commands ===")
    print(commands)

def compile(filepath: str, debug: bool = False):
    filepath = path_normalize(filepath)
    filename = path_filename(filepath)
    path_validate(filepath)
    print(c(f"Compiling ", "cyan") + c(f"'{filename}'", "yellow") + c(f"...", "cyan"))
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
        errorType = "Generate"
        output = generate(program, debug)
        if debug:
            printCommands(output)
        # TOTO: Output to file
    except Exception as e:
        print_error(errorType, filename, e)
