"""Validate every supported statement before generation."""
from .lexer import fail

def check(program, filepath="<string>", debug=False):
    for body in program.functions.values():
        for statement in body:
            value = statement.argument
            if not value.strip() or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
                fail("arguments must be nonempty single-line text without control characters", statement.token, filepath)
            if statement.token.value == "call" and value not in program.functions:
                fail(f"unknown function {value!r}", statement.token, filepath)
            if statement.token.value == "command" and value.startswith(("/", "#")):
                fail("command must not start with / or #", statement.token, filepath)
