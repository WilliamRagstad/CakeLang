# Cake compiler: implemented language and backend

The README describes Cake's direction. This document describes the compiler
implemented in this branch: a language with reusable functions, structured data,
and Minecraft-inspired operations, targeting **Minecraft Java Edition 1.20.4**
(datapack format **26**). It is an initial subset, not a complete implementation
of the language envisioned in the README.

## Install and compile

Python 3.10+ is required. There are no runtime Python dependencies.

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

Windows activation: `.venv\Scripts\activate`. The installed `cake` command works
outside the checkout; `python cake.py` works inside it. `--lint` validates without
writing. Errors include source path, line and column, and produce a nonzero exit
code. Output defaults to `build/SOURCE_STEM`, namespace to `cake`. Existing output
directories are refused. Choose a new output path or remove an old generated pack.

## Functions and data

```text
def makeBoost(kind, seconds) {
    return { kind: kind, duration: seconds * 2, amplifier: 1 };
}

def applyEffects(target, recipe) {
    as(target, {
        forEach(recipe, boost, {
            effect(@s, boost.kind, boost.duration, boost.amplifier);
        });
    });
}

flight = [
    makeBoost(minecraft:levitation, 2),
    { kind: minecraft:slow_falling, duration: 20, amplifier: 0 }
];
applyEffects(@s, flight);
```

Functions declared with `def` accept numbers, strings, booleans, selectors,
resource IDs, records, and lists. They can call other definitions, perform
operations, and return values. `macro` is currently an alias for `def`.
An explicit `return` must be the final statement. The final expression is also
an implicit return, preserving selector definitions such as `randomClose`.

Bindings (`name = expression`) are immutable within their scope. Records use
`{ field: expression }`, fields use `record.field`, and lists use `[a, b]`.
Empty `{}` in a value context is an empty record. Functions use lexical scope:
parameters and local bindings take precedence over top-level bindings; caller
locals do not leak into called functions. Top-level values must be bound before
a top-level call uses them. Runtime entry points see the completed top-level
bindings. Parameters may shadow globals.

Numeric `+`, `-`, `*`, `/`, unary minus and parentheses are supported with
standard precedence. Division produces a floating-point value. Booleans are
`true` and `false`, distinct from numbers. Record/list values do not support
mutation, indexing, or arbitrary methods yet.

These values, arithmetic, parameter passing, and `def` calls are evaluated at
**compile time**. They configure and compose Minecraft behavior; they are not
yet runtime heap objects or scoreboard-backed variables. Selector values
describe selections evaluated by Minecraft at runtime. Generic function names,
scope and recursion are checked even when unused; argument-dependent field and
type checks occur when a function is instantiated. Recursion is not supported
for compile-time definitions.

## Control and execution context

- `repeat(count, { ... })` expands a block in order. The count is an integer
  from 0 to 1024; even a zero-count block is validated.
- `forEach(list, item, { ... })` instantiates a block once per list element.
  The iteration binding is scoped to the block. Empty lists emit nothing;
  argument-dependent type checks require an iteration.
- `as(selector, { ... })` binds the selection at runtime, sets the execution
  position to each selected entity, and executes the entire block in that
  context. The backend generates a helper function, so a random selector is
  resolved once for the block. Use `@s` inside to refer to that entity.

The backend limits generated commands to 10,000, list iterations to 1024,
compile-time evaluation to 100,000 steps, and expression/call nesting to 64.
The `__cake_` function prefix is reserved for compiler-generated helpers.

## Selectors and Minecraft values

```text
import player from minecraft

def randomClose(maxRadius) {
    r(type=player, radius<=maxRadius)
}

repeat(3, {
    say(randomClose(10), "Hello {@s}!");
});
```

Selectors are first-class values: `@s`, `@a`, `@p`, `@r`, `@e`, or filtered
calls `s(...)`, `a(...)`, `p(...)`, `r(...)`, `e(...)`. Supported filters:
`type=resource`, `radius<=number`, `tag="name"`, `limit=integer` (except on
`s`). Radius becomes Minecraft's `distance=..number`. Resource IDs such as
`minecraft:levitation` are typed values, not command strings. The current
resource literal syntax is `namespace:identifier`; paths with slashes are not
implemented. The only implemented import is `player from minecraft`.

