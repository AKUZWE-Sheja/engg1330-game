"""Builds the dictionary board that player.py and pc_logic.py expect.

Coordinates are (row, col). Row 0 is the TOP of the screen.
The player starts on the bottom row and races to the top row.
The opponent starts on the top row and races to the bottom row.
"""


def top_row(size):
    return {(0, col) for col in range(size)}


def bottom_row(size):
    return {(size - 1, col) for col in range(size)}


def new_board(level, name, size, player_start, pc_start, intro):
    return {
        "level": level,
        "name": name,
        "size": size,
        "intro": intro,
        "round": 1,
        "player_start": player_start,
        "pc_pos": pc_start,
        "player_goal": top_row(size),
        "pc_goal": set() if pc_start is None else bottom_row(size),
        "player_walls": {},          # tile -> round placed
        "pc_walls": {},              # tile -> round placed
        "neutral_walls": set(),      # patrol wall tiles
        "collapsed": set(),
        "anchored": set(),
        "door_tiles": set(),
        "protected": set(),
        "pickups": {},               # tile -> power-up kind
        "glyphs": [],
        "prism": None,
        "shard": None,
        "keystone": None,
        "pc_walls_left": 0,
        "pc_jammed": False,
        "pc_has_phase": False,
        "pc_walled_last": False,
        "patrols": [],               # pc_logic patrol format
        "respawn": [],               # (round_due, tile, kind)
        "coins": set(),
        "hint_coin": None,
        "coins_needed": 0,
        "coins_got": 0,
    }


def build_level_0():
    board = new_board(
        0, "Tutorial", 9, (8, 4), None,
        "Collect the 3 coins to unlock the top row, then walk to it. "
        "A 4th coin is hidden slightly off the path.")
    board["door_tiles"] = top_row(9)
    board["coins"] = {(6, 4), (4, 4), (2, 4)}
    board["coins_needed"] = 3
    board["hint_coin"] = (5, 2)
    return board


def build_level_1():
    board = new_board(
        1, "Open Barricade", 9, (8, 4), (0, 4),
        "Reach the top row before the opponent reaches the bottom row. "
        "Something shimmers in the Central Plaza...")
    mid = 4
    board["protected"] = {(r, c) for r in range(mid - 2, mid + 3)
                          for c in range(mid - 2, mid + 3)}
    board["prism"] = (3, 3)
    board["pickups"] = {(6, 4): "survey"}
    board["pc_walls_left"] = 8
    return board


def build_level_2():
    board = new_board(
        2, "Shifting Barricade", 11, (10, 5), (0, 5),
        "The top row is sealed by a Glyph Door marked with an eye. "
        "Only those who can see can open it.")
    board["door_tiles"] = top_row(11)
    board["glyphs"] = [(8, 4), (5, 4), (2, 4)]
    board["protected"] = {(5, 3), (5, 7)}          # the twin chokepoints
    board["pickups"] = {(5, 5): "phase"}
    board["patrols"] = [
        {"tiles": [(4, 1), (4, 2)], "direction": (0, 1), "stall": 0},
        {"tiles": [(6, 8), (6, 9)], "direction": (0, -1), "stall": 0},
    ]
    board["neutral_walls"] = {t for p in board["patrols"] for t in p["tiles"]}
    board["pc_walls_left"] = 10
    return board


def build_level_3():
    board = new_board(
        3, "Collapse Protocol", 13, (12, 6), (0, 2),
        "The board is crumbling. The old exit will not last. "
        "A Keystone silhouette hangs in the outer ring...")
    board["keystone"] = (0, 6)
    board["protected"] = {(1, 6)}                  # the choke tile
    board["pickups"] = {(9, 6): "overclock"}
    board["pc_walls_left"] = 12
    return board


BUILDERS = [build_level_0, build_level_1, build_level_2, build_level_3]


def build_level(index):
    return BUILDERS[index]()
