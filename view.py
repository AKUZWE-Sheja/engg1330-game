"""Drawing code. Reuses display.py for the tiles and the controls list."""
import display
import player as pl

PLAIN_ICONS = {
    "player": " P ", "pc": " C ", "player_wall": " # ", "pc_wall": " = ",
    "patrol": " ! ", "pickup": " $ ", "aim": " : ", "glyph1": " 1 ",
    "glyph2": " 2 ", "glyph3": " 3 ", "prism": " * ", "shard": " o ",
    "keystone": " K ", "collapsed": "   ", "empty": " . ",
}
EXTRA_EMOJI = {"coin": " 🪙 ", "goal": " 🏁 ", "door": " 🔒 "}
EXTRA_PLAIN = {"coin": " c ", "goal": " E ", "door": " L "}

extra = dict(EXTRA_EMOJI)


def use_plain():
    display.ICONS.update(PLAIN_ICONS)
    extra.update(EXTRA_PLAIN)


def tile_icon(human, board, tile, secrets, aim):
    icon = display.cell(human, board, tile, secrets, aim)
    if icon != display.ICONS["empty"]:
        return icon
    if tile in board["door_tiles"]:
        return extra["door"]
    if tile in board["coins"] or tile == board["hint_coin"]:
        return extra["coin"]
    if tile in pl.goal_set(board["player_goal"]) and tile not in board["collapsed"]:
        return extra["goal"]
    return icon


def draw_board(human, board):
    secrets = pl.visible_secrets(human, board)
    aim = pl.aim_tiles(human)
    for row in range(board["size"]):
        line = ""
        for col in range(board["size"]):
            line += tile_icon(human, board, (row, col), secrets, aim)
        print(line)
    print()
    print("Level {0}: {1} | Round {2} | Moves {3} | Walls {4}".format(
        board["level"], board["name"], board["round"],
        human["moves_left"], human["walls_left"]))
    print("Sight: {0} | Anchor: {1}".format(
        "yes" if human["sight"] else "no",
        "used" if human["anchor_used"] else ("yes" if human["anchor"] else "no")))
    if board["level"] == 0:
        print("Coins: {0}/{1}".format(board["coins_got"], board["coins_needed"]))
    view = pl.survey_view(human, board)
    if view is not None and view["pc_path"] is not None:
        print("Opponent: {0} steps from goal, {1} walls left".format(
            len(view["pc_path"]) - 1, view["pc_walls_left"]))


def draw_key():
    if extra is not EXTRA_EMOJI and extra["goal"] == EXTRA_PLAIN["goal"]:
        print("P you  C opponent  # your wall  = enemy wall  ! patrol  $ power-up  E goal  L sealed")
        return
    print("🔴 you  🔵 opponent  🟥 your wall  🟦 enemy wall  🚧 patrol  🎁 power-up  🏁 goal  🔒 sealed")
