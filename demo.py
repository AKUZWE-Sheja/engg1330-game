import sys

from grid import use_plain_icons
from levels import build_all


def show(board, reveal_all=False):
    start = board.actors["player"]
    route = board.route(start, board.exits)

    if route is None:
        if board.sealed:
            status = "Route: BLOCKED - the exit is sealed (level lock)"
        else:
            status = "Route: BLOCKED - no path to the exit"
        board.set_path(None)
    else:
        status = "Route: {0} steps   Pickups are walkable   Echoes are ignored".format(
            len(route) - 1)
        board.set_path(route)

    print("\n".join(board.screen(status, reveal_all)))


def show_lock():
    board = build_all()[2]
    print("--- Level 2 with the Glyph Door still sealed ---")
    show(board)
    print()
    print("--- Same board after the three glyphs are stepped in order ---")
    board.sealed = False
    show(board)


def show_wall_check():
    board = build_all()[3]
    start = board.actors["player"]
    target = board.exits
    for y in range(board.height):
        for x in range(board.width):
            if not board.can_place_wall(x, y):
                continue
            if board.wall_blocks_route(start, target, x, y):
                print("Wall at ({0}, {1}) would seal the player in -> rejected".format(x, y))
                return
    print("No single wall seals this board, so every legal cell is allowed.")


def main():
    args = sys.argv[1:]
    if "plain" in args:
        use_plain_icons()

    boards = build_all()

    if "lock" in args:
        show_lock()
        return

    if "all" in args:
        for board in boards:
            show(board)
            print()
        return

    show(boards[3])
    print()
    show_wall_check()


if __name__ == "__main__":
    main()