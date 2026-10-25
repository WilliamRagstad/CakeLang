import unittest
from pathlib import Path
from src.generator import generate
from tests.test_compiler import analyze
from src.types.error import CakeError

class AbstractionTests(unittest.TestCase):
    def compile(self, source):
        return generate(analyze(source), namespace="demo", filepath="test.cake").functions

    def test_records_lists_generic_functions_and_arithmetic(self):
        source = """
        def double(value) { return value * 2; }
        def recipe(id, duration) {
            result = { kind: id, duration: double(duration), amplifier: 1 };
            return result;
        }
        def apply(target, items) {
            forEach(items, item, {
                effect(target, item.kind, item.duration, item.amplifier);
            });
        }
        boosts = [recipe(minecraft:levitation, 2 + 1), recipe(minecraft:speed, 5)];
        apply(@s, boosts);
        """
        self.assertEqual(self.compile(source)["main"], [
            "effect give @s minecraft:levitation 6 1 true",
            "effect give @s minecraft:speed 10 1 true",
        ])

    def test_lexical_scope_and_independent_instantiations(self):
        source = """
        duration = 3;
        def boost(target, seconds) { effect(target, minecraft:speed, seconds); }
        def defaultBoost(target) { effect(target, minecraft:speed, duration); }
        def caller(duration) { defaultBoost(@s); boost(@s, duration); }
        caller(20);
        caller(30);
        """
        self.assertEqual(self.compile(source)["main"], [
            "effect give @s minecraft:speed 3 0 true", "effect give @s minecraft:speed 20 0 true",
            "effect give @s minecraft:speed 3 0 true", "effect give @s minecraft:speed 30 0 true",
        ])

    def test_execution_context_binds_random_target_once(self):
        source = """
        as(r(radius<=10), {
            effect(@s, minecraft:levitation, 3);
            effect(@s, minecraft:slow_falling, 20);
        });
        """
        functions = self.compile(source)
        self.assertEqual(functions["main"], ["execute as @r[distance=..10] at @s run function demo:__cake_1"])
        self.assertEqual(functions["__cake_1"], [
            "effect give @s minecraft:levitation 3 0 true",
            "effect give @s minecraft:slow_falling 20 0 true",
        ])

    def test_named_arguments_and_resource_types(self):
        self.assertEqual(self.compile('effect(@s, minecraft:speed, amplifier=2, duration=5, hideParticles=false);')["main"],
                         ["effect give @s minecraft:speed 5 2 false"])
        self.assertEqual(self.compile('give(@s, minecraft:arrow, count=8 * 2);')["main"],
                         ["give @s minecraft:arrow 16"])

    def test_scalar_return_and_empty_procedure(self):
        self.assertEqual(self.compile('def identity(x) { x } def nothing() {} nothing(); say(identity("hello"));')["main"],
                         ["say hello"])

    def test_examples_need_no_raw_commands(self):
        for path in Path("examples").glob("*.cake"):
            self.assertNotIn("command(", path.read_text(), path)

    def test_invalid_types_scope_and_unsupported_constructs(self):
        cases = [
            'effect(@s, "minecraft:speed", 3)',
            'effect(@s, minecraft:speed, true)',
            'effect(@s, minecraft:speed, 0)',
            'effect(@s, minecraft:speed, 2.5)',
            'effect(@s, minecraft:speed, 3, 256)',
            'effect(@s, minecraft:speed, 3, hideParticles=1)',
            'effect(@s, minecraft:speed, 3, duration=4)',
            'effect(@s, minecraft:speed, nope=4)',
            'effect(@s, minecraft:speed, duration=3, 1)',
            'give("someone", minecraft:arrow)',
            'give(@s, minecraft:arrow, -1)',
            'tag(@s, "a b")',
            'kill(e(type="minecraft:husk"))',
            'x = { a: 1, a: 2 };',
            'x = { a: 1 }; give(@s, minecraft:arrow, x.b);',
            'x = 1; x = 2;',
            'x = 1 / 0;',
            'x = true + 1;',
            'def action() { say("hi"); } x = action();',
            'def identity(x) { return x; say("unreachable"); }',
            'return 1;',
            'forEach(3, value, {say("bad");});',
            'forEach([], value, {unknown();});',
            'forEach([1], value, {}); give(@s, minecraft:arrow, value);',
            'as("a", {say("bad");});',
            'function __cake_1() {}',
            'def unused(x) { missing(x); }',
            'def recursive(x) { recursive(x); }',
            'summon(minecraft:husk, {x:0, y:0, z:1}, {unknown: true});',
            'summon(minecraft:husk, {x:0, y:0, z:1}, {noAI: 1});',
            'particle(@s, minecraft:end_rod, {x:0,y:0,z:0}, {x:-1,y:0,z:0});',
            'give(@, minecraft:arrow);',
            'x = [1, 2;',
        ]
        for source in cases:
            with self.subTest(source=source), self.assertRaisesRegex(CakeError, r"test.cake:\d+:\d+:"):
                self.compile(source)

    def test_expansion_limits_and_deep_expression_errors(self):
        self.assertEqual(len(self.compile('repeat(1000, { repeat(10, { say("hi"); }); });')["main"]), 10000)
        values = ",".join(["1"] * 100)
        sources = [
            'repeat(1001, { repeat(10, { say("hi"); }); });',
            'x = ' + '+'.join(["1"] * 100) + ';',
            'values = [' + values + ']; def nothing() {} '
            'forEach(values, i, {forEach(values, j, {forEach(values, k, {nothing();});});});',
        ]
        for source in sources:
            with self.subTest(source=source[:80]), self.assertRaisesRegex(CakeError, r"test.cake:\d+:\d+:"):
                self.compile(source)
