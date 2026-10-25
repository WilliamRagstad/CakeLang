# Run as a player in an open area, on Easy difficulty or higher.
kit = { weapon: minecraft:bow, ammunition: minecraft:arrow, count: 16 };

def equip(target, equipment) {
    give(target, equipment.weapon);
    give(target, equipment.ammunition, equipment.count);
}

def practiceTarget(target, equipment, distance) {
    equip(target, equipment);
    as(target, {
        summon(minecraft:husk, { x: 0, y: 0, z: distance }, {
            noAI: true,
            persistent: true,
            tags: ["cake_target"],
            name: "Cake target"
        });
    });
}

practiceTarget(@s, kit, 8);
say("Hit the target eight blocks south! Remove remaining targets with /function target:cleanup");
function cleanup() {
    as(@s, {
        kill(e(type=minecraft:husk, tag="cake_target", radius<=32));
    });
}
