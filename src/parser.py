from lib2to3.pgen2 import token
from tracemalloc import start

# === Global variables ===

tokens = None
currentIndex = 0

# === Helper functions ===

def error(message: str, token: dict):
    raise Exception(f"{message} at line {token['line']}:{token['column']} to {token['lineEnd']}:{token['columnEnd']}.")

def errorExpected(what, token: dict):
    error(f"Expected {what}, but got '{token['value']}' of type {token['type']}", token)

def peekToken(offset=0, _acc=0) -> dict:
    global currentIndex, tokens
    if currentIndex + _acc + offset >= len(tokens):
        return None
    t = tokens[currentIndex + _acc + offset]
    if t["type"] == "Comment":
        return peekToken(offset, _acc + 1)
    return t

def getToken() -> dict:
    global currentIndex, tokens
    if currentIndex >= len(tokens):
        return None
    t = tokens[currentIndex]
    while t["type"] == "Comment":
        currentIndex += 1
        t = tokens[currentIndex]
    currentIndex += 1
    return t

def expectNext(type, value = None) -> None:
    t = getToken()
    if t["type"] != type:
        errorExpected(type, t)
    if value != None and t["value"] != value:
        errorExpected(value, t)
    return None

def checkNext(type, value = None) -> bool:
    t = peekToken()
    if t["type"] != type:
        return False
    if value != None and t["value"] != value:
        return False
    return True

# === Parsing ===

def parse_expression():
    t = getToken()
    print(t)
    lhs = None
    if t["type"] == "Separator" and t["value"] == "(":
        expr = parse_expression()
        expectNext("Separator", ")")
        lhs = expr
    elif t["type"] == "Identifier":
        nt = peekToken()
        if nt["type"] == "Separator" and nt["value"] == "(":
            lhs = parse_function_call(t)
        else:
            lhs = {
                "type": "IdentifierExpression",
                "value": t["value"],
                "line": t["line"],
                "column": t["column"],
                "lineEnd": t["lineEnd"],
                "columnEnd": t["columnEnd"]
            }
    elif t["type"] == "String":
        lhs =  {
            "type": "StringExpression",
            "value": t["value"],
            "line": t["line"],
            "column": t["column"],
            "lineEnd": t["lineEnd"],
            "columnEnd": t["columnEnd"]
        }
    elif t["type"] == "Number":
        lhs =  {
            "type": "NumberExpression",
            "value": t["value"],
            "line": t["line"],
            "column": t["column"],
            "lineEnd": t["lineEnd"],
            "columnEnd": t["columnEnd"]
        }
    else:
        errorExpected("expression", t)
    
    # Check for infix operators
    nt = peekToken()
    if nt["type"] == "Operator":
        getToken() # Consume the operator
        rhs = parse_expression()
        # print(lhs, nt, rhs)
        if nt["value"] == "=":
            lhs = {
                "type": "AssignmentExpression",
                "left": lhs,
                "right": rhs,
                "line": lhs["line"],
                "column": lhs["column"],
                "lineEnd": rhs["lineEnd"],
                "columnEnd": rhs["columnEnd"]
            }
        elif nt["value"] == ":":
            lhs = {
                "type": "MemberExpression",
                "lhs": lhs,
                "rhs": rhs,
                "line": lhs["line"],
                "column": lhs["column"],
                "lineEnd": rhs["lineEnd"],
                "columnEnd": rhs["columnEnd"]
            }
        else:
            lhs = {
                "type": "BinaryExpression",
                "operator": nt["value"],
                "lhs": lhs,
                "rhs": rhs,
                "line": lhs["line"],
                "column": lhs["column"],
                "lineEnd": rhs["lineEnd"],
                "columnEnd": rhs["columnEnd"]
            }
    else:
        print(f"parse_expression: no infix operator: {nt}")
    return lhs

def parse_function_call(startToken) -> dict:
    args = []
    while True:
        print(f"parse_function_call loop: {startToken['value']}")
        if checkNext("Separator", ")"):
            break
        args.append(parse_expression())
        print(f"parse_function_call peek: {startToken['value']}", peekToken())
        if checkNext("Separator", ","):
            getToken() # Consume the comma
    close = getToken()
    return {
        "type": "FunctionCall",
        "name": startToken["value"],
        "args": args,
        "line": startToken["line"],
        "column": startToken["column"],
        "lineEnd": close["lineEnd"],
        "columnEnd": close["columnEnd"]
    }

def parse_statement():
    t = getToken()
    if t["type"] == "Keyword" and t["value"] == "if":
        return parse_if_statement()
    elif t["type"] == "Keyword" and t["value"] == "while":
        return parse_while_statement()
    elif t["type"] == "Identifier":
        nt = peekToken()
        if nt["type"] == "Separator" and nt["value"] == "(":
            return parse_function_call(t)
        else:
            return parse_assignment_statement(t)
    else:
        errorExpected("statement", t)

def parse(_tokens: list) -> dict:
    global currentIndex, tokens
    tokens = _tokens
    currentIndex = 0
    body = []
    while currentIndex < len(tokens):
        t = getToken()
        nt = peekToken()
        # Function call
        if (t["type"] == "Identifier" and
           nt["type"] == "Separator" and
           nt["value"] == "("):
           body.append(parse_function_call(t))
           continue
        else:
            errorExpected("function call", t)

    return {
        'type': 'Program',
        'body': body,
        'lines': tokens[-1]['lineEnd']
    }