# Run as a player in an open area. Spawns one stationary practice target.
command("give @s minecraft:bow 1");
command("give @s minecraft:arrow 16");
command("execute at @s run summon minecraft:husk ~ ~ ~8 {NoAI:1b,PersistenceRequired:1b,Tags:[\"cake_target\"],CustomName:'{\"text\":\"Cake target\"}'}");
say("Hit the target eight blocks south! Remove remaining targets with /function target:cleanup");
function cleanup() {
    command("execute at @s run kill @e[type=minecraft:husk,tag=cake_target,distance=..32]");
}
