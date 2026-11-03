from collections import deque

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right by 1 tile

def in_plane(tile, size):
    """
    in_plane essentially returns True if both the row and column numbers are between 0 and the board's size limit.
    It will prevent my bfs from looking for paths outside the edges of the grid.
    """
    row, col = tile
    return 0 <= row < size and 0 <= col < size



def rebuild_path(came_from, end):
    """
    Rebuild the path from the start to the end using the came_from dictionary.
    The came_from dictionary is basically a map showing all where we came from.
    Starting at the end tile, the func steps backwards until it reaches the starting point. 
    I reverse so that the result can be a coherent path from x0 to xn rather than the reverse.
    """
    path = []
    tile = end
    while tile is not None:
        path.append(tile)
        tile = came_from[tile]
    path.reverse()
    return path



def get_shortest_path(start, target, walls, size=9, has_phase_step=False, door_tiles=None, avoid_tiles=None):
    """
    First, we check if the target is one or group of tiles (e.g. an entire row), 
    converting it to a set so my bfs can easily check if it has hit a winning spot hhh.
    Using deque to check tiles in a breadth-first manner, 
    starting at the starting tile and explore all possible moves in the four cardinal directions.
    If it returns None, then we're simply boxed in.
    Power-ups are ignored in L1.
    """
    goals = {target} if isinstance(target, tuple) else set(target)
    # If goal's 1 tile (a tuple) -> set(target), else -> convert the whole bunch into a set.

    door_tiles = set(door_tiles or set())  # Glyph Door -> never passable, empty set if not on level

    if avoid_tiles:
        door_tiles |= (set(avoid_tiles) - goals)   # collapsing tiles added to door_tiles (stranger, danger).
        # - goals so that if the goal is there, we just ignore the collapse and go for it (win's a win).
    
    max_passes = 1 if has_phase_step else 0
    # If opponent has phase step, they can pass thru 1 wall, else 0 walls.

    start_state = (start, 0)  # (tile, walls_passed)

    came_from = {start_state: None}
    queue = deque([start_state])

    while queue:
        state = queue.popleft()
        current, walls_passed = state

        if current in goals:
            return [tile for tile, _ in rebuild_path(came_from, state)]

        for d_row, d_col in DIRECTIONS:
            nxt = (current[0] + d_row, current[1] + d_col)
            if not in_plane(nxt, size) or nxt in door_tiles:
                continue

            new_passed = walls_passed
            if nxt in walls:
                if walls_passed >= max_passes:
                    continue  # no Phase Step left, wall blocks us
                new_passed += 1

            new_state = (nxt, new_passed)
            if new_state not in came_from:
                came_from[new_state] = state
                queue.append(new_state)

        # Deque basically works in waves. We add the 4 neighbors to the queue then we visit the first inside (FIFO) 
        # then we add its neighbors at the back of the queuetoo but go back and visit the second in the queue bfr we get to them.
    
    return None


def get_next_pc_move(current, target, walls, size=9, **options):
    """
    Returns the single tile the opponent should step to this turn.
    If None -> opponent is stuck and should surrender? or place a wall.
    If len(path) == 1 -> opponent is already on the goal yay.
    Otherwise, return the next tile in the path.
    """
    path = get_shortest_path(current, target, walls, size, **options)

    if path is None and options.get("avoid_tiles"):
        options["avoid_tiles"] = None    # ignore the collapse if nowhere else to go.
        path = get_shortest_path(current, target, walls, size, **options)

    if path is None:
        return None
    if len(path) == 1:
        return current
    return path[1]


def update_phase_step(has_phase_step, new_tile, walls):
    """
    Calls after pc moves to make sure the Phase Step is updated.
    """
    if new_tile in walls:
        return False
    return has_phase_step

def path_length(path):
    """
    To decide if grabbing a phase step is worth it.
    """
    return None if path is None else len(path) - 1


