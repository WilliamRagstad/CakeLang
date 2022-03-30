from .types.function import FunctionCallExpression
from .types.datapack import DataPack, DataPackFunction
from .types.program import Program
from .types.environment import EnvFunction, Environment
from .types.expression import Expression

# === Global variables ===

debug = False

# === Helper functions ===

def error(message: str, exp: Expression):
    raise Exception(f"{message} at line {exp.line}:{exp.column} to {exp.lineEnd}:{exp.columnEnd}.")

def generateFunctionCall(f: FunctionCallExpression, env: Environment) -> str:
	value = env.lookup(f.name)
	if value == None:
		error(f"Function {f.name} not found.", f)
	elif value.type == "Function" and isinstance(value, EnvFunction):
		return value.generator(f)
	else:
		error(f"{f.name} is not a function.", f)

def generateExpression(exp: Expression, env: Environment) -> str:
	match exp.type:
		case "FunctionCallExpression":
			return generateFunctionCall(exp, env)

def generateProgram(program: Program, env: Environment) -> DataPack:
	pack = DataPack()
	main = DataPackFunction("main", [])
	# program body is the main function
	for exp in program.body:
		main.commands.append(generateExpression(exp, env))
	pack.functions.append(main)
	return pack

def generate(ast, env: Environment, _debug: bool = False) -> DataPack:
	global debug
	debug = _debug
	return generateProgram(ast, env)
