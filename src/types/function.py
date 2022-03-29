from types.expression import Expression


class FunctionCallExpression(Expression):
    def __init__(self, _name, _args, _line, _column, _lineEnd, _columnEnd):
        super().__init__("FunctionCallExpression", None, _line, _column, _lineEnd, _columnEnd)
        self.name = _name
        self.args = _args
        self.body = None
        self.env = None