def decide_pc_target(pc_pos, goal, powerup_pos, walls, size=11,
                     opponent_pos=None, max_detour=4, door_tiles=None):
    """
    Decides: go to the goal, or detour to grab the Phase Step first?
    If the opponent can get there first, nope.
    """

    if powerup_pos is None:
        return goal

    direct = get_shortest_path(pc_pos, goal, walls, size, door_tiles=door_tiles)
    to_powerup = get_shortest_path(pc_pos, powerup_pos, walls, size, door_tiles=door_tiles)
    from_powerup = get_shortest_path(powerup_pos, goal, walls, size,
                                     has_phase_step=True, door_tiles=door_tiles)
    
    if to_powerup is None or from_powerup is None:
        return goal

    if opponent_pos is not None:
        opponent_to_powerup = get_shortest_path(opponent_pos, powerup_pos, walls, size, door_tiles=door_tiles)
        if (opponent_to_powerup is not None
                and path_length(opponent_to_powerup) < path_length(to_powerup)):
            return goal

    detour_cost = path_length(to_powerup) + path_length(from_powerup)
    if direct is None or detour_cost <= path_length(direct) + max_detour:
        return powerup_pos
    return goal
    # max_detour ensures pc won't be delayed by >= 4 steps


def shift_tiles(tiles, direction):
    """
    Helper func to shift patrol walls since they occup > 1 tile.
    """
    return [(r + direction[0], c + direction[1]) for r, c in tiles]


def update_patrol_walls(patrol_state, opponent_walls, size=11):
    """
    Moves every patrol wall one step. If opponent wall is in the way -> stalls.
    After 2 stalls -> crystallizes into Anchor shard & position is returned, otherwise -> None.
    """
    shard = None
    remaining = []

    for patrol in patrol_state:
        new_tiles = shift_tiles(patrol["tiles"], patrol["direction"])

        # bounce off the edge of the board
        if not all(in_plane(t, size) for t in new_tiles):
            d_row, d_col = patrol["direction"]
            patrol["direction"] = (-d_row, -d_col)
            new_tiles = shift_tiles(patrol["tiles"], patrol["direction"])
            # if the new position is outta bounds, go opposite direction.

        if any(t in opponent_walls for t in new_tiles):
            patrol["stall"] += 1  # blocked by the opponent's wall, increment stall
        else:
            patrol["tiles"] = new_tiles
            patrol["stall"] = 0

        if patrol["stall"] >= 2 and shard is None:
            shard = patrol["tiles"][0]        # becomes the Anchor shard
            continue
        remaining.append(patrol)

    patrol_state[:] = remaining   # so only the non-crystallized patrols stay
    return shard


def get_patrol_tiles(patrol_state):
    """
    Since patrols count as walls for the BFS, this func returns a set of all tiles occupied by patrol walls.
    """
    return {tile for patrol in patrol_state for tile in patrol["tiles"]}


def get_ring_tiles(size, rings):
    """
    If tile distance from edge < rings, it's gon' collapse.
    """
    return {(r, c) for r in range(size) for c in range(size)
            if min(r, c, size - 1 - r, size - 1 - c) < rings}
            # formula = min(top, left, bottom, right) < rings


