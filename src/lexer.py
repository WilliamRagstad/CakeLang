from io import TextIOWrapper


def tokenize(filepath: str) -> list:
    tokens = []
    with open(filepath, 'r') as f:
        lineNr = 1
        colNr = 0
        readNext = True
        # Find tokens
        c = None
        while True:
            if readNext:
                c = f.read(1)
            readNext = True
            colNr += 1
            if not c:
                break # End of file
            if c == ' ' or c == '\t':
                continue
            if c == '\n':
                lineNr += 1
                colNr = 0
                continue
            # If c is a digit, read until non-digit
            if c.isdigit():
                t = read_number(c, f, lineNr, colNr)
                tokens.append(t)
                c = t['next']
                readNext = False
                continue
            elif c.isalpha():
                t = read_identifier(c, f, lineNr, colNr)
                tokens.append(t)
                c = t['next']
                readNext = False
                continue
            elif c == '"':
                t = read_string(f, lineNr, colNr)
                tokens.append(t)
                continue
            elif c in ['+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', '^', '~', '?']:
                tokens.append({
                    'type': 'Operator',
                    'value': c,
                    'line': lineNr,
                    'column': colNr
                })
                continue
            elif c in ['(', ')', '{', '}', '[', ']', ';', ':', ',']:
                tokens.append({
                    'type': 'Separator',
                    'value': c,
                    'line': lineNr,
                    'column': colNr
                })
                continue
            elif c == '#':
                t = read_comment(f, lineNr, colNr)
                tokens.append(t)
                continue
            else:
                raise Exception(f"Unexpected character '{c}' at line {lineNr} column {colNr}")
    return tokens   


def read_number(first: str, f: TextIOWrapper, line: int, column: int):
    number = first
    c = f.read(1)
    while c.isdigit():
        number += c
        c = f.read(1)
    return {
        'type': 'Number',
        'value': int(number),
        'next': c,
        'line': line,
        'column': column
    }

def read_identifier(first: str, f: TextIOWrapper, line: int, column: int):
    identifier = first
    c = f.read(1)
    while c.isalpha() or c.isdigit() or c == '_':
        identifier += c
        c = f.read(1)
    if identifier in ['true', 'false']:
        return {
            'type': 'Boolean',
            'value': identifier == 'true',
            'next': c,
            'line': line,
            'column': column
        }
    elif identifier in ['if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new', 'typeof', 'in', 'of']:
        return {
            'type': 'Keyword',
            'value': identifier,
            'next': c,
            'line': line,
            'column': column
        }
    else: return {
        'type': 'Identifier',
        'value': identifier,
        'next': c,
        'line': line,
        'column': column
    }

def read_string(f: TextIOWrapper, line: int, column: int):
    string = ''
    c = f.read(1)
    while c != '"':
        string += c
        c = f.read(1)
    return {
        'type': 'String',
        'value': string,
        'line': line,
        'column': column
    }

def read_comment(f: TextIOWrapper, line: int, column: int):
    comment = ''
    c = f.read(1)
    while c != '\n':
        comment += c
        c = f.read(1)
    return {
        'type': 'Comment',
        'value': comment,
        'line': line,
        'column': column
    }