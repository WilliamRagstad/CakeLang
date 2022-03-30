
from .types.environment import Environment
from .types.expression import Expression

# === Global variables ===

debug = False

# === Helper functions ===
def generateExperssion(exp: Expression):
	match exp.type:
		case "Expression":
			return ""

def generate(ast, _debug: bool = False):
	global debug
	debug = _debug
	env = Environment.globalEnv()
	functions = []
	# program body is the main function
