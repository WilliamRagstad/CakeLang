"""Location-aware lexer for the supported Cake subset."""
from dataclasses import dataclass
from pathlib import Path
import json
import re
from .types.error import CakeSyntaxError

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int

def fail(message, token, filepath):
    raise CakeSyntaxError(f"{filepath}:{token.line}:{token.column}: {message}", filepath)

def lex(text, filepath="<string>"):
    tokens = []
    i, line, column = 0, 1, 1
    while i < len(text):
        c = text[i]
        if c.isspace():
            if c == "\n":
                line, column = line + 1, 1
            else:
                column += 1
            i += 1
            continue
        if c == "#":
            end = text.find("\n", i)
            end = len(text) if end < 0 else end
            column += end - i
            i = end
            continue
        token = Token(c, c, line, column)
        if c == '"':
            try:
                value, length = json.JSONDecoder().raw_decode(text[i:])
            except ValueError:
                fail("invalid or unterminated JSON string", token, filepath)
            tokens.append(Token("string", value, line, column))
        elif c.isascii() and c.isdigit():
            value = re.match(r"[0-9]+(?:\.[0-9]+)?", text[i:])[0]
            length = len(value)
            if length > 100:
                fail("numeric literal is too long", token, filepath)
            tokens.append(Token("number", float(value) if "." in value else int(value), line, column))
        elif text.startswith("<=", i):
            tokens.append(Token("<=", "<=", line, column))
            length = 2
        elif c.isascii() and (c.isalpha() or c == "_"):
            value = re.match(r"[A-Za-z_][A-Za-z_0-9]*", text[i:])[0]
            length = len(value)
            tokens.append(Token("name", value, line, column))
        elif c in "(){};,:=":
            tokens.append(token)
            length = 1
        else:
            fail(f"unsupported character or construct {c!r}", token, filepath)
        i += length
        column += length
    tokens.append(Token("eof", "", line, column))
    return tokens

def tokenize(filepath, debug=False):
    return lex(Path(filepath).read_text(encoding="utf-8"), str(filepath))
