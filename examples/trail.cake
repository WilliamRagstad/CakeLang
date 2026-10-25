# Toggle a sparkling trail while walking or flying.
command("tag @s add cake_trail");
say("Trail enabled. Stop with /function trail:stop");
function load() {
    say("Cake trail loaded. Start with /function trail:main");
}
function tick() {
    command("execute as @a[tag=cake_trail] at @s run particle minecraft:end_rod ~ ~0.2 ~ 0.2 0.1 0.2 0 2 force @s");
}
function stop() {
    command("tag @s remove cake_trail");
    say("Trail disabled.");
}
