import player from minecraft

def randomClose(maxRadius) {
    # Or use minecraft:player
    r(type=player, radius<=maxRadius)
}

repeat(3, {
    say(randomClose(10), "Hello {@s}!");
});
