from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from src.compiler import compile
from src.generator import generate
from tests.test_compiler import analyze

FIXTURES = Path(__file__).parent / "fixtures"

def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}

class GeneratorTests(unittest.TestCase):
    def test_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pack"
            compile(FIXTURES / "basic.cake", output=out, namespace="demo")
            self.assertEqual(tree(out), tree(FIXTURES / "basic"))
            before = tree(out)
            with self.assertRaisesRegex(ValueError, "already exists"):
                compile(FIXTURES / "basic.cake", output=out)
            self.assertEqual(tree(out), before)

    def test_names_and_independent_functions(self):
        for name in ["../escape", "a/b", "UPPER", "", ".", "..", "/tmp/x"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                generate(analyze('say("hi")'), namespace=name)
        pack = generate(analyze('say("one") function other() { say("two") }'))
        self.assertEqual(pack.functions, {"main": ["say one"], "other": ["say two"]})
        self.assertFalse(any("tags" in p for p in pack.files()))

    def test_cli_failure_and_lint_no_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "bad.cake"
            out = Path(tmp) / "pack"
            source.write_text('say("unterminated')
            result = subprocess.run([sys.executable, "cake.py", str(source), "-o", str(out)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn(f"{source}:1:5:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(out.exists())
            source.write_text('say("ok")')
            result = subprocess.run([sys.executable, "cake.py", "--lint", str(source), "-o", str(out)])
            self.assertEqual(result.returncode, 0)
            self.assertFalse(out.exists())
