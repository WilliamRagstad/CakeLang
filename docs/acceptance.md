# Minecraft Java 1.20.4 acceptance gate

Status: **INCOMPLETE — game/server verification not run**.

The environment has Java 21 but no supplied Minecraft server installation,
accepted server EULA, running world, or player client. No EULA was accepted on
the user's behalf. Python compilation/fixtures cannot substitute for this gate.

Use an isolated Java 1.20.4 client/world or server with its EULA accepted by the
operator. Enable cheats/operator permissions and use Easy or higher difficulty.

- [ ] Record exact client/server version, date, operator, and server log.
- [ ] Install all three freshly compiled packs and run /reload.
- [ ] Confirm /datapack list enabled contains all three; inspect logs for errors.
- [ ] launch:main lifts the executing player and they land slowly.
- [ ] target:main gives bow/arrows and spawns a stationary husk eight blocks south.
- [ ] Shoot the husk; target:cleanup removes surviving tagged targets within 32 blocks.
- [ ] trail:main shows particles following the player while moving.
- [ ] trail:stop stops particles; another player without the tag gets no trail.
- [ ] Reload: load announces readiness and tick continues without duplicate effects.
- [ ] Stop trails, remove test packs, reload, and confirm no lingering tick errors.

Do not mark this checklist complete based only on command text inspection.

# Review sequence

1. Runnable compiler baseline: installable CLI, isolated lexer/parser/checker,
   location-bearing failures, explicit subset.
2. Datapack generation: 1.20.4 metadata, functions, lifecycle tags, safe new
   output directory, deterministic fixture tests.
3. Examples and accurate documentation: three runnable example sources,
   complete output fixtures, clean-wheel CI, and this pending gameplay gate.

The third change remains a draft until the Minecraft acceptance gate is recorded.
