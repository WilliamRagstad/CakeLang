# Reuse the same behavior with different particle styles.
sparkle = {
    kind: minecraft:end_rod,
    offset: { x: 0, y: 0.2, z: 0 },
    spread: { x: 0.2, y: 0.1, z: 0.2 },
    count: 2
};

def showTrail(players, style) {
    particle(players, style.kind, style.offset, style.spread, count=style.count);
}

tag(@s, "cake_trail");
say("Trail enabled. Stop with /function trail:stop");
function load() {
    say("Cake trail loaded. Start with /function trail:main");
}
function tick() {
    showTrail(a(tag="cake_trail"), sparkle);
}
function stop() {
    tag(@s, "cake_trail", enabled=false);
    say("Trail disabled.");
}
