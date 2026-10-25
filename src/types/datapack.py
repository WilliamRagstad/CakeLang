"""Minecraft Java 1.20.4 pack model and filesystem output."""
from dataclasses import dataclass
from pathlib import Path
import json
import re
import tempfile
import shutil

@dataclass
class DataPack:
    namespace: str
    functions: dict[str, list[str]]

    def files(self):
        if not re.fullmatch(r"[a-z0-9_][a-z0-9_.-]*", self.namespace):
            raise ValueError("namespace must use lowercase letters, digits, _, . or -")
        files = {
            "pack.mcmeta": json.dumps({"pack": {
                "pack_format": 26, "description": "Cake pack for Minecraft Java 1.20.4"
            }}, indent=2) + "\n"
        }
        for name, commands in self.functions.items():
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
                raise ValueError(f"invalid function name: {name!r}")
            files[f"data/{self.namespace}/functions/{name}.mcfunction"] = "".join(
                command + "\n" for command in commands)
        for hook in ("load", "tick"):
            if hook in self.functions:
                files[f"data/minecraft/tags/functions/{hook}.json"] = json.dumps(
                    {"values": [f"{self.namespace}:{hook}"]}, indent=2) + "\n"
        return files

    def write(self, destination):
        files = self.files()
        destination = Path(destination)
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"output already exists: {destination}; choose a new directory")
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".cake-", dir=destination.parent))
        try:
            for name, content in files.items():
                path = staging / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
            staging.rename(destination)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        return destination
