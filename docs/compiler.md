# Implemented compiler subset

Cake compiles a deliberately small language subset to **Minecraft Java Edition
1.20.4** datapacks (pack format **26**). Python 3.10+ is required.
There are no runtime Python dependencies. Other Minecraft versions and Bedrock
Edition are not supported.

## Install and run

From a checkout:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install .
cake examples/launch.cake --namespace launch --output build/launch
cake examples/target.cake --namespace target --output build/target
cake examples/trail.cake --namespace trail --output build/trail
cake examples/greet_random.cake --namespace greet_random --output build/greet_random
python -m unittest discover -v
```

Windows users can activate with `.venv\Scripts\activate`.
The installed `cake` command works outside the checkout. `python cake.py` also
works from the checkout. `cake --help` lists options; `--lint` validates without
writing. Errors go to stderr with a nonzero exit code and source line/column.
Output defaults to `build/SOURCE_STEM`, namespace to `cake`. Use distinct
namespaces when installing multiple packs. Existing output directories are
refused: remove an old *generated* pack or choose a new output path.

## Supported language

```text
# Comments run to the end of a line.
say("Hello world");
call("greet");
function greet() {
    command("give @s minecraft:cookie 1");
}
```

A program contains top-level calls and zero-argument function declarations.
Top-level calls become `NAMESPACE:main`; they do not run automatically.
Functions named `load` and `tick` register in Minecraft's load and tick tags.
Other functions run through `call("name")` or Minecraft's `/function` command.
Calls may refer to functions declared later. Semicolons are optional.
Function names use `[a-z_][a-z0-9_]*`; `main` is reserved.

| Call | Output |
| --- | --- |
| `say("text")` | `say text` |
| `command("Minecraft command")` | The command verbatim, without a leading slash |
| `call("local_function")` | `function namespace:local_function` |

Arguments must be JSON-style double-quoted strings. Escaped quotes, backslashes,
and Unicode are supported; empty/whitespace-only strings and control characters
are rejected. The one-argument form does not interpolate Cake expressions.
Minecraft interprets selectors and command text at execution time.
**Cake does not validate Minecraft command grammar**, resource IDs, permissions,
or runtime success. Command syntax must match Java 1.20.4. Function calls inherit
Minecraft's execution context; load/tick have server context, so use
`execute as ... at ...` when a player or position is needed.
Recursive calls are permitted and subject to Minecraft's command limits.

## Selector definitions and repetition

The README describes the language's direction and remains unchanged. The compiler
currently also supports this program (see examples/greet_random.cake):

```text
import player from minecraft
def randomClose(maxRadius) {
    r(type=player, radius<=maxRadius)
}
repeat(3, {
    say(randomClose(10), "Hello {@s}!");
});
```

`def` and `macro` are equivalent compile-time selector definitions. Their bodies
contain one selector expression; parameters are numeric. Definitions can call
other definitions, including forward references, but cannot recurse. Both used
and unused definitions are checked. These definitions emit no runtime function.

`r()` selects one random player. Its optional filters are `type=player` (requires
the import above), `type=minecraft:player` (no import needed), and
`radius<=number` (a nonnegative radius, translated to `distance=..number`).
This subset supports only the player import and player entity type.

`repeat(integer, { statements })` expands its body at compile time, in order.
Counts range from 0 to 1024; even a zero-count body is checked. Expanded programs
are limited to 10,000 commands, and nesting is bounded.

`say(selector, "message")` executes as the selected player and broadcasts a
JSON text message to all players. `{@s}` becomes a selector text component
showing that player's name. Each repeated command selects independently, so
three repetitions do not guarantee three distinct players. Radius is relative
to the calling position: run from player chat or with `execute at`.
The one-argument `say("text")` form remains a literal Minecraft say command.

Other modules, variables, assignments, arithmetic, other selector filters,
other interpolation selectors, conditionals, general loops, runtime function
parameters, return statements, and nested definitions fail explicitly.
Minecraft `execute` may be used inside `command`.
Historical examples in examples/legacy use additional unsupported constructs.

## Try the examples

Copy the generated directories directly into
`<world>/datapacks/`. Each directory must contain `pack.mcmeta` at its root.
Use Java **1.20.4**, enable cheats or operator permission, then run `/reload`
and `/datapack list enabled`.

Run these in player chat in a disposable test world:

- `/function greet_random:main`: greets a random player within 10 blocks three times.
- `/function launch:main`: a short levitation ride with slow falling.
- `/function target:main`: gives a bow and arrows and spawns a stationary husk
  eight blocks south. Shoot it; `/function target:cleanup` removes tagged targets
  within 32 blocks. Use an open area and Easy or higher difficulty.
- `/function trail:main`: enables a personal particle trail.
  Walk around; `/function trail:stop` disables it.

The examples change player effects, inventory, tags, and entities.
They do not place blocks. Target drops and given items can remain after cleanup.
Trail tags persist through reloads; stop the trail before removing the pack.

## Verification status

Automated tests cover source errors, unsupported syntax, CLI behavior, all four
example outputs, and exact datapack trees/commands against committed fixtures.
CI builds and installs a wheel into a fresh environment and compiles all four examples.

**Minecraft acceptance is incomplete.** No live 1.20.4 client/server playthrough
has been performed for this change. Fixtures establish compiler output, not
gameplay correctness. Follow [the acceptance checklist](acceptance.md)
before calling the examples game-verified.

Format reference: https://minecraft.wiki/w/Data_pack
