class CakeError(Exception):
	def __init__(self, message, filepath):
		super().__init__(message)
		self.filepath = filepath

class CakeSyntaxError(CakeError):
	pass

class CakeSemanticError(CakeError):
	pass

class CakeTypeError(CakeError):
	pass

class CakeGenerateError(CakeError):
	pass
