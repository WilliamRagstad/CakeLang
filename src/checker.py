"""Resolve lexical bindings and lower typed Cake abstractions to command IR."""
import json
import math
import re
from .lexer import Token, fail
from .parser import BUILTINS, Program, Statement
from .minecraft import Resource, Selector, SIGNATURES, render

VOID = object()
MAX_COMMANDS = 10000

class Checker:
    def __init__(self, program, filepath):
        self.program, self.filepath = program, filepath
        self.globals = {}
        self.functions = {}
        self.current = []
        self.stack = []
        self.command_count = 0
        self.helper_count = 0
        self.evaluations = 0

    def error(self, message, node):
        fail(message, node.token, self.filepath)

    def text(self, value, node):
        if not isinstance(value, str) or not value.strip() or any(
                ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
            self.error("expected nonempty single-line text without control characters", node)
        return value

    def emit(self, kind, value, node):
        self.command_count += 1
        if self.command_count > MAX_COMMANDS:
            self.error("expanded program exceeds 10000 commands", node)
        self.current.append(Statement(Token("name", kind, node.token.line, node.token.column), value))

    def validate(self, nodes, names, in_def=False, depth=0):
        """Check names/structure even in unused generic definitions."""
        names = set(names)
        for index, node in enumerate(nodes):
            if depth > 64:
                self.error("expression nesting exceeds 64", node)
            if node.kind == "assign":
                if node.value in names or node.value in BUILTINS or node.value in self.program.definitions:
                    self.error(f"duplicate or reserved binding {node.value!r}", node)
                self.validate(node.args, names, in_def, depth + 1)
                names.add(node.value)
                continue
            if node.kind == "return":
                if not in_def or index != len(nodes) - 1:
                    self.error("return must be the final statement of a def/macro", node)
            if node.kind == "name":
                value = node.value
                if not (value in names or value in ("true", "false", "@s", "@a", "@p", "@r", "@e")
                        or ":" in value or value in self.program.imports):
                    self.error(f"unknown name {value!r}", node)
            if node.kind == "call":
                name = node.value
                if name not in BUILTINS and name not in self.program.definitions and name not in self.program.functions:
                    self.error(f"unsupported construct {name!r}", node)
                if name in self.program.definitions and len(node.args) != len(self.program.definitions[name][0]):
                    self.error(f"wrong argument count for {name}", node)
                if name == "forEach":
                    if len(node.args) != 3 or node.args[1].kind != "name" or node.args[2].kind != "block":
                        self.error("forEach expects a list, a binding name and a block", node)
                    self.validate([node.args[0]], names, in_def, depth + 1)
                    self.validate(node.args[2].args, names | {node.args[1].value}, False, depth + 1)
                    continue
            self.validate(node.args, names, in_def, depth + 1)

    def validate_definitions(self):
        globals_available = {node.value for node in self.program.functions["main"] if node.kind == "assign"}
        graph = {}
        def calls(node):
            result = {node.value} if node.kind == "call" and node.value in self.program.definitions else set()
            for arg in node.args:
                result.update(calls(arg))
            return result
        for name, (params, body, _) in self.program.definitions.items():
            # Parameters may shadow global bindings.
            self.validate(body.args, globals_available | set(params), True)
            graph[name] = calls(body)
        visited = set()
        def visit(name, active):
            if name in active or len(active) >= 64:
                fail("recursive or excessively nested compile-time definition",
                     self.program.definitions[name][2], self.filepath)
            if name in visited:
                return
            for child in graph[name]:
                visit(child, active + (name,))
            visited.add(name)
        for name in graph:
            visit(name, ())
        self.validate(self.program.functions["main"], set())
        for name, body in self.program.functions.items():
            if name != "main":
                self.validate(body, globals_available)

    def value(self, node, scope, pure=True):
        self.evaluations += 1
        if self.evaluations > 100000:
            self.error("compile-time evaluation exceeds 100000 steps", node)
        kind = node.kind
        if kind == "string":
            return self.text(node.value, node)
        if kind == "number":
            return node.value
        if kind == "name":
            if node.value in scope:
                return scope[node.value]
            if node.value in self.globals:
                return self.globals[node.value]
            if node.value in ("true", "false"):
                return node.value == "true"
            if node.value in ("@s", "@a", "@p", "@r", "@e"):
                return Selector(node.value)
            if node.value in self.program.imports:
                return Resource("minecraft:" + node.value)
            if ":" in node.value:
                return Resource(node.value)
            self.error(f"unknown name {node.value!r}", node)
        if kind == "record":
            return dict(zip(node.value, [self.value(arg, scope) for arg in node.args]))
        if kind == "list":
            return [self.value(arg, scope) for arg in node.args]
        if kind == "block" and not node.args:
            return {}
        if kind == "field":
            record = self.value(node.args[0], scope)
            if not isinstance(record, dict) or node.value not in record:
                self.error(f"missing record field {node.value!r}", node)
            return record[node.value]
        if kind in ("binary", "negate"):
            args = [self.value(arg, scope) for arg in node.args]
            if any(type(value) not in (int, float) for value in args):
                self.error("arithmetic requires numeric values", node)
            if kind == "negate":
                return -args[0]
            a, b = args
            if node.value == "/" and b == 0:
                self.error("division by zero", node)
            result = {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b}[node.value]()
            if abs(result) > 1e100 or (type(result) is float and not math.isfinite(result)):
                self.error("arithmetic result is out of range", node)
            return result
        if kind != "call":
            self.error("unsupported value expression", node)
        name = node.value
        if name in self.program.definitions:
            params, body, _ = self.program.definitions[name]
            if len(params) != len(node.args) or any(arg.kind == "filter" for arg in node.args):
                self.error(f"{name} expects {len(params)} positional arguments", node)
            if name in self.stack or len(self.stack) >= 64:
                self.error("recursive or excessively nested compile-time definition", node)
            values = [self.value(arg, scope) for arg in node.args]
            self.stack.append(name)
            try:
                result = self.body(body.args, dict(zip(params, values)), pure, True)
            finally:
                self.stack.pop()
            if pure and result is VOID:
                self.error(f"{name} does not return a value", node)
            return result
        if name in ("r", "s", "a", "p", "e"):
            return self.selector(node, scope)
        if pure:
            self.error(f"{name} is an operation, not a value", node)
        self.operation(node, scope)
        return VOID

    def selector(self, node, scope):
        filters = {}
        allowed = {("type", "="), ("radius", "<="), ("tag", "="), ("limit", "=")}
        for arg in node.args:
            if arg.kind != "filter" or arg.value not in allowed:
                self.error("unsupported selector filter", arg)
            key = arg.value[0]
            if key in filters:
                self.error(f"duplicate selector filter {key}", arg)
            value = self.value(arg.args[0], scope)
            if key == "type":
                if not isinstance(value, Resource):
                    self.error("selector type must be a namespaced resource or imported player", arg)
                if node.value in ("r", "a", "p") and value.name != "minecraft:player":
                    self.error("player selectors require minecraft:player", arg)
                filters[key] = value.name
            elif key == "radius":
                if type(value) not in (int, float) or not 0 <= value <= 30000000:
                    self.error("radius must be a nonnegative number at most 30000000", arg)
                filters["distance"] = ".." + format(value, ".15g")
            elif key == "tag":
                if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.+-]+", value):
                    self.error("invalid selector tag", arg)
                filters[key] = value
            elif key == "limit":
                if type(value) is not int or not 1 <= value <= 2147483647 or node.value == "s":
                    self.error("limit must be a positive integer on a non-self selector", arg)
                filters[key] = str(value)
        # Detect duplicate radius even though it is rendered as distance.
        keys = [arg.value[0] for arg in node.args]
        if len(keys) != len(set(keys)):
            self.error("duplicate selector filter", node)
        suffix = "[" + ",".join(f"{key}={value}" for key, value in filters.items()) + "]" if filters else ""
        return Selector("@" + node.value + suffix)

    def bind(self, node, scope):
        required, defaults = SIGNATURES[node.value]
        fields = list(required) + [key for key, _ in defaults]
        values = {}
        named = False
        for index, arg in enumerate(node.args):
            if arg.kind == "filter":
                named = True
                key, op = arg.value
                if op != "=" or key not in fields:
                    self.error("unknown named argument", arg)
                expression = arg.args[0]
            else:
                if named or index >= len(fields):
                    self.error("unexpected positional argument", arg)
                key, expression = fields[index], arg
            if key in values:
                self.error(f"duplicate argument {key}", arg)
            values[key] = self.value(expression, scope)
        if any(key not in values for key in required):
            self.error(f"{node.value} requires {', '.join(required)}", node)
        for key, default in defaults:
            values.setdefault(key, default)
        return values

    def capture(self, nodes, scope):
        previous = self.current
        self.current = []
        try:
            self.body(nodes, scope)
            return self.current
        finally:
            self.current = previous

    def operation(self, node, scope):
        name = node.value
        if name in SIGNATURES:
            command = render(name, self.bind(node, scope), lambda message: self.error(message, node))
            self.emit("command", command, node)
            return
        if name in self.program.functions:
            if node.args:
                self.error("runtime functions have no arguments; use def for parameterized functions", node)
            self.emit("call", name, node)
            return
        if name == "repeat":
            if len(node.args) != 2 or node.args[1].kind != "block":
                self.error("repeat expects a count and a block", node)
            times = self.value(node.args[0], scope)
            if type(times) is not int or not 0 <= times <= 1024:
                self.error("repeat count must be an integer from 0 to 1024", node)
            commands = self.capture(node.args[1].args, dict(scope))
            self.command_count -= len(commands)
            for _ in range(times):
                for command in commands:
                    self.emit(command.token.value, command.argument, node)
            return
        if name == "forEach":
            if len(node.args) != 3 or node.args[1].kind != "name" or node.args[2].kind != "block":
                self.error("forEach expects a list, a binding name and a block", node)
            values = self.value(node.args[0], scope)
            if not isinstance(values, list) or len(values) > 1024:
                self.error("forEach expects a list of at most 1024 elements", node)
            for value in values:
                local = dict(scope)
                local[node.args[1].value] = value
                self.body(node.args[2].args, local)
            return
        if name == "as":
            if len(node.args) != 2 or node.args[1].kind != "block":
                self.error("as expects a selector and a block", node)
            target = self.value(node.args[0], scope)
            if not isinstance(target, Selector):
                self.error("as expects a selector", node)
            self.helper_count += 1
            helper = f"__cake_{self.helper_count}"
            self.functions[helper] = self.capture(node.args[1].args, dict(scope))
            self.emit("execute_call", (f"execute as {target.command} at @s", helper), node)
            return
        if name == "say" and len(node.args) == 2:
            selector, message = [self.value(arg, scope) for arg in node.args]
            if not isinstance(selector, Selector):
                self.error("say first argument must be a selector", node)
            message = self.text(message, node)
            if any(part != "{@s}" for part in re.findall(r"\{@[^}]*\}", message)):
                self.error("only {@s} interpolation is supported", node)
            parts = re.split(r"(\{@s\})", message)
            components = [{"selector": "@s"} if part == "{@s}" else {"text": part}
                          for part in parts if part]
            self.emit("command", f"execute as {selector.command} at @s run tellraw @a " +
                      json.dumps(components, ensure_ascii=False, separators=(",", ":")), node)
            return
        if name not in ("say", "command", "call") or len(node.args) != 1:
            self.error(f"unsupported call or argument count for {name}", node)
        value = self.text(self.value(node.args[0], scope), node)
        if name == "call" and value not in self.program.functions:
            self.error(f"unknown function {value!r}", node)
        if name == "command" and value.lstrip().startswith(("/", "#")):
            self.error("command must not start with / or #", node)
        self.emit(name, value, node)

    def body(self, nodes, scope, pure=False, in_def=False):
        result = VOID
        for index, node in enumerate(nodes):
            if node.kind == "assign":
                if node.value in scope:
                    self.error(f"binding {node.value!r} is immutable", node)
                scope[node.value] = self.value(node.args[0], scope)
                result = VOID
            elif node.kind == "return":
                if not in_def or index != len(nodes) - 1:
                    self.error("return must be the final statement of a def/macro", node)
                return self.value(node.args[0], scope, pure)
            else:
                if not in_def and node.kind != "call":
                    self.error("unsupported statement; expected assignment or call", node)
                result = self.value(node, scope, pure)
        return result

    def run(self):
        self.validate_definitions()
        self.current = []
        self.body(self.program.functions["main"], self.globals)
        self.functions["main"] = self.current
        for name, body in self.program.functions.items():
            if name != "main":
                self.current = []
                self.body(body, {})
                self.functions[name] = self.current
        return Program(self.functions, lowered=True)

def check(program, filepath="<string>", debug=False):
    if program.lowered:
        return program
    return Checker(program, filepath).run()