def get_collapsed_tiles(size, turn_counter, collapse_every=5, max_collapses=3):
    """
    To get collapsed tiles + the ring that will collapse next (rounds ending in 4 / 9 / 14).
    """
    rings = min(turn_counter // collapse_every, max_collapses)   # how many so far? capped at 3
    about_to_collapse = (turn_counter % collapse_every == collapse_every - 1)
    
    if about_to_collapse and rings < max_collapses:
        rings += 1
    
    return get_ring_tiles(size, rings)


def get_winning_goal(level, size, turn_counter, lockdown_node=None, goal_row=None):
    """
    Level 1-2: the final row. 
    Level 3: the lockdown node once the goal edge collapses.
    """
    if goal_row is None:
        goal_row = size - 1
    goal_tiles = {(goal_row, col) for col in range(size)}
    # default -> last row of the board

    if level == 3 and turn_counter >= 5 and lockdown_node is not None:
        return lockdown_node
    return goal_tiles


def get_active_walls(wall_ages, turn_counter, lifetime=8):
    """
    wall_ages is a dictionary = {tile: round_placed}. 
    Walls aged > 8 die.
    """
    return {tile for tile, placed in wall_ages.items()
            if turn_counter - placed < lifetime}


def get_overclock_moves(current, target, walls, size=13, **options):
    """
    Overclock = two enemy steps in one turn.
    """
    moves = []
    for _ in range(2):
        nxt = get_next_pc_move(current, target, walls, size, **options)
        if nxt is None or nxt == current:
            break
            # if boxed in or won, stop.
        moves.append(nxt)
        current = nxt

    return moves


def should_use_overclock(pc_path, opponent_path):
    """
    Only use it when the falling behind.
    """
    return path_length(pc_path) > path_length(opponent_path)


def can_place_wall(turn_counter, sudden_death_round=20):
    """
    opponent can place walls as long as turn_counter <= 20.
    """
    return turn_counter <= sudden_death_round


def is_wall_placement_legal(tile, walls, opponent_pos, pc_pos, opponent_goal, pc_goal, size, protected=None, door_tiles=None, avoid_tiles=None):
    
    if tile in walls or tile in (opponent_pos, pc_pos):
        return False
    # can't if wall already there or if opponent is there.

    if protected and tile in protected:
        return False
    
    new_walls = walls | {tile} # a simulation
    
    return (get_shortest_path(opponent_pos, opponent_goal, new_walls, size, door_tiles=door_tiles, avoid_tiles=avoid_tiles) is not None
            and get_shortest_path(pc_pos, pc_goal, new_walls, size, door_tiles=door_tiles, avoid_tiles=avoid_tiles) is not None)
    # Total opponent boxing in isn't allowed


def choose_wall(opponent_pos, pc_pos, opponent_goal, pc_goal, walls, size, protected=None, door_tiles=None, avoid_tiles=None, min_gain=2):
    """
    Returns the best tile to block, or None (= just move instead).
    """
    opponent_path = get_shortest_path(opponent_pos, opponent_goal, walls, size)
    pc_path = get_shortest_path(pc_pos, pc_goal, walls, size)

    if opponent_path is None or pc_path is None:
        return None
    
    if path_length(opponent_path) > path_length(pc_path):
        return None  # we're already winning

    best_tile, best_score = None, 0

    for tile in opponent_path[1:-1]:  # only try tiles on the opponent's route
        if not is_wall_placement_legal(tile, walls, opponent_pos, pc_pos,
                                       opponent_goal, pc_goal, size, protected, door_tiles=door_tiles, avoid_tiles=avoid_tiles):
            continue

        new_walls = walls | {tile}

        new_opponent_path = get_shortest_path(opponent_pos, opponent_goal, new_walls, size, door_tiles=door_tiles, avoid_tiles=avoid_tiles)
        new_pc_path = get_shortest_path(pc_pos, pc_goal, new_walls, size, door_tiles=door_tiles, avoid_tiles=avoid_tiles)

        new_opponent_len = path_length(new_opponent_path)
        new_pc_len = path_length(new_pc_path)

        if new_opponent_len is None or new_pc_len is None:
            continue

        opponent_gain = new_opponent_len - path_length(opponent_path)
        # How many extra detour steps does this wall make the opponent to take?
        
        pc_loss = new_pc_len - path_length(pc_path)
        # Does it affect my route too?

        score = opponent_gain - pc_loss  # ROI basically, weighting gains

        if score >= min_gain and score > best_score:
            best_tile, best_score = tile, score
            # best_score is best score so far, best_tile is the tile that gives that score.

    return best_tile