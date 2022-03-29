from glob import glob
from io import TextIOWrapper

# === Global variables ===

line = 1
column = 0
tokens = []

# === Helper functions ===

def next(file: TextIOWrapper):
    global line, column
    c = file.read(1)
    column += 1
    if c == '\n':
        line += 1
        column = 0
    return c


# === Lexing ===

def read_number(first: str, f: TextIOWrapper):
    global line, column
    startLine = line
    startColumn = column
    number = first
    c = next(f)
    while c.isdigit():
        number += c
        c = next(f)
    return {
        'type': 'Number',
        'value': int(number),
        'next': c,
        'line': startLine,
        'column': startColumn,
        'lineEnd': line,
        'columnEnd': column
    }

def read_identifier(first: str, f: TextIOWrapper):
    global line, column
    startLine = line
    startColumn = column
    identifier = first
    c = next(f)
    while c.isalpha() or c.isdigit() or c == '_':
        identifier += c
        c = next(f)
    if identifier in ['true', 'false']:
        return {
            'type': 'Boolean',
            'value': identifier == 'true',
            'next': c,
            'line': startLine,
            'column': startColumn,
            'lineEnd': line,
            'columnEnd': column
        }
    elif identifier in ['macro', 'function', 'comp', 'if', 'else', 'while', 'for', 'import', 'from', 'as', 'repeat', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new', 'typeof', 'in', 'of']:
        return {
            'type': 'Keyword',
            'value': identifier,
            'next': c,
            'line': startLine,
            'column': startColumn,
            'lineEnd': line,
            'columnEnd': column
        }
    else: return {
        'type': 'Identifier',
        'value': identifier,
        'next': c,
        'line': startLine,
        'column': startColumn,
        'lineEnd': line,
        'columnEnd': column
    }

def read_string(f: TextIOWrapper):
    global line, column
    startLine = line
    startColumn = column
    string = ''
    c = next(f)
    while c != '"':
        if c == '\n':
            raise Exception(f"Unexpected newline in string at line {line} column {column}")
        string += c
        c = next(f)
    return {
        'type': 'String',
        'value': string,
        'line': startLine,
        'column': startColumn,
        'lineEnd': line,
        'columnEnd': column
    }

def read_comment(f: TextIOWrapper):
    global line, column
    startLine = line
    startColumn = column
    comment = ''
    c = next(f)
    while c != '\n':
        comment += c
        c = next(f)
    return {
        'type': 'Comment',
        'value': comment,
        'line': startLine,
        'column': startColumn,
        'lineEnd': line,
        'columnEnd': column
    }
    
def tokenize(filepath: str) -> list:
    global line, column, tokens
    tokens = []
    line = 1
    column = 0
    with open(filepath, 'r') as f:
        readNext = True
        c = None
        while True:
            if readNext:
                c = next(f)
            readNext = True
            if not c:
                break # End of file
            if c in [' ', '\t', '\r', '\n']:
                continue
            # If c is a digit, read until non-digit
            if c.isdigit():
                t = read_number(c, f)
                tokens.append(t)
                c = t['next']
                readNext = False
                continue
            elif c.isalpha():
                t = read_identifier(c, f)
                tokens.append(t)
                c = t['next']
                readNext = False
                continue
            elif c == '"':
                t = read_string(f)
                tokens.append(t)
                continue
            elif c in ['+', '-', '*', '/', '%', '=', '!', '<', '>', ':', '&', '|', '^']:
                tokens.append({
                    'type': 'Operator',
                    'value': c,
                    'line': line,
                    'column': column,
                    'lineEnd': line,
                    'columnEnd': column + 1
                })
                continue
            elif c in ['(', ')', '{', '}', '[', ']', ',']:
                tokens.append({
                    'type': 'Separator',
                    'value': c,
                    'line': line,
                    'column': column,
                    'lineEnd': line,
                    'columnEnd': column + 1
                })
                continue
            elif c == '#':
                t = read_comment(f)
                tokens.append(t)
                continue
            else:
                raise Exception(f"Unexpected character '{c}' at line {line} column {column}-{column + 1}")
    return tokens   

