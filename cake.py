"""Cake command line interface."""
import argparse
import sys
from src.compiler import compile
from src.linter import lint
from src.types.error import CakeError

def main(argv=None):
    parser = argparse.ArgumentParser(description="Cake: Minecraft Java Edition 1.20.4")
    parser.add_argument("source")
    parser.add_argument("--version", action="version", version="Cake 0.2.0")
    parser.add_argument("-l", "--lint", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    try:
        (lint if args.lint else compile)(args.source, args.debug)
    except (CakeError, OSError, UnicodeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
