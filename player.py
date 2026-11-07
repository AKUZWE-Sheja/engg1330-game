from pc_logic import get_shortest_path, in_plane

KEYS = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
WALL_DIRS = {"h": (0, 1), "v": (1, 0)}     

LEVEL_WALLS = {0: 0, 1: 8, 2: 10, 3: 12}
LEVEL_HOLD = {0: 1, 1: 1, 2: 1, 3: 2}

START_BUDGET = 150
ANCHOR_RANGE = 99
DISMANTLE_RANGE = 2
BOMB_RANGE = 3
SUDDEN_DEATH_ROUND = 20
USES_TURN = ["dash", "phase", "dismantle", "bomb"]


def next_tile(tile, key, steps):
    d_row = KEYS[key][0]
    d_col = KEYS[key][1]
    return (tile[0] + d_row * steps, tile[1] + d_col * steps)


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def goal_set(goal):
    if isinstance(goal, tuple):
        return {goal}
    return set(goal)


def all_walls(board):
    walls = set()
    for tile in board["player_walls"]:
        walls.add(tile)
    for tile in board["pc_walls"]:
        walls.add(tile)
    for tile in board["neutral_walls"]:
        walls.add(tile)
    return walls


def can_see_glyphs(player):
    return player["sight"] or player["level"] == 0


def secret_tiles(board):
    tiles = set(board["glyphs"])
    if board["prism"] is not None:
        tiles.add(board["prism"])
    if board["shard"] is not None:
        tiles.add(board["shard"])
    if board["keystone"] is not None:
        tiles.add(board["keystone"])
    return tiles

def new_player():
    player = {
        "moves_left": START_BUDGET,
        "sight": False,
        "anchor": False,
        "anchor_used": False,
    }
    reset_for_level(player, 0, (0, 0))
    return player


def reset_for_level(player, level, start):
    player["level"] = level
    player["pos"] = start
    player["walls_left"] = LEVEL_WALLS[level]
    player["hold"] = LEVEL_HOLD[level]
    player["inventory"] = []        
    player["survey_rounds"] = 0
    player["glyph_progress"] = 0
    player["walled_last_turn"] = False
    player["walled_this_turn"] = False
    player["actions_left"] = 0
    player["aim"] = None          
    player["aim_tile"] = None
    player["aim_dir"] = "h"


def begin_turn(player):
    player["actions_left"] = 1
    player["walled_this_turn"] = False


def end_turn(player):
    player["walled_last_turn"] = player["walled_this_turn"]
    player["aim"] = None
    if player["survey_rounds"] > 0:
        player["survey_rounds"] -= 1
    player["moves_left"] -= 1
    player["actions_left"] = 0

    if player["moves_left"] <= 0:
        return [("out_of_moves",)]
    return []

def move_blocked(player, board, tile):
    if not in_plane(tile, board["size"]):
        return "That's the edge of the board."
    if tile in board["collapsed"]:
        return "That tile has collapsed."
    if tile in board["door_tiles"]:
        return "The Glyph Door is sealed."
    if tile in all_walls(board):
        return "A wall is in the way."
    if tile == board["pc_pos"]:
        return "The opponent is standing there."
    return None


def step_on(player, board, tile):
    events = []
    if tile in board["pickups"]:
        if len(player["inventory"]) < player["hold"]:
            kind = board["pickups"].pop(tile)
            player["inventory"].append((kind, tile))
            events.append(("picked", kind))
        else:
            events.append(("hands_full", board["pickups"][tile]))
    if tile == board["prism"] and player["survey_rounds"] > 0 and not player["sight"]:
        player["sight"] = True
        board["prism"] = None
        events.append(("echo", "sight"))
    if tile == board["shard"] and not player["anchor"]:
        player["anchor"] = True
        board["shard"] = None
        events.append(("echo", "anchor"))
    glyphs = board["glyphs"]
    if can_see_glyphs(player) and len(board["door_tiles"]) > 0 and tile in glyphs:
        if tile == glyphs[player["glyph_progress"]]:
            player["glyph_progress"] += 1
            events.append(("glyph", player["glyph_progress"]))
            if player["glyph_progress"] == len(glyphs):
                board["door_tiles"] = set()
                events.append(("door_open",))
        else:
            if tile == glyphs[0]:
                player["glyph_progress"] = 1
            else:
                player["glyph_progress"] = 0
            events.append(("glyph_reset",))

    if tile in goal_set(board["player_goal"]):
        events.append(("won",))

    return events


