say("Hello world");
function load() { call("greet") }
function tick() { command("execute as @a run particle minecraft:happy_villager ~ ~1 ~ 0 0 0 0 1") }
function greet() { say("Ready!") }
