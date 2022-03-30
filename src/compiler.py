from os import write
from .checker import check
from .generator import generate
from .lexer import tokenize
from .parser import error, parse


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
        print(f"\n{errorType} Error in '{filepath}':\n    {e}")
        sys.exit(1)
