from dataclasses import dataclass, field

import paths

icons = {
    "player": " 🔴 ",
    "pc": " 🔵 ",
    "player_wall": " 🟥 ",
    "pc_wall": " 🟦 ",
    "patrol": " 🚧 ",
    "pickup": " 🎁 ",
    "aim": " 🟫 ",
    "glyph1": " 1️⃣ ",
    "glyph2": " 2️⃣ ",
    "glyph3": " 3️⃣ ",
    "prism": " 💎 ",
    "shard": " 🔷 ",
    "keystone": " 🔑 ",
    "collapsed": "    ",
    "empty": " ⬛ ",
}

icons["coin"] = " 🪙 "
icons["exit"] = " 🏁 "
icons["sealed"] = " 🔒 "
icons["fixed_wall"] = " ⬜ "

""" used when a terminal renders the keycap glyphs at a different width
which shifts whole rows. Call use_plain_icons() to switch."""
PLAIN_ICONS = {
    "player": " P ", "pc": " C ", "player_wall": " # ", "pc_wall": " = ",
    "patrol": " ! ", "pickup": " $ ", "aim": " : ", "glyph1": " 1 ",
    "glyph2": " 2 ", "glyph3": " 3 ", "prism": " * ", "shard": " o ",
    "keystone": " K ", "collapsed": "   ", "empty": " . ", "coin": " c ",
    "exit": " E ", "sealed": " L ", "fixed_wall": " X ",
}


def use_plain_icons():
    icons.clear()
    icons.update(PLAIN_ICONS)


LEGEND_LINES = (
    "🔴 player  🔵 pc  🟥 player wall  🟦 pc wall  🚧 patrol  ⬜ fixed wall",
    "🎁 pickup  💎 prism  🔷 shard  🔑 keystone  🏁 exit  🔒 sealed  🪙 coin  🟫 path",
)


class Board:
    def __init__(self, index, width, height, name=""):
        if width < 3 or height < 3:
            raise ValueError("board must be at least 3x3")
        self.index = index
        self.width = width
        self.height = height
        self.name = name
        self.meta = {}

        self.walls = {}
        self.collapsed = set()
        self.pickups = {}
        self.hidden = {}
        self.exists = set()
        self.sealed = False
        self.actors = {}
        self.patrols = []
        self.path_cells = set()
        self.aim = None

    # --- queries ------------------------------------------------------
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def patrol_cells(self):
        cells = set()
        for patrol in self.patrols:
            cells.add(patrol["path"][patrol["i"]])
        return cells

    def wall_cells(self):
        blocked = set(self.walls)
        blocked.update(self.collapsed)
        blocked.update(self.patrol_cells())
        if self.sealed:
            blocked.update(self.exits)
        return blocked

    def is_wall(self, x, y):
        return (x, y) in self.wall_cells()

    def is_open(self, x, y):
        return self.in_bounds(x, y) and not self.is_wall(x, y)

    def route(self, start, target):
        return paths.get_shortest_path(
            start, target, self.width, self.height, self.wall_cells())

    def wall_blocks_route(self, start, target, x, y):
        return paths.wall_blocks_route(
            start, target, self.width, self.height, self.wall_cells(), (x, y))

    def can_place_wall(self, x, y, mover="player", target=None):
        if not self.in_bounds(x, y):
            return False
        cell = (x, y)
        if cell in self.wall_cells() or cell in self.exists or cell in self.pickups:
            return False
        for pos in self.actors.values():
            if pos == cell:
                return False
        if target is not None:
            start = self.actors.get(mover)
            if start is not None and self.wall_blocks_route(start, target, x, y):
                return False
        return True

    def place_wall(self, x, y, owner="player"):
        if not self.can_place_wall(x, y):
            raise ValueError("cannot place a wall at ({0}, {1})".format(x, y))
        self.walls[(x, y)] = owner

    def reveal(self, echo):
        for cell in list(self.hidden):
            if self.hidden[cell] == echo:
                del self.hidden[cell]

    def add_patrol(self, path):
        if len(path) < 2:
            raise ValueError("patrol path needs at least 2 cells")
        self.patrols.append({"path": list(path), "i": 0})

    def advance_patrols(self):
        for patrol in self.patrols:
            patrol["i"] = (patrol["i"] + 1) % len(patrol["path"])

    def set_path(self, path):
        self.path_cells = set()
        if not path:
            return
        for cell in path[1:-1]:
            self.path_cells.add(cell)

    def icon_at(self, x, y, reveal_all=False):
        cell = (x, y)
        if self.actors.get("player") == cell:
            return "player"
        if self.actors.get("pc") == cell:
            return "pc"
        if cell in self.collapsed:
            return "collapsed"
        if cell in self.walls:
            owner = self.walls[cell]
            if owner == "player":
                return "player_wall"
            if owner == "pc":
                return "pc_wall"
            return "fixed_wall"
        if cell in self.patrol_cells():
            return "patrol"
        if cell in self.hidden and not reveal_all:
            return "empty"
        if cell in self.pickups:
            return self.pickups[cell]
        if cell in self.exits:
            if self.sealed:
                return "sealed"
            return "exit"
        if cell == self.aim:
            return "aim"
        if cell in self.path_cells:
            return "aim"
        return "empty"

    def render(self, reveal_all=False):
        lines = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(icons[self.icon_at(x, y, reveal_all)])
            lines.append("".join(row))
        return lines

    def screen(self, status="", reveal_all=False):
        """Board+header+status+legend. 18 lines for a 13x13 board
            so it always fits an 80x24 terminal."""
        lines = []
        lines.append("Barricade: Echoes   Level {0}: {1}   {2}x{3}".format(
            self.index, self.name, self.width, self.height))
        lines.append(status)
        lines.extend(self.render(reveal_all))
        lines.append("")
        lines.extend(LEGEND_LINES)
        return lines