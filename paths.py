from collections import deque

DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def get_shortest_path(start, target, width, height, walls=(), extra_blocked=()):
    targets = as_cells(target)
    blocked = set(walls)
    blocked.update(extra_blocked)

    if not _inside(start, width, height):
        return None
    if start in targets:
        return [start]

    came_from = {start: None}
    queue = deque([start])
    goal = None

    while queue:
        current = queue.popleft()
        if current in targets:
            goal = current
            break
        x, y = current
        for dx, dy in DIRECTIONS:
            nxt = (x + dx, y + dy)
            if not _inside(nxt, width, height):
                continue
            if nxt in blocked:
                continue
            if nxt in came_from:
                continue
            came_from[nxt] = current
            queue.append(nxt)

    if goal is None:
        return None
    return _rebuild(came_from, goal)


def get_path_length(start, target, width, height, walls=(), extra_blocked=()):
    path = get_shortest_path(start, target, width, height, walls, extra_blocked)
    if path is None:
        return None
    return len(path) - 1


def wall_blocks_route(start, target, width, height, walls, new_wall):
    blocked = set(walls)
    blocked.add(new_wall)
    return get_shortest_path(start, target, width, height, blocked) is None
    


def reachable_cells(start, width, height, walls=(), extra_blocked=()):
    blocked = set(walls)
    blocked.update(extra_blocked)
    if not _inside(start, width, height):
        return set()
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS:
            nxt = (x + dx, y + dy)
            if not _inside(nxt, width, height):
                continue
            if nxt in blocked or nxt in seen:
                continue
            seen.add(nxt)
            queue.append(nxt)
    return seen


# --- helpers ---------------------------------------------------------

def _inside(cell, width, height):
    x, y = cell
    return 0 <= x < width and 0 <= y < height


def as_cells(target):
    if target is None:
        return set()
    if isinstance(target, tuple) and len(target) == 2 and isinstance(target[0], int):
        return {target}
    return set(target)


def _rebuild(came_from, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path