def travel(player, board, path):
    for tile in path:
        reason = move_blocked(player, board, tile)
        if reason is not None:
            return False, reason, []

    events = []
    for tile in path:
        player["pos"] = tile
        events = events + step_on(player, board, tile)
        if ("won",) in events:
            break
    return True, "Moved to " + str(player["pos"]) + ".", events


def move(player, board, key):
    if player["actions_left"] <= 0:
        return False, "No actions left this turn.", []
    if key not in KEYS:
        return False, "Move with w / a / s / d.", []

    ok, msg, events = travel(player, board, [next_tile(player["pos"], key, 1)])
    if ok:
        player["actions_left"] -= 1
    return ok, msg, events

def has_route(start, goal, walls, board):
    path = get_shortest_path(start, goal_set(goal), walls, board["size"], avoid_tiles=board["collapsed"])
    return path is not None


def wall_tiles(tile, direction):
    d_row = WALL_DIRS[direction][0]
    d_col = WALL_DIRS[direction][1]
    return [tile, (tile[0] + d_row, tile[1] + d_col)]


def wall_blocked(player, board, tiles):
    for tile in tiles:
        if not in_plane(tile, board["size"]):
            return "That's off the board."
        if tile in all_walls(board) or tile in board["door_tiles"] or tile in board["collapsed"]:
            return "That spot isn't free."
        if tile == player["pos"] or tile == board["pc_pos"]:
            return "Someone is standing there."
        if tile in board["protected"] or tile in secret_tiles(board):
            return "Walls can't go here."
        if tile in board["pickups"]:
            return "Walls can't go here."

    new_walls = all_walls(board)
    for tile in tiles:
        new_walls.add(tile)
    if not has_route(player["pos"], board["player_goal"], new_walls, board):
        return "That would block your own path."
    if not has_route(board["pc_pos"], board["pc_goal"], new_walls, board):
        return "You can't fully block the opponent."
    return None


def place_wall(player, board, tile, direction):
    if player["actions_left"] <= 0:
        return False, "No actions left this turn.", []
    if player["walls_left"] <= 0:
        return False, "You have no walls left.", []
    if player["level"] == 1 and player["walled_last_turn"]:
        return False, "You placed a wall last turn, you must move this turn.", []
    if player["level"] == 3 and board["round"] > SUDDEN_DEATH_ROUND:
        return False, "Sudden Death: no more walls.", []

    if direction not in WALL_DIRS:
        return False, "Wall direction must be h or v.", []

    tiles = wall_tiles(tile, direction)
    reason = wall_blocked(player, board, tiles)
    if reason is not None:
        return False, reason, []

    for wall_tile in tiles:
        board["player_walls"][wall_tile] = board["round"]
    player["walls_left"] -= 1
    player["walled_this_turn"] = True
    player["actions_left"] -= 1
    return True, "Wall placed. " + str(player["walls_left"]) + " left.", [("wall", tiles)]

def dash(player, board, key, steps):
    if key not in KEYS or steps < 1 or steps > 2:
        return False, "Dash: give a direction (w/a/s/d) and 1 or 2.", []
    path = []
    for i in range(1, steps + 1):
        path.append(next_tile(player["pos"], key, i))
    return travel(player, board, path)


def phase_step(player, board, key):
    if key not in KEYS:
        return False, "Phase Step: give a direction (w/a/s/d).", []
    middle = next_tile(player["pos"], key, 1)
    landing = next_tile(player["pos"], key, 2)

    if middle in board["door_tiles"]:
        return False, "Phase Step can't pass the Glyph Door.", []
    if middle not in all_walls(board):
        return False, "There's no wall to phase through there.", []
    return travel(player, board, [landing])


def survey(player, board):
    player["survey_rounds"] = 2
    return True, "Survey is on for 2 rounds.", [("survey",)]


def wall_cache(player, board):
    player["walls_left"] += 1
    return True, "+1 wall. " + str(player["walls_left"]) + " left.", []


def jam(player, board):
    board["pc_jammed"] = True
    return True, "Opponent can't place walls next turn.", [("jam",)]


