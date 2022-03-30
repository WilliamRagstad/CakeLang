class CakeError(Exception):
	type = "Unknown"
	def __init__(self, message, filepath):
		super().__init__(message)
		self.filepath = filepath

class CakeSyntaxError(CakeError):
	type = "Syntax"
	pass

class CakeSemanticError(CakeError):
	type = "Semantic"
	pass

class CakeTypeError(CakeError):
	type = "Type"
	pass

class CakeGenerateError(CakeError):
	type = "Generate"
	pass
