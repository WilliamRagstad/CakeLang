from os import write
import sys
from lexer import tokenize
from parser import parse

# === Global variables ===

VERSION = '0.0.1'
USAGE = f"""Welcome to Cake lang compiler v{VERSION}! 🎂
Usage: compiler (options) [file]

Options:
    -h, --help      Print this help message and exit.
    -v, --version   Print version information and exit.
    -l, --lint      Lint the source file.
"""

# === Helper functions ===

def printTokens(tokens: list):
    print("=== Tokens ===")
    for t in tokens:
        print(t['type'], "\t", t['value'])

def compile(filepath: str):
    filepath = filepath.replace('\\', '/')
    filename = filepath[filepath.index('/') + 1:]
    if not (filepath.endswith('.cake') or filepath.endswith('.c')):
        print(f"The specified file '{filename}' was not a valid cake file. Must end with .cake or .c")
        sys.exit(1)
    print(f"Compiling '{filename}'...")
    errorType = "Unknown"
    try:
        errorType = "Syntax"
        tokens = tokenize(filepath)
        # printTokens(tokens)
        errorType = "Semantic"
        program = parse(tokens)
        print("=== AST ===")
        print(program)
    except Exception as e:
        print(f"\n{errorType} Error in '{filepath}':\n    {e}")
        sys.exit(1)

# === Main ===

def main(args: list):
    if len(args) == 0 or '-h' in args or '--help' in args:
        print(USAGE)
    elif '-v' in args or '--version' in args:
        print(f"Cake lang version {VERSION}")
    elif '-l' in args or '--lint' in args:
        print("Linting...")
    # Compile
    elif len(args) > 1:
        print("Too many arguments, try -h or --help to show usage.")
        sys.exit(1)
    elif len(args) == 1:
        compile(args[0])
    else:
        print("Unknown option, try -h or --help to show usage.")
        sys.exit(1)

if __name__ == '__main__':
    # Call main with args
    main(sys.argv[1:])