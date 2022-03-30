from .types.datapack import DataPack, DataPackFunction
from .types.program import Program
from .types.environment import Environment
from .types.expression import Expression

# === Global variables ===

debug = False

# === Helper functions ===
def generateExpression(exp: Expression):
	match exp.type:
		case "Expression":
			return ""

def generateProgram(program: Program, env: Environment) -> DataPack:
	pack = DataPack()
	main = DataPackFunction("main", [])
	# program body is the main function
	for exp in program.body:
		main.commands.append(generateExpression(exp))
	return pack


def generate(ast, _debug: bool = False) -> DataPack:
	global debug
	debug = _debug
	return generateProgram(ast, Environment.globalEnv())
