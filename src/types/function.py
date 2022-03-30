from ..util import indent
from .expression import Expression


class FunctionCallExpression(Expression):
	def __init__(self, _name: str, _args: list[Expression], _line: int, _column: int, _lineEnd: int, _columnEnd: int):
		super().__init__("FunctionCallExpression", None, _line, _column, _lineEnd, _columnEnd)
		self.name = _name
		self.args = _args

	def toString(self, indentation):
		i = indent(indentation)
		s = f"{i}{self.type}('{self.name}', \n"
		for arg in self.args:
			s += f"{arg.toString(indentation + 1)},\n"
		s += i + ")"
		return s

	def __str__(self):
		return self.toString(0)