AI: Gemini
Prompt:
For our ENGG1330 project, we are developing a 2D top-down, turn-based puzzle game inspired by "Barricade". The primary objective is to navigate a grid and reach the exit before a computer-controlled opponent. The game features a tutorial followed by three progressively difficult levels, scaling from a 9x9 grid up to a 13x13 grid. Progression introduces complex mechanics, including strategic wall placement and level-specific power-ups.   A central mechanic is the "Echoes" meta-puzzle, which ties the separate levels into a cohesive campaign. Players draw from a global, shared move budget, making detours costly. While optional for beating their immediate levels, hidden "Echo" items must be collected to bypass locks in subsequent stages:   Level 1 (Open Barricade): Players use a "Survey" power-up to reveal a hidden Prism tile, which grants the Echo of Sight.   Level 2 (Shifting Barricade): The exit is blocked by a Glyph Door that requires the Echo of Sight to reveal. This level introduces neutral, moving "Patrol Walls". If a player traps a Patrol Wall for two rounds, it drops the Echo of Anchor.   Level 3 (Collapse Protocol): The board features decaying player walls and a crumbling outer ring that is removed every 5 rounds. Players must use the Echo of Sight to find the true hidden exit and the Echo of Anchor to freeze it before it collapses.   The AI opponent is designed to scale in difficulty alongside the player. While it ignores Echoes, its pathfinding logic evolves: in Level 2, it acts as an Opportunist capable of stealing power-ups like Phase Step to walk through walls, and in Level 3, it acts as a Survivalist that predicts board collapses and routes itself to safety.

~~~~~~~~~~~~~~~~~~~~~~~~
My self-breakdown:
- Writing the general bfs that can be used overall: - get_shortest_path(start, target, walls). This includes grid navigation, entity ignorance for Level I (ignoring power-ups n stepping over them), exporting data (to get the entire coordinates for shortest path so Arjith uses that for Survey)
Level 2 Opponent can steal power-ups tho.

- Writing function update_patrol_walls(patrol_state, player_walls) for the moving walls. If a patrol wall's movement is blocked by a player wall, increment a stall counter. If it is stalled for 2 rounds, it drops the Anchor shard. Return the shard so Aydhan prints it too.

- get_next_enemy_move(current, target, walls) for main's enemy steps

- Pass turn_counter into the BFS. If turn_counter ends in 4 or 9 (meaning the board collapses next turn), temporarily treat all coordinates in the outer ring as # walls. This forces the opponent to automatically route itself into the safe inner rings.

- target = gem_coordinate -> target = lockdown_node

- walls_passed, has_phase_step for shortest-path calculation to include exactly one # tile, then toggle it back to false.

Output: my README.md

_________________________

How to do the collapsing walls

Writing a test case for me