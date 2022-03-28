from lib2to3.pgen2 import token
from tracemalloc import start

# === Global variables ===

tokens = None
currentIndex = 0

# === Helper functions ===

def error(message: str, token: dict):
    raise Exception(f"{message} at line {token['line']}:{token['column']} to {token['lineEnd']}:{token['columnEnd']}.")

def errorExpected(what, got, token: dict):
    error(f"Expected {what}, got {got}", token)

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
        errorExpected(type, t["type"], t)
    if value != None and t["value"] != value:
        errorExpected(value, t["value"], t)
    return None

def checkNext(type, value = None) -> bool:
    t = getToken()
    if t["type"] != type:
        return False
    if value != None and t["value"] != value:
        return False
    return True

# === Parsing ===

def parse_expression():
    t = getToken()
    if t["type"] not in ["Identifier", "Number", "String"]:
        errorExpected("expression", t["type"], t)
    return t

def parse_function_call(functionName) -> dict:
    args = []
    while True:
        if checkNext("Separator", ")"):
            break
        args.append(parse_expression())
        if checkNext("Separator", ","):
            getToken() # Consume the comma
    return {
        "type": "FunctionCall",
        "name": functionName,
        "args": args,
    }

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
           body.append(parse_function_call(t["value"]))
           continue
        else:
            errorExpected("function call", t["type"], t)

    return {
        'type': 'Program',
        'body': body
    }