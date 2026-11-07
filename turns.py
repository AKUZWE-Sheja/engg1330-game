"""Opponent turn and end-of-round rules.

Uses the helpers in pc_logic.py (pathfinding, wall choice, collapse rings,
patrols, wall decay) and the board helpers in player.py.
"""
import random

import pc_logic
import player as pl


# The opponent hesitates (does nothing) every Nth round, so the player can
# afford a short detour for an Echo. 0 = never hesitates.
PC_PAUSE_EVERY = {1: 4, 2: 3, 3: 0}


# ---------------------------------------------------------------- goals
def update_goals(board):
    """Refresh the goal tiles for the current round."""
    level = board["level"]
    size = board["size"]
    rnd = board["round"]
    if board["pc_pos"] is None:
        board["pc_goal"] = set()
        return
    board["pc_goal"] = pc_logic.get_winning_goal(
        level, size, rnd, lockdown_node=board["keystone"], goal_row=size - 1)
    if level == 3 and rnd > 5:
        # the old goal edge is gone: only the Keystone is left
        key = board["keystone"]
        if key in board["collapsed"]:
            board["player_goal"] = set()
        else:
            board["player_goal"] = {key}


# ------------------------------------------------------------ opponent
def _try_pc_wall(board, human):
    level = board["level"]
    rnd = board["round"]
    if board["pc_walls_left"] <= 0 or board["pc_jammed"]:
        return None
    if level == 1 and board["pc_walled_last"]:
        return None                        # no consecutive walls (level 1)
    if level == 3 and not pc_logic.can_place_wall(rnd):
        return None                        # sudden death
    size = board["size"]
    walls = set(pl.all_walls(board)) | set(board["collapsed"])
    protected = (set(board["protected"]) | set(board["pickups"])
                 | pl.secret_tiles(board) | set(board["door_tiles"]))
    min_gain = 3 if level == 3 else 2

    tile = pc_logic.choose_wall(
        human["pos"], board["pc_pos"], board["player_goal"], board["pc_goal"],
        walls, size, protected=protected, min_gain=min_gain)
    if tile is None:
        return None

    # player walls are 2 tiles long, so the opponent's are too
    r, c = tile
    for d_row, d_col in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        partner = (r + d_row, c + d_col)
        if not pc_logic.in_plane(partner, size):
            continue
        if pc_logic.is_wall_placement_legal(
                partner, walls | {tile}, human["pos"], board["pc_pos"],
                board["player_goal"], board["pc_goal"], size, protected):
            return [tile, partner]
    return None


def pc_turn(board, human):
    """The opponent places a wall or moves one tile.
    Returns (messages, opponent_won)."""
    msgs = []
    if board["pc_pos"] is None:
        return msgs, False

    level = board["level"]
    size = board["size"]
    rnd = board["round"]

    pause = PC_PAUSE_EVERY.get(level, 0)
    if pause and rnd % pause == 0:
        msgs.append("The opponent hesitates.")
        return msgs, False

    wall = _try_pc_wall(board, human)
    if wall is not None:
        for tile in wall:
            board["pc_walls"][tile] = rnd
        board["pc_walls_left"] -= 1
        board["pc_walled_last"] = True
        board["pc_jammed"] = False
        msgs.append("The opponent placed a wall. ({0} left)".format(
            board["pc_walls_left"]))
        return msgs, False

    board["pc_walled_last"] = False
    board["pc_jammed"] = False

    pos = board["pc_pos"]
    walls = set(pl.all_walls(board))
    door = set(board["door_tiles"]) | set(board["collapsed"])
    goal = board["pc_goal"]
    move_walls = walls | {human["pos"]}

    avoid = None
    if level == 3:
        # Survivalist: stay off the rings that are about to melt
        avoid = pc_logic.get_ring_tiles(size, 3) - set(board["collapsed"])

    # Opportunist: level 2 opponent may detour for Phase Step
    powerup_pos = None
    if level == 2 and not board["pc_has_phase"]:
        for tile, kind in board["pickups"].items():
            if kind == "phase":
                powerup_pos = tile
    target = pc_logic.decide_pc_target(
        pos, goal, powerup_pos, move_walls, size,
        opponent_pos=human["pos"], door_tiles=door)

    nxt = pc_logic.get_next_pc_move(
        pos, target, move_walls, size,
        has_phase_step=board["pc_has_phase"], door_tiles=door, avoid_tiles=avoid)

    if nxt == human["pos"]:
        # Phase Step is for walls, not for walking through the player
        nxt = pc_logic.get_next_pc_move(
            pos, target, move_walls, size,
            has_phase_step=False, door_tiles=door, avoid_tiles=avoid)

    if nxt is None or nxt == pos or nxt == human["pos"]:
        return msgs, False

    board["pc_has_phase"] = pc_logic.update_phase_step(
        board["pc_has_phase"], nxt, walls)
    board["pc_pos"] = nxt

    if level == 2 and board["pickups"].get(nxt) == "phase":
        del board["pickups"][nxt]
        board["pc_has_phase"] = True
        msgs.append("The opponent grabbed Phase Step!")

    if nxt in pl.goal_set(goal):
        msgs.append("The opponent reached its goal!")
        return msgs, True
    return msgs, False


