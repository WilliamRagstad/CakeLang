from os import write
import sys
from termcolor import colored as c
from .checker import check
from .generator import generate
from .lexer import tokenize
from .parser import parse


# === Helper functions ===

def printTokens(tokens: list):
    print("=== Tokens ===")
    for t in tokens:
        print(t['type'], "\t", t['value'])

def compile(filepath: str):
    filepath = filepath.replace('\\', '/')
    filename = filepath[filepath.index('/') + 1:]
    if not (filepath.endswith('.cake') or filepath.endswith('.c')):
        print(c(f"The specified file '{filename}' is not a valid cake file. Must end with .cake or .c", "red"))
        sys.exit(1)
    print(c(f"Compiling ", "cyan") + c(f"'{filename}'", "yellow") + c(f"...", "cyan"))
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
        print(c(f"\n{errorType} Error", "red", attrs=["bold"]) + c(f" in ", "red") + c(f"'{filename}'", "yellow") + c(f":\n    {e}", "red"))
        sys.exit(1)
