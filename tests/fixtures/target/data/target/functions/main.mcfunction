give @s minecraft:bow 1
give @s minecraft:arrow 16
execute at @s run summon minecraft:husk ~ ~ ~8 {NoAI:1b,PersistenceRequired:1b,Tags:["cake_target"],CustomName:'{"text":"Cake target"}'}
say Hit the target eight blocks south! Remove remaining targets with /function target:cleanup
