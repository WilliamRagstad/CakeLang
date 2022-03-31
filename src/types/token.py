class Token():
	def __init__(self, _type: str, _value, _line: int, _column: int, _lineEnd: int, _columnEnd: int, _next: str):
		self.type = _type
		self.value = _value
		self.line = _line
		self.column = _column
		self.lineEnd = _lineEnd
		self.columnEnd = _columnEnd
		self.next = _next

	def __str__(self):
		value = f"'{self.value}'" if isinstance(self.value, str) else str(self.value)
		return self.type.ljust(10) + ' | ' + value

class OperatorToken(Token):
	def __init__(self, _subtype: str, _value, _line: int, _column: int, _lineEnd: int, _columnEnd: int):
		super().__init__('Operator', _value, _line, _column, _lineEnd, _columnEnd, None)
		self.subtype = _subtype
