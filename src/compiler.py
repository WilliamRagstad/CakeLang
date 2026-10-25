"""Public compiler entry points. Errors propagate to the CLI."""
from .lexer import tokenize
from .parser import parse
from .checker import check

def analyze(filepath, debug=False):
    program = parse(tokenize(filepath), str(filepath))
    program = check(program, str(filepath))
    if debug:
        print(program)
    return program

def compile(filepath, debug=False, output=None, namespace="cake"):
    from pathlib import Path
    from .generator import generate
    pack = generate(analyze(filepath, debug), namespace, str(filepath))
    if output is None:
        output = Path("build") / Path(filepath).stem
    pack.write(output)
    return pack
