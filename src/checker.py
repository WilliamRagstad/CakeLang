# Static analyzer and type checker
from .types.environment import Environment

# === Global variables ===

debug = False

def check(ast, _debug: bool = False):
	global debug
	debug = _debug
	env = Environment.globalEnv()
	pass