"""Location-aware parser for calls, selectors and compile-time definitions."""
from dataclasses import dataclass, field
import re
from .lexer import fail

@dataclass
class Statement:
    token: object
    argument: str

@dataclass
class Expression:
    token: object
    kind: str
    value: object = None
    args: list = field(default_factory=list)

@dataclass
class Program:
    functions: dict
    definitions: dict = field(default_factory=dict)
    imports: set = field(default_factory=set)

def parse(tokens, filepath="<string>", debug=False):
    index = 0
    program = Program({"main": []})

    def take(kind):
        nonlocal index
        token = tokens[index]
        if token.kind != kind:
            fail(f"expected {kind}, got {token.value or 'end of input'!r}; unsupported syntax", token, filepath)
        index += 1
        return token

    def optional(kind):
        if tokens[index].kind == kind:
            take(kind)
            return True
        return False

    def expression(depth=0):
        if depth > 64:
            fail("expression nesting exceeds 64", tokens[index], filepath)
        token = tokens[index]
        if token.kind in ("string", "number"):
            take(token.kind)
            return Expression(token, token.kind, token.value)
        if token.kind == "{":
            take("{")
            body = []
            while tokens[index].kind != "}":
                body.append(expression(depth + 1))
                optional(";")
            take("}")
            return Expression(token, "block", args=body)
        name = take("name")
        value = name.value
        if optional(":"):
            value += ":" + take("name").value
        if not optional("("):
            return Expression(name, "name", value)
        args = []
        if tokens[index].kind != ")":
            while True:
                if tokens[index].kind == "name" and tokens[index + 1].kind in ("=", "<="):
                    key = take("name")
                    op = take(tokens[index].kind)
                    args.append(Expression(key, "filter", (key.value, op.kind), [expression(depth + 1)]))
                else:
                    args.append(expression(depth + 1))
                if not optional(","):
                    break
        take(")")
        return Expression(name, "call", value, args)

    while tokens[index].kind != "eof":
        token = tokens[index]
        if token.value == "import":
            take("name")
            subject = take("name")
            source = take("name")
            if source.value != "from":
                fail("expected from", source, filepath)
            module = take("name")
            if subject.value != "player" or module.value != "minecraft":
                fail("only import player from minecraft is supported", subject, filepath)
            program.imports.add("player")
            optional(";")
        elif token.value in ("function", "def", "macro"):
            keyword = take("name")
            name = take("name")
            if name.value in program.functions or name.value in program.definitions or name.value in {"say", "command", "call", "repeat", "r"}:
                fail(f"duplicate or reserved function {name.value!r}", name, filepath)
            take("(")
            params = []
            if tokens[index].kind != ")":
                while True:
                    param = take("name")
                    if param.value in params:
                        fail("duplicate parameter", param, filepath)
                    params.append(param.value)
                    if not optional(","):
                        break
            take(")")
            body = expression()
            if body.kind != "block":
                fail("expected function body", body.token, filepath)
            if keyword.value == "function":
                if params or not re.fullmatch(r"[a-z_][a-z0-9_]*", name.value):
                    fail("runtime functions require no parameters and lowercase resource names", name, filepath)
                program.functions[name.value] = body.args
            else:
                if len(body.args) != 1:
                    fail("def/macro bodies must contain one selector expression", name, filepath)
                program.definitions[name.value] = (params, body.args[0], name)
        else:
            program.functions["main"].append(expression())
            optional(";")
    return program
