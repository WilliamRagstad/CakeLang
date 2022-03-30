from typing import Callable
from .function import FunctionCallExpression

class EnvEntry():
	def __init__(self, type: str):
		self.type = type
class EnvFunction(EnvEntry):
	def __init__(self, generator: Callable[[FunctionCallExpression], str]):
		super().__init__("Function")
		self.generator = generator

# === Environment ===
class Environment():
	def __init__(self, name, parent = None):
		self.parent = parent
		self.name = name
		self.values = {}

	@staticmethod
	def globalEnv():
		return Environment("global")

	def lookup(self, identifier) -> EnvEntry | None:
		if identifier in self.values:
			return self.values[identifier]
		elif self.parent != None:
			return self.parent.find(identifier)
		else:
			return None

	def set(self, identifier, value: EnvEntry):
		self.values[identifier] = value

	def derive(self, name):
		return Environment(name, self)
