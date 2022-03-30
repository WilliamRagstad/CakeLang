import sys
from src.compiler import compile

# === Global variables ===

VERSION = '0.0.1'
USAGE = f"""Welcome to Cake lang compiler v{VERSION}! 🎂
Usage: compiler (options) [file]

Options:
    -h, --help      Print this help message and exit.
    -v, --version   Print version information and exit.
    -l, --lint      Lint the source file."""

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