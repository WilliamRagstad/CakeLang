# Run as a player: /function launch:main
# An effect recipe is data, reusable with different targets or settings.
flight = [
    { kind: minecraft:levitation, duration: 3, amplifier: 4 },
    { kind: minecraft:slow_falling, duration: 20, amplifier: 0 }
];

def applyEffects(target, recipe) {
    # Bind the target once; every effect applies to the same entity.
    as(target, {
        forEach(recipe, boost, {
            effect(@s, boost.kind, boost.duration, boost.amplifier);
        });
    });
}

say("Launch! Enjoy a short flight with a slow landing.");
applyEffects(@s, flight);
