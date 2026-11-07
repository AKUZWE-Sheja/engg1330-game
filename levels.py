from grid import Board

def build_level_0():
#tutorial
    board = Board(0, 9, 9, "Tutorial")
    board.actors["player"] = (4, 7)

    for x in range(1, 8):
        board.exits.add((x, 1))
    board.sealed = True

    for cell in [(4, 6), (4, 5), (4, 4)]:
        board.pickups[cell] = "coin"
    board.pickups[(2, 5)] = "coin"          

    board.meta = {"coins_required": 3, "hint_cell": (2, 5),
                  "hint_text": "Some rewards matter later."}
    return board


def build_level_1():
#level 1
    board = Board(1, 9, 9, "Open Barricade")
    board.actors["player"] = (4, 7)

    for x in range(1, 8):
        board.exits.add((x, 1))

    for cell in [(2, 3), (6, 3), (2, 5), (6, 5)]:
        board.walls[cell] = "fixed"

    board.pickups[(4, 4)] = "prism"
    board.hidden[(4, 4)] = "sight"           

    board.meta = {"secret": (4, 4), "echo": "sight"}
    return board


def build_level_2():
#level 2
    board = Board(2, 11, 11, "Shifting Barricade")
    board.actors["player"] = (5, 9)

    for x in range(1, 10):
        board.exits.add((x, 1))
    board.sealed = True

    glyphs = [(2, 8), (9, 7), (3, 2)]
    for i in range(3):
        cell = glyphs[i]
        board.pickups[cell] = "glyph" + str(i + 1)
        board.hidden[cell] = "sight"         

    board.walls[(5, 3)] = "fixed"
    board.walls[(5, 7)] = "fixed"

    patrol_path = [(2, 5), (3, 5), (4, 5), (5, 5),
                   (6, 5), (7, 5), (8, 5), (9, 5)]
    board.add_patrol(patrol_path)

    board.meta = {"glyph_order": glyphs, "echo": "anchor",
                  "patrol_track": set(patrol_path)}
    return board


def build_level_3():
#level 3
    board = Board(3, 13, 13, "Collapse Protocol")
    board.actors["player"] = (6, 11)

    keystone = (6, 1)
    for x in range(1, 12):
        if x != keystone[0]:
            board.exits.add((x, 1))          # the decoy edge

    board.pickups[keystone] = "keystone"
    board.hidden[keystone] = "sight"

    for cell in [(4, 6), (8, 6), (6, 8)]:
        board.walls[cell] = "fixed"

    board.meta = {"secret": keystone, "choke": (6, 2),
                  "decoy_collapses_on_round": 5,
                  "choke_collapses_on_round": 10,
                  "echo": None}
    return board


def build_all():
    return [build_level_0(), build_level_1(), build_level_2(), build_level_3()]