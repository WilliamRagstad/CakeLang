from termcolor import colored as c
from .types.error import CakeSemanticError
from .types.token import Token
from .types.expression import Expression
from .types.function import FunctionCallExpression
from .types.statements import AssignmentStatement, IfStatement, ImportStatement, WhileStatement
from .types.operator import OperatorExpression
from .types.program import Program

# === Global variables ===

filepath = None
tokens = None
currentIndex = 0
debug = False

# === Helper functions ===

def dprint(*args):
	global debug
	if debug: print(*args)

def error(message: str, token: Token):
	raise CakeSemanticError(f"{message} at line {token.line}:{token.column} to {token.lineEnd}:{token.columnEnd}.", filepath)

def errorExpected(what, token: Token):
	if token == None:
		raise CakeSemanticError(f"Expected {what} at end of input.", filepath)
	error(f"Expected {what}, but got '{token.value}' of type {token.type}", token)

def peekToken(offset=0) -> Token:
	global currentIndex, tokens
	if currentIndex + offset >= len(tokens):
		return None
	t = tokens[currentIndex + offset]
	if t.type == "Comment":
		return peekToken(offset + 1)
	return t

def getToken(incrIndex = True) -> Token:
	global currentIndex, tokens
	if currentIndex >= len(tokens):
		return None
	t = tokens[currentIndex]
	while t.type == "Comment":
		currentIndex += 1
		t = getToken(False)
		if t == None:
			return t
	if incrIndex:
		currentIndex += 1
	return t

def isEndOfInput():
	return peekToken() == None

def expectNext(type, value = None) -> Token:
	t = getToken()
	if t == None or t.type != type:
		errorExpected(type, t)
	if value != None and t.value != value:
		errorExpected(value, t)
	return t

def checkNext(type, value = None) -> bool:
	t = peekToken()
	if t == None or t.type != type:
		return False
	if value != None and t.value != value:
		return False
	return True

# === Parsing ===

def parse_expression():
	t = getToken()
	lhs = None
	if t.type == "Separator" and t.value == "(":
		expr: Expression = parse_expression()
		expectNext("Separator", ")")
		lhs = expr
	elif t.type == "Identifier":
		nt = peekToken()
		if nt.type == "Separator" and nt.value == "(":
			lhs = parse_function_call(t)
		else:
			lhs = Expression("IdentifierExpression", t.value, t.line, t.column, t.lineEnd, t.columnEnd)
	elif t.type == "String":
		lhs =  Expression("StringExpression", t.value, t.line, t.column, t.lineEnd, t.columnEnd)
	elif t.type == "Number":
		lhs =  Expression("NumberExpression", t.value, t.line, t.column, t.lineEnd, t.columnEnd)
	else:
		errorExpected("expression", t)

	# Check for infix operators
	nt = peekToken()
	if nt.type == "Operator":
		getToken() # Consume the operator
		rhs = parse_expression()
		if nt.value == "=":
			lhs = OperatorExpression("AssignmentExpression", None, lhs, rhs, lhs.line, lhs.column, rhs.lineEnd, rhs.columnEnd)
		elif nt.value == ":":
			lhs = OperatorExpression("MemberExpression", None, lhs, rhs, lhs.line, lhs.column, rhs.lineEnd, rhs.columnEnd)
		else:
			lhs = OperatorExpression("BinaryExpression", nt.value, lhs, rhs, lhs.line, lhs.column, rhs.lineEnd, rhs.columnEnd)
	return lhs

def parse_function_call(startToken: Token):
	args = []
	expectArg = False
	expectNext("Separator", "(")
	while True:
		if checkNext("Separator", ")"):
			if expectArg:
				errorExpected("argument", getToken())
			print(f"parse_function_call '{startToken.value}': end of arguments")
			break
		dprint(f"parse_function_call '{startToken.value}': parsing argument")
		args.append(parse_expression())
		expectArg = False
		if checkNext("Separator", ","):
			getToken() # Consume the comma
			expectArg = True
	close = getToken()
	return FunctionCallExpression(startToken.value, args, startToken.line, startToken.column, close.lineEnd, close.columnEnd)

def parse_block():
	statements = []
	start = expectNext("Separator", "{")
	while not checkNext("Separator", "}"):
		statements.append(parse_statement())
	end = getToken() # Consume the closing brace
	return {
		"type": "BlockStatement",
		"statements": statements,
		"line": start.line,
		"column": start.column,
		"lineEnd": end.lineEnd,
		"columnEnd": end.columnEnd
	}

def parse_body():
	if checkNext("Separator", "{"):
		return parse_block()
	else:
		return parse_statement()

def parse_statement():
	t = getToken()
	if t and t.type == "Keyword" and t.value == "if":
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
		return IfStatement(condition, body, elseIfs, elseBody, t.line, t.column, end.lineEnd, end.columnEnd)
	elif t and t.type == "Keyword" and t.value == "while":
		condition = parse_expression()
		body = parse_body()
		return WhileStatement(condition, body, t.line, t.column, body.lineEnd, body.columnEnd)
	elif t and t.type == "Identifier":
		nt = peekToken()
		if nt.type == "Separator" and nt.value == "(":
			return parse_function_call(t)
		elif nt.type == "Separator" and nt.value == "=":
			getToken() # Consume the =
			rhs = parse_expression()
			return AssignmentStatement(t.value, rhs, t.line, t.column, rhs.lineEnd, rhs.columnEnd)
	# Else always throws an error
	errorExpected("statement", t)

def parse_import():
	start = expectNext("Keyword", "import")
	subjects = []
	while not checkNext("Keyword", "from"):
		subjects.append(expectNext("Identifier").value)
		if checkNext("Separator", ","):
			getToken()
	getToken() # Consume the from keyword
	module = expectNext("Identifier")
	dprint(f"parse_import: {subjects} from '{module.value}'")
	return ImportStatement(module, subjects, start.line, start.column, module.lineEnd, module.columnEnd)

def parse(_tokens: list[Token], _filepath: str, _debug: bool = False) -> Program:
	global currentIndex, tokens, debug, filepath
	filepath = _filepath
	tokens = _tokens
	currentIndex = 0
	debug = _debug
	imports = []
	body = []
	dprint('>',c("Parsing...", "cyan"))
	while not isEndOfInput():
		if checkNext("Keyword", "import"):
			imports.append(parse_import())
		body.append(parse_statement())
	return Program(imports, body, tokens[-1].lineEnd)
