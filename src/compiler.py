from os import write
from termcolor import colored as c

from .types.program import Program
from .util import path_filename, path_normalize, path_validate, print_error
from .lexer import tokenize
from .parser import parse
from .checker import check
from .generator import generate

def printTokens(tokens: list):
    print(c("=== Tokens ===", "cyan"))
    for t in tokens:
        print(t['type'].ljust(10), '|', t['value'])

def printProgram(program: Program):
    print(c("=== Program ===", "cyan"))
    print("Lines:", program.lines)
    print("Imports:")
    for i in program.imports:
        print("    ", i)
    if len(program.imports) == 0: print("  None")
    print("AST:")
    for b in program.body:
        print("    ", b)
    if len(program.body) == 0: print("  None")

def printCommands(commands):
    print(c("=== Commands ===", "cyan"))
    print(commands)

def printTypeCheck():
    print(c("=== Type Check ===", "cyan"))
    print("Type checking successful!")

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
            printProgram(program)
        errorType = "Type"
        check(program, debug)
        if debug:
            printTypeCheck()
        errorType = "Generate"
        output = generate(program, debug)
        if debug:
            printCommands(output)
        # TOTO: Output to file
    except Exception as e:
        print_error(errorType, filename, e)
