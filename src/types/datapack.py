class DataPackFunction():
	def __init__(self, name: str, args: list, commands: list[str] = []):
		self.name = name
		self.args = args
		self.commands = commands

class DataPack():
	"""
	Compiled data pack representation.
	"""
	def __init__(self) -> None:
		self.functions: list[DataPackFunction] = []