# ----------------------------------------------------------- end of round
def _tile_free(board, human, tile):
    if tile == human["pos"] or tile == board["pc_pos"]:
        return False
    if tile in pl.all_walls(board) or tile in board["pickups"]:
        return False
    if tile in board["collapsed"] or tile in board["door_tiles"]:
        return False
    if tile in pl.secret_tiles(board):
        return False
    return True


def end_round(board, human):
    """Patrols, collapse, wall decay, respawns, then the next round starts.
    Returns (messages, level_failed)."""
    msgs = []
    level = board["level"]
    size = board["size"]
    rnd = board["round"]

    # Level 2: patrol walls move; one stalled twice becomes the Anchor shard
    if board["patrols"]:
        shard = pc_logic.update_patrol_walls(
            board["patrols"], set(board["player_walls"]), size)
        board["neutral_walls"] = pc_logic.get_patrol_tiles(board["patrols"])
        if shard is not None:
            board["shard"] = shard
            msgs.append("A stalled patrol wall crystallised into an Anchor shard!")

    # Level 3: the outer ring collapses at the end of rounds 5, 10 and 15
    if level == 3 and rnd % 5 == 0 and rnd <= 15:
        rings = min(rnd // 5, 3)
        ring = pc_logic.get_ring_tiles(size, rings) - set(board["anchored"])
        newly = ring - board["collapsed"]
        board["collapsed"] |= ring
        for tile in newly:
            board["player_walls"].pop(tile, None)
            board["pc_walls"].pop(tile, None)
            board["pickups"].pop(tile, None)
        msgs.append("The board collapses! Ring {0} is gone.".format(rings))

    # Level 3: walls decay after 8 rounds
    if level == 3:
        for name in ("player_walls", "pc_walls"):
            alive = pc_logic.get_active_walls(board[name], rnd + 1, lifetime=8)
            for tile in list(board[name]):
                if tile not in alive:
                    del board[name][tile]

    # Level 1: used power-ups come back after 4 rounds
    waiting = []
    for due, tile, kind in board["respawn"]:
        if rnd + 1 >= due and _tile_free(board, human, tile):
            board["pickups"][tile] = kind
            msgs.append("A power-up reappeared.")
        else:
            waiting.append((due, tile, kind))
    board["respawn"] = waiting

    # Level 3 Sudden Death: power-ups spawn every round after round 20
    if level == 3 and rnd >= 20 and len(board["pickups"]) < 3:
        free = [(r, c) for r in range(size) for c in range(size)
                if _tile_free(board, human, (r, c))]
        if free:
            board["pickups"][random.choice(free)] = random.choice(["overclock", "phase"])
            msgs.append("Sudden Death: a power-up spawned.")

    board["round"] = rnd + 1
    update_goals(board)

    failed = False
    if level == 3 and board["round"] > 5 and board["keystone"] in board["collapsed"]:
        msgs.append("The Keystone collapsed. The exit is gone.")
        failed = True
    return msgs, failed
