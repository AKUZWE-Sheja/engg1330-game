"""Barricade: Echoes - main game loop.

Run:   python main.py
Extra: python main.py --plain       (letters instead of emoji)
       python main.py --level 2     (start at level 2, for testing)
       python main.py --no-clear    (do not clear the screen)
"""
import os
import sys

import display
import level_setup
import player
import turns
import view

LAST_LEVEL = 3
CLEAR = True


def clear_screen():
    if CLEAR:
        os.system("cls" if os.name == "nt" else "clear")


def ask(prompt):
    try:
        return input(prompt)
    except EOFError:
        return "q"


def start_level(human, index):
    board = level_setup.build_level(index)
    player.reset_for_level(human, index, board["player_start"])
    turns.update_goals(board)
    return board


def show(human, board, log):
    clear_screen()
    view.draw_key()
    view.draw_board(human, board)
    display.draw_controls(human)
    view.draw_extra_controls(human, board)
    print()
    for line in log[-6:]:
        print(line)


def handle_events(human, board, events, log):
    """Turn player.py events into messages. Returns True if the level was won."""
    won = False
    for event in events:
        kind = event[0]
        if kind == "won":
            won = True
        elif kind == "picked":
            log.append("Picked up " + event[1] + ".")
        elif kind == "hands_full":
            log.append("Your hands are full: can't pick up " + event[1] + ".")
        elif kind == "echo":
            log.append("*** You earned the Echo of " + event[1].capitalize() + "! ***")
        elif kind == "glyph":
            log.append("Glyph " + str(event[1]) + " lit.")
        elif kind == "glyph_reset":
            log.append("Wrong glyph! The sequence resets.")
        elif kind == "door_open":
            log.append("The Glyph Door opens!")
        elif kind == "anchored":
            log.append("Tile " + str(event[1]) + " is pinned and won't collapse.")
        elif kind == "used" and board["level"] == 1:
            board["respawn"].append((board["round"] + 4, event[2], event[1]))
    return won


def check_coins(human, board, log):
    pos = human["pos"]
    if pos in board["coins"]:
        board["coins"].discard(pos)
        board["coins_got"] += 1
        log.append("Coin! ({0}/{1})".format(board["coins_got"], board["coins_needed"]))
        if board["coins_got"] >= board["coins_needed"]:
            board["door_tiles"] = set()
            log.append("The top row is unlocked!")
    elif pos == board["hint_coin"]:
        board["hint_coin"] = None
        log.append("Some rewards matter later.")


def player_turn(human, board, log):
    """Returns 'won', 'quit', 'restart', 'replay N' or None (turn finished)."""
    player.begin_turn(human)
    while True:
        show(human, board, log)
        raw = ask("\n> ").strip().lower()
        if human["aim"] is None:
            if raw in ("q", "quit", "restart"):
                return raw
            if raw.startswith("replay"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].isdigit() and int(parts[1]) < board["level"]:
                    return raw
                log.append("Type replay and an earlier level, e.g. replay 1.")
                continue
        ok, message, events = player.handle_command(human, board, raw)
        if message:
            log.append(message)
        if handle_events(human, board, events, log):
            return "won"
        if board["level"] == 0:
            check_coins(human, board, log)
        if human["actions_left"] <= 0 and human["aim"] is None:
            return None


def restart_level(human, board, log, reason):
    log.append(reason)
    log.append("The level restarts. (Your move budget is NOT refunded.)")
    return start_level(human, board["level"])


def main():
    global CLEAR
    args = sys.argv[1:]
    if "--plain" in args:
        view.use_plain()
    if "--no-clear" in args:
        CLEAR = False
    level = 0
    if "--level" in args:
        level = int(args[args.index("--level") + 1])

    human = player.new_player()
    board = start_level(human, level)
    log = ["Level {0}: {1}".format(board["level"], board["name"]), board["intro"]]

    while True:
        result = player_turn(human, board, log)

        if result in ("q", "quit"):
            print("Quitting...")
            return
        if result == "restart":
            board = restart_level(human, board, log, "Restarting the level.")
            continue
        if result is not None and result.startswith("replay"):
            board = start_level(human, int(result.split()[1]))
            log.extend(["", "Replaying level {0}: {1}".format(board["level"], board["name"]),
                        board["intro"]])
            continue
        if result == "won":
            log.append("*** You cleared level {0}! ***".format(board["level"]))
            if board["level"] >= LAST_LEVEL:
                show(human, board, log)
                print("\nCongratulations, you beat the game!")
                return
            board = start_level(human, board["level"] + 1)
            log.extend(["", "Level {0}: {1}".format(board["level"], board["name"]),
                        board["intro"]])
            continue

        if player.end_turn(human):
            show(human, board, log)
            print("\nYou ran out of moves. Game over.")
            return

        messages, opponent_won = turns.pc_turn(board, human)
        log.extend(messages)
        if opponent_won:
            board = restart_level(human, board, log, "The opponent got there first!")
            continue

        messages, failed = turns.end_round(board, human)
        log.extend(messages)
        if failed:
            board = restart_level(human, board, log, "You can no longer win this level.")


if __name__ == "__main__":
    main()
