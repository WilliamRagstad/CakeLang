from pathlib import Path
import unittest
from src.generator import generate
from src.types.error import CakeError
from tests.test_compiler import analyze

class LanguageTests(unittest.TestCase):
    def commands(self, source):
        return generate(analyze(source), filepath="test.cake").functions["main"]

    def test_exact_user_program_and_readme_macro(self):
        source = Path("examples/greet_random.cake").read_text()
        expected = 'execute as @r[type=minecraft:player,distance=..10] at @s run tellraw @a [{"text":"Hello "},{"selector":"@s"},{"text":"!"}]'
        self.assertEqual(self.commands(source), [expected] * 3)
        self.assertEqual(self.commands(source.replace("def ", "macro ")), [expected] * 3)
        self.assertEqual(self.commands(source.replace("import player from minecraft", "").replace("type=player", "type=minecraft:player")), [expected] * 3)

    def test_repeat_and_parameter_substitution(self):
        self.assertEqual(self.commands('repeat(2, { repeat(2, { say("hi"); }); });'), ["say hi"] * 4)
        self.assertEqual(self.commands('repeat(0, { say("hi"); });'), [])
        commands = self.commands('def near(n) { r(radius<=n) } say(near(2.5), "Hi"); say(near(20), "Bye");')
        self.assertIn("distance=..2.5", commands[0])
        self.assertIn("distance=..20", commands[1])
        self.assertEqual(self.commands('def outer(n) { inner(n) } def inner(n) { r(radius<=n) } say(outer(3), "ok")'),
                         ['execute as @r[distance=..3] at @s run tellraw @a [{"text":"ok"}]'])

    def test_invalid_constructs(self):
        cases = [
            'import cow from minecraft', 'import player from other',
            'say(r(type=player), "hello")', 'say(r(type="player"), "hello")',
            'say(r(radius="1"), "hello")', 'say(r(radius<=1,radius<=2), "hello")',
            'say(r(foo=1), "hello")', 'say(1, "hello")',
            'def near(n) { r(radius<=n) } say(near(), "hello")',
            'def near(n) { r(radius<=n) } say(near("2"), "hello")',
            'def near(n) { r(radius<=missing) }',
            'def near(n,n) { r() }', 'def say(n) { r() }',
            'def near(n) { unknown() }', 'def near(n) { missing }',
            'def outer(n) { inner(n) } def inner(n) { outer(n) }',
            'repeat(1.5, {say("hi")})', 'repeat(1025, {say("hi")})',
            'repeat(2, "hi")', 'repeat(0, {unknown()})',
            'repeat(1024, {repeat(1024, {say("hi")})})',
            'say(r(), "Hello {@p}")', 'function f() { def g(n) { r() } }',
            'repeat(3, { say(r(), "hi");', 'say(r(radius<=), "hi")',
        ]
        for source in cases:
            with self.subTest(source=source), self.assertRaisesRegex(CakeError, r"test.cake:\d+:\d+:"):
                self.commands(source)
