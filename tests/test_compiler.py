import unittest
from src.lexer import lex
from src.parser import parse
from src.checker import check
from src.types.error import CakeError

def analyze(text):
    program = parse(lex(text, "test.cake"), "test.cake")
    check(program, "test.cake")
    return program

class CompilerTests(unittest.TestCase):
    def test_supported_and_reentrant(self):
        text = '# comment\nsay("hello"); function greet() { say("world") } call("greet")'
        self.assertEqual(list(analyze(text).functions), ["main", "greet"])
        self.assertEqual(analyze("").functions, {"main": []})
        self.assertEqual(len(analyze(text).functions["main"]), 2)

    def test_errors_have_locations(self):
        for text in ['say("oops', 'say(', 'say("a",)', 'function f() {', 'say("a") + 1',
                     'import missing from minecraft', 'while(true) {}', 'x = 1',
                     'macro f() {}', 'unknown("x")', 'call("missing")',
                     'command("/say hi")', 'say("a\\nb")', 'function main() {}',
                     'function A() {}', 'say("a" "b")', 'say("\\ud800")']:
            with self.subTest(text=text), self.assertRaisesRegex(CakeError, r"test.cake:\d+:\d+:"):
                analyze(text)

    def test_line_column(self):
        with self.assertRaisesRegex(CakeError, "test.cake:2:3:"):
            analyze('# comment\n  unknown()')

if __name__ == "__main__":
    unittest.main()
