# === Global variables ===

from .types.expression import Expression
from .types.function import FunctionCallExpression
from .types.statements import AssignmentStatement, IfStatement, ImportStatement, WhileStatement
from .types.operator import OperatorExpression
from .types.program import Program


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

def expectNext(type, value = None) -> dict:
    t = getToken()
    if t["type"] != type:
        errorExpected(type, t)
    if value != None and t["value"] != value:
        errorExpected(value, t)
    return t

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
    # print(t)
    lhs = None
    if t["type"] == "Separator" and t["value"] == "(":
        expr: Expression = parse_expression()
        expectNext("Separator", ")")
        lhs = expr
    elif t["type"] == "Identifier":
        nt = peekToken()
        if nt["type"] == "Separator" and nt["value"] == "(":
            lhs = parse_function_call(t)
        else:
            lhs = Expression("IdentifierExpression", t["value"], t["line"], t["column"], t["lineEnd"], t["columnEnd"])
    elif t["type"] == "String":
        lhs =  Expression("StringExpression", t["value"], t["line"], t["column"], t["lineEnd"], t["columnEnd"])
    elif t["type"] == "Number":
        lhs =  Expression("NumberExpression", t["value"], t["line"], t["column"], t["lineEnd"], t["columnEnd"])
    else:
        errorExpected("expression", t)

    # Check for infix operators
    nt = peekToken()
    if nt["type"] == "Operator":
        getToken() # Consume the operator
        rhs = parse_expression()
        # print(lhs, nt, rhs)
        if nt["value"] == "=":
            lhs = OperatorExpression("AssignmentExpression", None, lhs, rhs, lhs["line"], lhs["column"], rhs["lineEnd"], rhs["columnEnd"])
        elif nt["value"] == ":":
            lhs = OperatorExpression("MemberExpression", None, lhs, rhs, lhs["line"], lhs["column"], rhs["lineEnd"], rhs["columnEnd"])
        else:
            lhs = OperatorExpression("BinaryExpression", nt["value"], lhs, rhs, lhs["line"], lhs["column"], rhs["lineEnd"], rhs["columnEnd"])
    # else:
        # print(f"parse_expression: no infix operator: {nt}")
    return lhs

def parse_function_call(startToken):
    args = []
    expectNext("Separator", "(")
    while True:
        # print(f"parse_function_call loop: {startToken['value']}")
        if checkNext("Separator", ")"):
            # print(f"parse_function_call: end of args")
            break
        args.append(parse_expression())
        # print(f"parse_function_call peek: {startToken['value']}", peekToken())
        if checkNext("Separator", ","):
            getToken() # Consume the comma
    close = getToken()
    return FunctionCallExpression(startToken["value"], args, startToken["line"], startToken["column"], close["lineEnd"], close["columnEnd"])

def parse_block():
    statements = []
    start = expectNext("Separator", "{")
    while not checkNext("Separator", "}"):
        statements.append(parse_statement())
    end = getToken() # Consume the closing brace
    return {
        "type": "BlockStatement",
        "statements": statements,
        "line": start["line"],
        "column": start["column"],
        "lineEnd": end["lineEnd"],
        "columnEnd": end["columnEnd"]
    }

def parse_body():
    if checkNext("Separator", "{"):
        return parse_block()
    else:
        return parse_statement()

def parse_statement():
    t = getToken()
    if t["type"] == "Keyword" and t["value"] == "if":
        condition = parse_expression()
        body = parse_body()
        elseIfs = []
        elseBody = None
        while checkNext("Keyword", "else"):
            getToken() # Consume the else keyword
            if checkNext("Separator", "if"):
                getToken() # Consume the if keyword
                elseIfs.append(parse_body())
            else:
                elseBody = parse_body()
                break
        end  = body
        if elseBody != None:
            end = elseBody
        elif len(elseIfs) > 0:
            end = elseIfs[-1]
        return IfStatement(condition, body, elseIfs, elseBody, t["line"], t["column"], end["lineEnd"], end["columnEnd"])
    elif t["type"] == "Keyword" and t["value"] == "while":
        condition = parse_expression()
        body = parse_body()
        return WhileStatement(condition, body, t["line"], t["column"], body["lineEnd"], body["columnEnd"])
    elif t["type"] == "Identifier":
        nt = peekToken()
        if nt["type"] == "Separator" and nt["value"] == "(":
            return parse_function_call(t)
        elif nt["type"] == "Separator" and nt["value"] == "=":
            getToken() # Consume the =
            rhs = parse_expression()
            return AssignmentStatement(t["value"], rhs, t["line"], t["column"], rhs["lineEnd"], rhs["columnEnd"])
    # Else always throws an error
    errorExpected("statement", t)

def parse_import():
    start = expectNext("Keyword", "import")
    subjects = []
    while not checkNext("Keyword", "from"):
        subjects.append(expectNext("Identifier"))
        if checkNext("Separator", ","):
            getToken()
    getToken() # Consume the from keyword
    module = expectNext("Identifier")
    return ImportStatement(module, subjects, start["line"], start["column"], module["lineEnd"], module["columnEnd"])

def parse(_tokens: list) -> dict:
    global currentIndex, tokens
    tokens = _tokens
    currentIndex = 0
    imports = []
    body = []
    while currentIndex < len(tokens):
        if checkNext("Keyword", "import"):
            imports.append(parse_import())
        body.append(parse_statement())
    return Program(imports, body, tokens[-1]["lineEnd"])