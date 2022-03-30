from .expression import Expression


class Program(Expression):
    def __init__(self, _imports: list, _body: list, _lines: int):
        self.type = "Program"
        self.imports = _imports
        self.body = _body
        self.lines = _lines
