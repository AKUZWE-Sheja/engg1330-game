"""Drawing code. Reuses display.py for the base tiles and the controls list.

Every emoji used here is a single double-width character, so rows line up.
Use view.use_plain() (python main.py --plain) for letters instead.
"""
import display
import player as pl

# --- emoji look (default) ---------------------------------------------
EMOJI_OVERRIDES = {
    "player": " 🧑 ", "pc": " 🤖 ",
    "player_wall": " 🧱 ", "pc_wall": " ⛔ ", "aim": " 🔶 ",
    "glyph1": " 🌑 ", "glyph2": " 🌓 ", "glyph3": " 🌕 ",
}
EXTRA_EMOJI = {"coin": " 💰 ", "goal": " 🏁 ", "lock": " 🔒 ", "eyes": " 👀 ",
               "shimmer": " ✨ "}
PICKUP_EMOJI = {"survey": " 🔍 ", "phase": " 👻 ", "overclock": " ⚡ "}

# --- plain letters (fallback) -----------------------------------------
PLAIN_ICONS = {
    "player": " P ", "pc": " C ", "player_wall": " # ", "pc_wall": " = ",
    "patrol": " ! ", "pickup": " $ ", "aim": " : ", "glyph1": " 1 ",
    "glyph2": " 2 ", "glyph3": " 3 ", "prism": " * ", "shard": " o ",
    "keystone": " K ", "collapsed": "   ", "empty": " . ",
}
EXTRA_PLAIN = {"coin": " c ", "goal": " E ", "lock": " L ", "eyes": " L ",
               "shimmer": " ~ "}
PICKUP_PLAIN = {"survey": " s ", "phase": " p ", "overclock": " o "}

ALIGN_COLUMNS = True      # set False if your terminal prints odd characters

extra = dict(EXTRA_EMOJI)
pickup_icons = dict(PICKUP_EMOJI)
plain_mode = False
display.ICONS.update(EMOJI_OVERRIDES)


def use_plain():
    global plain_mode
    plain_mode = True
    display.ICONS.update(PLAIN_ICONS)
    extra.update(EXTRA_PLAIN)
    pickup_icons.update(PICKUP_PLAIN)


def plaza_center(board):
    return (board["size"] // 2, board["size"] // 2)


def tile_icon(human, board, tile, secrets, aim):
    icon = display.cell(human, board, tile, secrets, aim)
    if tile in board["pickups"] and icon == display.ICONS["pickup"]:
        return pickup_icons.get(board["pickups"][tile], icon)
    if icon != display.ICONS["empty"]:
        return icon
    if tile in board["door_tiles"]:
        return extra["eyes"] if board["level"] == 2 else extra["lock"]
    if tile in board["coins"] or tile == board["hint_coin"]:
        return extra["coin"]
    if tile in pl.goal_set(board["player_goal"]) and tile not in board["collapsed"]:
        return extra["goal"]
    if board["level"] == 1 and not human["sight"] and tile == plaza_center(board):
        return extra["shimmer"]
    return icon


def boxed_in(human, board):
    for key in pl.KEYS:
        if pl.move_blocked(human, board, pl.next_tile(human["pos"], key, 1)) is None:
            return False
    return True


def warnings(human, board):
    """Lines telling the player what is missing to finish this level."""
    lines = []
    level = board["level"]
    if level == 2 and not human["sight"]:
        lines.append("WARNING: Level 2 needs the Echo of Sight to see the glyphs. "
                     "Type 'replay 1' to go back and find it.")
    if level == 3:
        if not human["sight"]:
            lines.append("WARNING: Level 3 needs the Echo of Sight. Type 'replay 1'.")
        if not human["anchor"]:
            lines.append("WARNING: Level 3 needs the Echo of Anchor. Type 'replay 2'.")
    return lines


def draw_board(human, board):
    secrets = pl.visible_secrets(human, board)
    aim = pl.aim_tiles(human)
    for row in range(board["size"]):
        line = ""
        for col in range(board["size"]):
            icon = tile_icon(human, board, (row, col), secrets, aim)
            if plain_mode or not ALIGN_COLUMNS:
                line += icon
            else:
                line += "\x1b[{0}G".format(col * 4 + 1) + icon   # jump to column
        print(line)
    print()
    print("Level {0}: {1} | Round {2} | Moves {3} | Walls {4}".format(
        board["level"], board["name"], board["round"],
        human["moves_left"], human["walls_left"]))
    print("Echo of Sight: {0} | Echo of Anchor: {1}".format(
        "yes" if human["sight"] else "no",
        "used" if human["anchor_used"] else ("yes" if human["anchor"] else "no")))
    if board["level"] == 0:
        print("Coins: {0}/{1}".format(board["coins_got"], board["coins_needed"]))
    if board["level"] == 2 and board["door_tiles"]:
        print("Glyph Door: {0}/3 glyphs lit (step on them in order)".format(
            human["glyph_progress"]))
    for line in warnings(human, board):
        print(line)
    if boxed_in(human, board):
        print("You are boxed in! Use a power-up, or type 'restart' to retry this level.")
    view = pl.survey_view(human, board)
    if view is not None and view["pc_path"] is not None:
        print("Opponent: {0} steps from goal, {1} walls left".format(
            len(view["pc_path"]) - 1, view["pc_walls_left"]))


def draw_key():
    if plain_mode:
        print("P you  C opponent  # your wall  = enemy wall  ! patrol  E goal  L sealed  c coin")
        print("s Survey  p Phase Step  o Overclock  1 2 3 glyphs  * prism  K keystone")
        return
    print("🧑 you  🤖 opponent  🧱 your wall  ⛔ enemy wall  🚧 patrol  🏁 goal  🔒 sealed  💰 coin")
    print("🔍 Survey  👻 Phase Step  ⚡ Overclock  🌑🌓🌕 glyphs 1-2-3  💎 prism  🔷 shard  🔑 keystone")


def draw_extra_controls(human, board):
    """Commands added by main.py (shown when not aiming)."""
    if human["aim"] is not None:
        return
    if board["level"] == 3 and human["anchor"] and not human["anchor_used"]:
        print("  anchor key  pin the Keystone so it never collapses")
    print("  restart     restart this level (moves are not refunded)")
    if board["level"] > 0:
        print("  replay N    go back to level N to find a missed Echo")
    print("  q           quit")
