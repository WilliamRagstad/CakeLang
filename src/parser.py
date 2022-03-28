from lib2to3.pgen2 import token
from tracemalloc import start

tokens = None
currentIndex = 0
def parse(_tokens: list) -> dict:
    global currentIndex, tokens
    tokens = _tokens
    currentIndex = 0
    body = []
    while currentIndex < len(tokens):
        ct = tokens[currentIndex]
        nt = tokens[currentIndex + 1]
        i += 1
        if (ct["type"] == "Identifier" and
           nt["type"] == "Separator" and
           nt["value"] == "("):
           # Function call
           fc = parse_function_call(tokens, i + 1, ct["value"])
           body.append(fc)
           i = fc["endIndex"]
           continue

        
    return {
        'type': 'Program',
        'body': body
    }

def expectNext(tokens, currentIndex, type, value):
    if tokens[currentIndex]["type"] != type:
        raise Exception(f"Expected {type}, got {tokens[currentIndex]['type']}")
    if tokens[currentIndex]["value"] != value:
        raise Exception(f"Expected {value}, got {tokens[currentIndex]['value']}")
    return currentIndex + 1

def checkNext(tokens, currentIndex, type, value):
    if tokens[currentIndex]["type"] != type:
        return False
    if tokens[currentIndex]["value"] != value:
        return False
    return True

def parse_expression(tokens, startIndex):
    currentIndex = startIndex
    ct = tokens[currentIndex]
    if ct["type"] not in ["Identifier", "Number", "String"]:
        raise Exception(f"Expected expression, got {ct['type']}")
    lhs = ct

def parse_function_call(tokens, startIndex, functionName) -> dict:
    args = []
    currentIndex = startIndex
    while True:
        if checkNext(tokens, currentIndex, "Separator", ")"):
            break
        args.append(parse_expression(tokens, currentIndex))
        currentIndex = args[-1]["endIndex"]
        if checkNext(tokens, currentIndex, "Separator", ","):
            currentIndex += 1

    return {
        "type": "FunctionCall",
        "name": functionName,
        "args": args,
        "startIndex": startIndex,
        "endIndex": currentIndex
    }