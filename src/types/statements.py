from types.expression import Expression


class ImportStatement(Expression):
    def __init__(self, _module, _subjects, _line, _column, _lineEnd, _columnEnd):
        super().__init__("ImportStatement", None, _line, _column, _lineEnd, _columnEnd)
        self.module = _module
        self.subjects = _subjects
        self.body = None
        self.env = None

class IfStatement(Expression):
    def __init__(self, _condition, _body, _elseIfs, _else, _line, _column, _lineEnd, _columnEnd):
        super().__init__("IfStatement", None, _line, _column, _lineEnd, _columnEnd)
        self.condition = _condition
        self.body = _body
        self.elseIfs = _elseIfs
        self.elseBody = _else

class WhileStatement(Expression):
    def __init__(self, _condition, _body, _line, _column, _lineEnd, _columnEnd):
        super().__init__("WhileStatement", None, _line, _column, _lineEnd, _columnEnd)
        self.condition = _condition
        self.body = _body

class AssignmentStatement(Expression):
    def __init__(self, _name, _value, _line, _column, _lineEnd, _columnEnd):
        super().__init__("AssignmentStatement", None, _line, _column, _lineEnd, _columnEnd)
        self.name = _name
        self.value = _value