def dismantle(player, board, tile):
    if tile not in board["pc_walls"]:
        return False, "No enemy wall there.", []
    if distance(player["pos"], tile) > DISMANTLE_RANGE:
        return False, "Too far, Dismantle only reaches 2 tiles.", []
    del board["pc_walls"][tile]
    return True, "Removed enemy wall.", [("wall_removed", tile)]


def direction_to(start, end):
    if end > start:
        return 1
    if end < start:
        return -1
    return 0


def gravity_pull(player, board):
    p_row = player["pos"][0]
    p_col = player["pos"][1]
    e_row = board["pc_pos"][0]
    e_col = board["pc_pos"][1]
    if p_row != e_row and p_col != e_col:
        return False, "Opponent isn't in your row or column.", []

    d_row = direction_to(e_row, p_row)
    d_col = direction_to(e_col, p_col)
    destination = (e_row + d_row, e_col + d_col)
    if destination == player["pos"]:
        return False, "Opponent is already next to you.", []
    tile = destination
    while tile != player["pos"]:
        if tile in all_walls(board) or tile in board["door_tiles"] or tile in board["collapsed"]:
            return False, "Something is between you.", []
        tile = (tile[0] + d_row, tile[1] + d_col)

    board["pc_pos"] = destination
    return True, "Pulled opponent to " + str(destination) + ".", [("pc_pulled", destination)]


def wall_bomb(player, board, corner):
    if distance(player["pos"], corner) > BOMB_RANGE:
        return False, "Too far, Wall Bomb only reaches 3 tiles.", []

    row = corner[0]
    col = corner[1]
    area = [(row, col), (row, col + 1), (row + 1, col), (row + 1, col + 1)]
    hits = []
    for tile in area:
        if tile in board["pc_walls"]:
            hits.append(tile)
    if len(hits) == 0:
        return False, "No enemy walls in that area.", []

    events = []
    for i in range(min(2, len(hits))):
        oldest = hits[0]
        for tile in hits:
            if board["pc_walls"][tile] < board["pc_walls"][oldest]:
                oldest = tile
        hits.remove(oldest)
        del board["pc_walls"][oldest]
        events.append(("wall_removed", oldest))

    return True, "Destroyed " + str(len(events)) + " enemy wall(s).", events


def overclock(player, board):
    player["actions_left"] += 1
    return True, "Overclock: 1 extra action this turn.", [("overclock",)]


def use_powerup(player, board, kind, arg1=None, arg2=None):
    slot = -1
    for i in range(len(player["inventory"])):
        if player["inventory"][i][0] == kind:
            slot = i
            break
    if slot == -1:
        return False, "You aren't holding " + kind + ".", []
    if kind in USES_TURN and player["actions_left"] <= 0:
        return False, "No actions left this turn.", []

    if kind == "dash":
        ok, msg, events = dash(player, board, arg1, arg2)
    elif kind == "phase":
        ok, msg, events = phase_step(player, board, arg1)
    elif kind == "survey":
        ok, msg, events = survey(player, board)
    elif kind == "cache":
        ok, msg, events = wall_cache(player, board)
    elif kind == "jam":
        ok, msg, events = jam(player, board)
    elif kind == "dismantle":
        ok, msg, events = dismantle(player, board, arg1)
    elif kind == "pull":
        ok, msg, events = gravity_pull(player, board)
    elif kind == "bomb":
        ok, msg, events = wall_bomb(player, board, arg1)
    elif kind == "overclock":
        ok, msg, events = overclock(player, board)
    else:
        return False, "Unknown power-up.", []
    if not ok:
        return ok, msg, events

    item = player["inventory"].pop(slot)
    if kind in USES_TURN:
        player["actions_left"] -= 1
    events.append(("used", kind, item[1]))   
    return True, msg, events

def use_anchor(player, board, tile):
    if not player["anchor"]:
        return False, "You don't have the Echo of Anchor.", []
    if player["anchor_used"]:
        return False, "Anchor already used.", []
    if not in_plane(tile, board["size"]) or tile in board["collapsed"]:
        return False, "Can't anchor that tile.", []
    if distance(player["pos"], tile) > ANCHOR_RANGE:
        return False, "Too far, Anchor only reaches 3 tiles.", []

    board["anchored"].add(tile)
    player["anchor_used"] = True
    return True, "Anchored " + str(tile) + ".", [("anchored", tile)]

