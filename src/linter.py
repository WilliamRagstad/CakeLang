from .compiler import analyze

def lint(filepath, debug=False):
    return analyze(filepath, debug)
