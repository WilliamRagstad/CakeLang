
from .types.environment import Environment
from .types.expression import Expression

# === Helper functions ===
def generateExperssion(exp: Expression):
    match exp.type:
        case "Expression":
            return ""

def generate(ast):
    env = Environment.globalEnv()
    functions = []
    # program body is the main function