def survey_view(player, board):
    if player["survey_rounds"] <= 0:
        return None
    path = get_shortest_path(board["pc_pos"], goal_set(board["pc_goal"]), all_walls(board),
                             board["size"], avoid_tiles=board["collapsed"])
    return {"pc_path": path, "pc_walls_left": board["pc_walls_left"]}


def visible_secrets(player, board):
    seen = {}
    if board["prism"] is not None and player["survey_rounds"] > 0:
        seen[board["prism"]] = "prism"
    if board["shard"] is not None:
        seen[board["shard"]] = "shard"
    if can_see_glyphs(player):
        for i in range(len(board["glyphs"])):
            seen[board["glyphs"][i]] = "glyph" + str(i + 1)
    if player["sight"] and board["keystone"] is not None:
        seen[board["keystone"]] = "keystone"
    return seen

def holding(player, kind):
    for item in player["inventory"]:
        if item[0] == kind:
            return True
    return False


def aim_tiles(player):
    if player["aim"] is None:
        return []
    tile = player["aim_tile"]
    if player["aim"] == "wall":
        return wall_tiles(tile, player["aim_dir"])
    if player["aim"] == "bomb":
        return [tile, (tile[0], tile[1] + 1), (tile[0] + 1, tile[1]), (tile[0] + 1, tile[1] + 1)]
    return [tile]


def start_aim(player, kind):
    if player["actions_left"] <= 0:
        return False, "No actions left this turn.", []
    if kind == "wall" and player["walls_left"] <= 0:
        return False, "You have no walls left.", []
    if kind in ["dismantle", "bomb"] and not holding(player, kind):
        return False, "You aren't holding " + kind + ".", []
    if kind == "anchor" and (not player["anchor"] or player["anchor_used"]):
        return False, "You can't use Anchor.", []

    player["aim"] = kind
    player["aim_tile"] = player["pos"]
    player["aim_dir"] = "h"
    return True, "Aiming " + kind + ".", []


def aim_command(player, board, cmd):
    kind = player["aim"]
    tile = player["aim_tile"]

    if cmd in KEYS:
        new_tile = next_tile(tile, cmd, 1)
        if in_plane(new_tile, board["size"]):
            player["aim_tile"] = new_tile
        return True, "", []

    if cmd == "r" and kind == "wall":
        if player["aim_dir"] == "h":
            player["aim_dir"] = "v"
        else:
            player["aim_dir"] = "h"
        return True, "", []

    if cmd == "n":
        player["aim"] = None
        return True, "Cancelled.", []

    if cmd == "y":
        if kind == "wall":
            ok, msg, events = place_wall(player, board, tile, player["aim_dir"])
        elif kind == "anchor":
            ok, msg, events = use_anchor(player, board, tile)
        else:
            ok, msg, events = use_powerup(player, board, kind, tile)
        if ok:
            player["aim"] = None
        return ok, msg, events      

    return False, "Use w/a/s/d, r, y or n while aiming.", []

HELP = "Unknown command, see the controls below the board."


def handle_command(player, board, text):
    parts = text.strip().lower().split()
    if len(parts) == 0:
        return False, HELP, []
    cmd = parts[0]
    args = parts[1:]

    if player["aim"] is not None:
        return aim_command(player, board, cmd)

    if cmd in KEYS and len(args) == 0:
        return move(player, board, cmd)

    if cmd == "pass":
        player["actions_left"] = 0
        return True, "Turn passed.", []

    if cmd == "b":
        return start_aim(player, "wall")

    if cmd in ["dismantle", "bomb", "anchor"]:
        return start_aim(player, cmd)

    if cmd in ["survey", "cache", "jam", "pull", "overclock"]:
        return use_powerup(player, board, cmd)

    if cmd == "dash" and len(args) >= 1:
        steps = 2
        if len(args) > 1 and args[1].isdigit():
            steps = int(args[1])
        return use_powerup(player, board, "dash", args[0], steps)

    if cmd == "phase" and len(args) == 1:
        return use_powerup(player, board, "phase", args[0])

    return False, HELP, []