from .expression import Expression


class OperatorExpression(Expression):
    def __init__(self, _type: str, _operator, _lhs, _rhs, _line, _column, _lineEnd, _columnEnd):
        super().__init__(_type, None, _line, _column, _lineEnd, _columnEnd)
        self.operator = _operator
        self.lhs = _lhs
        self.rhs = _rhs
