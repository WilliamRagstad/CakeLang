"""Type-check and expand compile-time Cake expressions into simple statements."""
import json
import re
from .lexer import fail
from .parser import Expression, Program, Statement

MAX_COMMANDS = 10000

def check(program, filepath="<string>", debug=False):
    def error(message, node):
        fail(message, node.token, filepath)

    def text(value, node):
        if not isinstance(value, str) or not value.strip() or any(
                ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
            error("expected nonempty single-line text without control characters", node)
        return value

    def evaluate(node, scope, stack=()):
        if node.kind in ("string", "number"):
            return node.value
        if node.kind == "name":
            if node.value in scope:
                return scope[node.value]
            if node.value == "minecraft:player" or (node.value == "player" and "player" in program.imports):
                return ("entity", "minecraft:player")
            error(f"unknown name {node.value!r}", node)
        if node.kind != "call":
            error("unsupported value expression", node)
        if node.value in program.definitions:
            params, body, _ = program.definitions[node.value]
            if len(params) != len(node.args):
                error(f"{node.value} expects {len(params)} arguments", node)
            if node.value in stack or len(stack) >= 64:
                error("recursive or excessively nested compile-time definition", node)
            values = [evaluate(arg, scope, stack) for arg in node.args]
            if any(type(value) not in (int, float) for value in values):
                error("def/macro parameters must be numeric", node)
            result = evaluate(body, dict(zip(params, values)), stack + (node.value,))
            if not isinstance(result, tuple) or result[0] != "selector":
                error("def/macro must return a selector", node)
            return result
        if node.value == "r":
            filters = {}
            for arg in node.args:
                if arg.kind != "filter" or arg.value not in (("type", "="), ("radius", "<=")):
                    error("r supports only type=player and radius<=number", arg)
                key = arg.value[0]
                if key in filters:
                    error(f"duplicate selector filter {key}", arg)
                value = evaluate(arg.args[0], scope, stack)
                if key == "type" and value != ("entity", "minecraft:player"):
                    error("only minecraft:player entity type is supported", arg)
                if key == "radius" and (not isinstance(value, (int, float)) or value < 0):
                    error("radius must be a nonnegative number", arg)
                filters[key] = value
            arguments = []
            if "type" in filters:
                arguments.append("type=minecraft:player")
            if "radius" in filters:
                arguments.append(f"distance=..{filters['radius']:g}")
            return ("selector", "@r" + ("[" + ",".join(arguments) + "]" if arguments else ""))
        error(f"unsupported value call {node.value!r}", node)

    # Validate unused definitions too, with symbolic numeric arguments. The
    # supported definition contract is selector-valued with numeric parameters.
    for name, (params, body, token) in program.definitions.items():
        result = evaluate(body, dict.fromkeys(params, 0), (name,))
        if not isinstance(result, tuple) or result[0] != "selector":
            fail("def/macro must return a selector", token, filepath)

    count = 0
    def lower(nodes, depth=0):
        nonlocal count
        if depth > 64:
            error("repeat nesting exceeds 64", nodes[0])
        result = []
        for node in nodes:
            if isinstance(node, Statement):
                kind, value = node.token.value, text(node.argument, node)
            else:
                if node.kind != "call":
                    error("unsupported statement; expected a call", node)
                kind = node.value
                if kind == "repeat":
                    if len(node.args) != 2 or node.args[1].kind != "block":
                        error("repeat expects a count and a block", node)
                    times = evaluate(node.args[0], {})
                    if type(times) is not int or not 0 <= times <= 1024:
                        error("repeat count must be an integer from 0 to 1024", node)
                    body = lower(node.args[1].args, depth + 1)
                    count += len(body) * max(0, times - 1)
                    if count > MAX_COMMANDS:
                        error("expanded program exceeds 10000 commands", node)
                    result.extend(body * times)
                    continue
                if kind == "say" and len(node.args) == 2:
                    selector = evaluate(node.args[0], {})
                    if not isinstance(selector, tuple) or selector[0] != "selector":
                        error("say first argument must be a selector", node)
                    message = text(evaluate(node.args[1], {}), node)
                    if any(part != "{@s}" for part in re.findall(r"\{@[^}]*\}", message)):
                        error("only {@s} interpolation is supported", node)
                    parts = re.split(r"(\{@s\})", message)
                    components = [{"selector": "@s"} if part == "{@s}" else {"text": part}
                                  for part in parts if part]
                    value = f"execute as {selector[1]} at @s run tellraw @a " + json.dumps(components, ensure_ascii=False, separators=(",", ":"))
                    kind = "command"
                else:
                    if kind not in ("say", "command", "call"):
                        error(f"unsupported construct {kind!r}", node)
                    if len(node.args) != 1:
                        error(f"{kind} expects one string argument", node)
                    value = text(evaluate(node.args[0], {}), node)
            if kind == "call" and value not in program.functions:
                error(f"unknown function {value!r}", node)
            if kind == "command" and value.lstrip().startswith(("/", "#")):
                error("command must not start with / or #", node)
            from .lexer import Token
            result.append(Statement(Token("name", kind, node.token.line, node.token.column), value))
            count += 1
            if count > MAX_COMMANDS:
                error("expanded program exceeds 10000 commands", node)
        return result

    return Program({name: lower(body) for name, body in program.functions.items()})