The greeting above broadcasts three messages naming selected players.
Each repetition selects independently; it may select the same player again.
Radius is relative to the caller's position. The `{@s}` interpolation in
two-argument `say` becomes a Minecraft selector text component.

## Typed Minecraft operations

Operations accept positional arguments followed by optional named arguments.
For example, `effect(@s, minecraft:speed, duration=5, amplifier=2)`.
Names below are the argument names accepted by the compiler.

| Operation | Required arguments | Optional arguments |
| --- | --- | --- |
| `effect` | `target, effect, duration` | `amplifier=0, hideParticles=true` |
| `give` | `target, item` | `count=1` |
| `tag` | `target, name` | `enabled=true` (false removes the tag) |
| `kill` | `target` | — |
| `summon` | `entity, position` | `data={}` |
| `particle` | `target, particle, position, spread` | `speed=0, count=1, force=true` |

Targets are selectors; effect, item, entity and particle IDs are resources.
Durations, amplifiers, counts, booleans and vector fields are type/range checked.
Effect durations are seconds; amplifiers are zero-based.
Positions and spreads are records with exactly `x, y, z` numeric fields.
Positions are relative to the execution position, and spreads are nonnegative.

`summon` accepts structured data fields `noAI`, `persistent`, `tags` (a list of
strings), and `name`; the backend serializes SNBT and JSON text safely.
`particle` executes at each target and shows the particles to that target.
Use player selectors for that operation. Command-specific block/item particle
parameters are not implemented.

`say("text")` emits a literal Minecraft say command.
`say(selector, "Hello {@s}!")` executes as the selected entity and broadcasts
a JSON text message. Strings use JSON double-quote/escape syntax; control
characters and empty/whitespace-only strings are rejected.

Minecraft resource existence and game-dependent applicability are not checked
against a registry. For example, effects require living entities and give
requires players. The target game version remains 1.20.4.

`command("...")` remains a low-level escape hatch for unsupported operations.
It is not used by any supported example. Raw commands receive no Minecraft
grammar validation; they cannot start with a slash or comment marker.

## Runtime entry points and pack output

Top-level operations become `namespace:main`; they do not run automatically.
Zero-argument `function name() { ... }` declarations produce callable runtime
functions. Invoke them with `name()`, `call("name")`, or Minecraft's
`/function namespace:name`. Functions named `load` and `tick` register in
Minecraft lifecycle tags. They run in server context; use `as` to bind players.

Runtime function names use `[a-z_][a-z0-9_]*`; `main` and `__cake_*` are
reserved. Runtime calls inherit Minecraft's execution context and command
limits. Unlike `def`, runtime functions have no parameter or return protocol
yet. Runtime mutation, general branching, dynamic loops, broader modules,
classes, and general runtime data structures remain future work. Unsupported
syntax fails explicitly rather than silently generating empty commands.

## Play the examples

Copy each generated pack directory into `<world>/datapacks/`, with
`pack.mcmeta` directly inside that directory. Use Java **1.20.4** with
cheats/operator permissions, then run `/reload` and `/datapack list enabled`.

- `/function launch:main`: applies a data-driven flight recipe to the player.
- `/function target:main`: equips a bow/arrows and spawns a stationary husk
  eight blocks south. Use an open area on Easy or higher difficulty.
  `/function target:cleanup` removes tagged targets within 32 blocks.
- `/function trail:main`: enables a personal particle trail.
  `/function trail:stop` disables it.
- `/function greet_random:main`: greets nearby random players three times.

Examples change effects, inventory, tags and entities, not blocks. Given items
and target drops can remain. Trail tags persist through reloads; stop the trail
before removing the pack.

## Verification

Tests cover language semantics, error locations, unsupported syntax,
execution-context helpers, CLI behavior, and complete output fixtures for all
four examples. CI installs a wheel into a fresh environment and compiles every
example outside the checkout on Python 3.10, 3.12 and 3.14.

**Minecraft acceptance remains incomplete.** No live 1.20.4 playthrough has been
performed. Follow [the runtime checklist](acceptance.md); compiler fixtures do
not establish game execution.

Pack format reference: https://minecraft.wiki/w/Data_pack
