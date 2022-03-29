
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
    expectNext("Separator", "(")
    while True:
        print(f"parse_function_call loop: {startToken['value']}")
        if checkNext("Separator", ")"):
            print(f"parse_function_call: end of args")
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
        return {
            "type": "IfStatement",
            "condition": condition,
            "body": body,
            "elseIfs": elseIfs,
            "else": elseBody,
            "line": t["line"],
            "column": t["column"],
            "lineEnd": end["lineEnd"],
            "columnEnd": end["columnEnd"]
        }
    elif t["type"] == "Keyword" and t["value"] == "while":
        condition = parse_expression()
        body = parse_body()
        return {
            "type": "WhileStatement",
            "condition": condition,
            "body": body,
            "line": t["line"],
            "column": t["column"],
            "lineEnd": body["lineEnd"],
            "columnEnd": body["columnEnd"]
        }
    elif t["type"] == "Identifier":
        nt = peekToken()
        if nt["type"] == "Separator" and nt["value"] == "(":
            return parse_function_call(t)
        elif nt["type"] == "Separator" and nt["value"] == "=":
            getToken() # Consume the =
            rhs = parse_expression()
            return {
                "type": "AssignmentStatement",
                "name": t["value"],
                "value": rhs,
                "line": t["line"],
                "column": t["column"],
                "lineEnd": rhs["lineEnd"],
                "columnEnd": rhs["columnEnd"]
            }
    # Else always throws an error
    errorExpected("statement", t)

def parse(_tokens: list) -> dict:
    global currentIndex, tokens
    tokens = _tokens
    currentIndex = 0
    body = []
    while currentIndex < len(tokens):
        body.append(parse_statement())

    return {
        'type': 'Program',
        'body': body,
        'lines': tokens[-1]['lineEnd']
    }