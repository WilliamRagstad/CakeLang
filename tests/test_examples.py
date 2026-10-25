from pathlib import Path
import tempfile
import unittest
from src.compiler import compile
from tests.test_generator import tree, FIXTURES

class ExampleTests(unittest.TestCase):
    def test_examples(self):
        for name in ("launch", "target", "trail", "greet_random"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / name
                compile(Path("examples") / f"{name}.cake", namespace=name, output=out)
                self.assertEqual(tree(out), tree(FIXTURES / name))
