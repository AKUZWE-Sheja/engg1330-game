ICONS = {
    "player": " 🔴 ",
    "pc": " 🔵 ",
    "player_wall": " 🟥 ",
    "pc_wall": " 🟦 ",
    "patrol": " 🚧 ",
    "pickup": " 🎁 ",
    "aim": " 🟫 ",
    "glyph1": " 1️⃣ ",
    "glyph2": " 2️⃣ ",
    "glyph3": " 3️⃣ ",
    "prism": " 💎 ",
    "shard": " 🔷 ",
    "keystone": " 🔑 ",
    "collapsed": "    ",
    "empty": " ⬛ ",
}


def cell(player, board, tile, secrets, aim):
    if tile == player["pos"]:
        return ICONS["player"]
    if tile == board["pc_pos"]:
        return ICONS["pc"]
    if tile in aim:
        return ICONS["aim"]
    if tile in board["collapsed"]:
        return ICONS["collapsed"]
    if tile in board["player_walls"]:
        return ICONS["player_wall"]
    if tile in board["pc_walls"]:
        return ICONS["pc_wall"]
    if tile in board["neutral_walls"]:
        return ICONS["patrol"]
    if tile in secrets:
        return ICONS[secrets[tile]]
    if tile in board["pickups"]:
        return ICONS["pickup"]
    return ICONS["empty"]


POWERUP_HELP = {
    "dash": ["dash w 2", "jump 1 or 2 tiles (w/a/s/d)"],
    "phase": ["phase w", "hop over a wall (w/a/s/d)"],
    "survey": ["survey", "see the opponent's path"],
    "cache": ["cache", "get 1 extra wall"],
    "jam": ["jam", "opponent can't place walls next turn"],
    "dismantle": ["dismantle", "aim at an enemy wall and remove it"],
    "pull": ["pull", "pull the opponent 1 tile toward you"],
    "bomb": ["bomb", "aim and destroy walls in a 2x2 area"],
    "overclock": ["overclock", "take 2 actions this turn"],
}


def control(keys, text):
    print("  " + keys.ljust(11) + text)


def draw_controls(player):
    print()
    if player["aim"] is not None:
        print("Aiming " + player["aim"])
        control("w a s d", "move the cursor")
        if player["aim"] == "wall":
            control("r", "turn the wall")
        control("y", "confirm")
        control("n", "cancel")
        return

    print("Controls")
    control("w a s d", "move up / left / down / right")
    if player["walls_left"] > 0:
        control("b", "place a wall (" + str(player["walls_left"]) + " left)")
    for item in player["inventory"]:
        help_line = POWERUP_HELP[item[0]]
        control(help_line[0], help_line[1])
    if player["anchor"] and not player["anchor_used"]:
        control("anchor", "aim and pin a tile so it never collapses")
    control("pass", "end your turn")