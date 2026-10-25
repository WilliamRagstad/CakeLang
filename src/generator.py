"""Lower the checked subset to Minecraft commands."""
from .checker import check
from .types.datapack import DataPack

def generate(program, namespace="cake", filepath="<string>", debug=False):
    program = check(program, filepath)
    functions = {}
    for name, body in program.functions.items():
        commands = []
        for statement in body:
            kind, value = statement.token.value, statement.argument
            if kind == "say":
                commands.append("say " + value)
            elif kind == "command":
                commands.append(value)
            elif kind == "call":
                commands.append(f"function {namespace}:{value}")
            else:
                raise ValueError(f"unsupported statement: {kind}")
        functions[name] = commands
    pack = DataPack(namespace, functions)
    pack.files()  # Validate resource names even without writing.
    return pack
