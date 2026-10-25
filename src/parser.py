"""Recursive descent parser; no global parser state."""
from dataclasses import dataclass
from .lexer import fail

@dataclass
class Statement:
    token: object
    argument: str

@dataclass
class Program:
    functions: dict

def parse(tokens, filepath="<string>", debug=False):
    index = 0
    functions = {"main": []}

    def take(kind):
        nonlocal index
        token = tokens[index]
        if token.kind != kind:
            fail(f"expected {kind}, got {token.value or 'end of input'!r}; unsupported syntax", token, filepath)
        index += 1
        return token

    def statement():
        token = take("name")
        if token.value not in {"say", "command", "call"}:
            fail(f"unsupported construct {token.value!r}", token, filepath)
        take("(")
        argument = take("string").value
        take(")")
        if tokens[index].kind == ";":
            take(";")
        return Statement(token, argument)

    while tokens[index].kind != "eof":
        if tokens[index].value == "function":
            take("name")
            name = take("name")
            if name.value in functions:
                fail(f"duplicate or reserved function {name.value!r}", name, filepath)
            import re
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", name.value):
                fail("function names must be lowercase resource names", name, filepath)
            take("(")
            take(")")
            take("{")
            body = []
            while tokens[index].kind != "}":
                body.append(statement())
            take("}")
            functions[name.value] = body
        else:
            functions["main"].append(statement())
    return Program(functions)
