class Expression():
    def __init__(self, _type: str, _value, _line, _column, _lineEnd, _columnEnd):
        self.type = _type
        self.value = _value
        self.line = _line
        self.column = _column
        self.lineEnd = _lineEnd
        self.columnEnd = _columnEnd

        