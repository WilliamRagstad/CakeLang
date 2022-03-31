from .expression import Expression
from ..util import indent

class OperatorExpression(Expression):
	def __init__(self, _type: str, _operator: str, _lhs: Expression, _rhs: Expression, _line, _column, _lineEnd, _columnEnd):
		super().__init__(_type, None, _line, _column, _lineEnd, _columnEnd)
		self.operator = _operator
		self.lhs = _lhs
		self.rhs = _rhs

	def toString(self, indentation):
		i = indent(indentation)
		ii = indent(indentation + 1)
		return f"{i}{self.type}(\n{self.lhs.toString(indentation + 1)},\n{ii}'{self.operator}',\n{self.rhs.toString(indentation + 1)}\n{i})"
