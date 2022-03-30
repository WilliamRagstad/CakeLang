# Static analyzer and type checker
from .types.program import Program
from .types.environment import Environment

# === Global variables ===

filepath = None
debug = False

def check(program: Program, _filepath: str, _debug: bool = False):
	global debug, filepath
	debug = _debug
	filepath = _filepath
	env = Environment.globalEnv()
	pass