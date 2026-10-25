"""Typed Minecraft operations. Source programs never assemble these strings."""
from dataclasses import dataclass
import json
import re

@dataclass(frozen=True)
class Selector:
    command: str

@dataclass(frozen=True)
class Resource:
    name: str

# Required arguments precede optional (name, default) pairs.
SIGNATURES = {
    "effect": (("target", "effect", "duration"), (("amplifier", 0), ("hideParticles", True))),
    "give": (("target", "item"), (("count", 1),)),
    "tag": (("target", "name"), (("enabled", True),)),
    "kill": (("target",), ()),
    "summon": (("entity", "position"), (("data", {}),)),
    "particle": (("target", "particle", "position", "spread"), (("speed", 0), ("count", 1), ("force", True))),
}

def render(name, args, error):
    def require(condition, message):
        if not condition:
            error(message)

    def selector(value):
        require(isinstance(value, Selector), "expected a selector")
        return value.command

    def resource(value):
        require(isinstance(value, Resource), "expected a namespaced Minecraft resource")
        return value.name

    def number(value, minimum, maximum, integer=False):
        require(type(value) is int if integer else type(value) in (int, float),
                "expected an integer" if integer else "expected a number")
        require(minimum <= value <= maximum, f"number must be between {minimum} and {maximum}")
        return str(value) if type(value) is int else format(value, ".15g")

    def boolean(value):
        require(type(value) is bool, "expected true or false")
        return "true" if value else "false"

    def tag_name(value):
        require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.+-]+", value) is not None,
                "tag names must contain only letters, digits, _, ., + or -")
        return value

    def vector(value, relative=False, minimum=-30000000):
        require(isinstance(value, dict) and set(value) == {"x", "y", "z"},
                "expected a record with exactly x, y and z fields")
        values = [number(value[key], minimum, 30000000) for key in ("x", "y", "z")]
        return " ".join(("~" + (v if v != "0" else "")) if relative else v for v in values)

    if name == "effect":
        return f"effect give {selector(args['target'])} {resource(args['effect'])} {number(args['duration'], 1, 1000000, True)} {number(args['amplifier'], 0, 255, True)} {boolean(args['hideParticles'])}"
    if name == "give":
        return f"give {selector(args['target'])} {resource(args['item'])} {number(args['count'], 1, 2147483647, True)}"
    if name == "tag":
        boolean(args["enabled"])
        return f"tag {selector(args['target'])} {'add' if args['enabled'] else 'remove'} {tag_name(args['name'])}"
    if name == "kill":
        return f"kill {selector(args['target'])}"
    if name == "summon":
        entity, position, data = resource(args["entity"]), vector(args["position"], True), args["data"]
        require(isinstance(data, dict), "summon data must be a record")
        require(set(data) <= {"noAI", "persistent", "tags", "name"}, "unsupported summon data field")
        nbt = []
        for key, nbt_key in (("noAI", "NoAI"), ("persistent", "PersistenceRequired")):
            if key in data:
                boolean(data[key])
                nbt.append(f"{nbt_key}:{1 if data[key] else 0}b")
        if "tags" in data:
            require(isinstance(data["tags"], list), "summon tags must be a list")
            nbt.append("Tags:" + json.dumps([tag_name(t) for t in data["tags"]], separators=(",", ":")))
        if "name" in data:
            require(isinstance(data["name"], str), "summon name must be a string")
            # SNBT double-quoted string containing a JSON text component.
            nbt.append("CustomName:" + json.dumps(json.dumps({"text": data["name"]}, separators=(",", ":"))))
        return f"summon {entity} {position}" + (" {" + ",".join(nbt) + "}" if nbt else "")
    if name == "particle":
        target = selector(args["target"])
        position = vector(args["position"], True)
        spread = vector(args["spread"], minimum=0)
        speed = number(args["speed"], 0, 1000000)
        count = number(args["count"], 0, 2147483647, True)
        boolean(args["force"])
        return f"execute as {target} at @s run particle {resource(args['particle'])} {position} {spread} {speed} {count} {'force' if args['force'] else 'normal'} @s"
    error(f"unsupported operation {name}")
