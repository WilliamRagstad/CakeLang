"""Parser for Cake functions, values, records and Minecraft-inspired calls."""
from dataclasses import dataclass, field
import re
from .lexer import fail

# Kept separate from source expressions: the backend consumes this small IR.
@dataclass
class Statement:
    token: object
    argument: str | tuple[str, str]

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
    lowered: bool = False

BUILTINS = {"say", "command", "call", "repeat", "forEach", "as",
            "r", "s", "a", "p", "e", "effect", "give", "tag", "summon", "kill", "particle"}

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

    def statement(depth=0):
        token = tokens[index]
        if token.kind == "name" and token.value == "return":
            take("name")
            return Expression(token, "return", args=[expression(depth + 1)])
        if token.kind == "name" and tokens[index + 1].kind == "=":
            take("name")
            take("=")
            return Expression(token, "assign", token.value, [expression(depth + 1)])
        return expression(depth)

    def expression(depth=0, precedence=0):
        if depth > 64:
            fail("expression nesting exceeds 64", tokens[index], filepath)
        node = atom(depth)
        while tokens[index].kind in ("+", "-", "*", "/"):
            priority = 2 if tokens[index].kind in ("*", "/") else 1
            if priority < precedence:
                break
            op = take(tokens[index].kind)
            node = Expression(op, "binary", op.kind, [node, expression(depth + 1, priority + 1)])
        return node

    def atom(depth):
        token = tokens[index]
        if token.kind in ("string", "number"):
            take(token.kind)
            node = Expression(token, token.kind, token.value)
        elif optional("-"):
            node = Expression(token, "negate", args=[expression(depth + 1, 3)])
        elif optional("("):
            node = expression(depth + 1)
            take(")")
        elif optional("["):
            values = []
            if tokens[index].kind != "]":
                while True:
                    values.append(expression(depth + 1))
                    if not optional(","):
                        break
            take("]")
            node = Expression(token, "list", args=values)
        elif optional("{"):
            values = []
            is_record = tokens[index].kind == "name" and tokens[index + 1].kind == ":"
            keys = []
            while tokens[index].kind != "}":
                if is_record:
                    key = take("name")
                    if key.value in keys:
                        fail("duplicate record field", key, filepath)
                    keys.append(key.value)
                    take(":")
                    values.append(expression(depth + 1))
                    if not optional(","):
                        break
                else:
                    values.append(statement(depth + 1))
                    optional(";")
            take("}")
            node = Expression(token, "record" if is_record else "block", keys, values)
        else:
            name = take("name")
            value = name.value
            if optional(":"):
                value += ":" + take("name").value
            if optional("("):
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
                node = Expression(name, "call", value, args)
            else:
                node = Expression(name, "name", value)
        while optional("."):
            field_name = take("name")
            node = Expression(field_name, "field", field_name.value, [node])
        return node

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
            if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name.value):
                fail("invalid definition name", name, filepath)
            if (name.value in program.functions or name.value in program.definitions
                    or name.value in BUILTINS or name.value.startswith("__cake_")):
                fail(f"duplicate or reserved function {name.value!r}", name, filepath)
            take("(")
            params = []
            if tokens[index].kind != ")":
                while True:
                    param = take("name")
                    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", param.value) or param.value in ("true", "false"):
                        fail("invalid parameter name", param, filepath)
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
                program.definitions[name.value] = (params, body, name)
        else:
            program.functions["main"].append(statement())
            optional(";")
    return program
