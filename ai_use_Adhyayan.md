# AI Usage Log - Team eng1330-game

## Person 4: Main Game Loop & Integration

### Task: Building `main.py`
**Prompt Used:** 
"I need a Python skeleton for a `while True` game loop that imports separate modules for grid, levels, player, pc_logic, and display. It needs to handle user input, check win/lose conditions, and update hazards."

**AI Output Summary:**
The AI generated a basic `main.py` file that initialized the game state, created a `while True` loop, called a display function, asked for user input (WASD), called the PC opponent's turn, and updated the environment.

**What was Kept:**
- The overall structure of the `while True` loop.
- The `sys.exit()` logic for quitting the game.
- The `time.sleep(0.1)` to prevent the terminal from flashing too fast.

**What was Rejected/Modified:**
- **Rejected:** The AI originally suggested using the `pygame` library for the display. We rejected this because our project requires a terminal-based interface.
- **Modified:** The AI used generic variable names like `state` and `enemy`. I modified these to match my teammates' actual file names and classes (e.g., changing `enemy` to `pc_opponent` to match `pc_logic.py`).
- **Modified:** The AI didn't include the hazard update step. I added `game_state.update_hazards()` to the loop so the collapsing walls actually update every turn.

### Task: Debugging Imports
**Prompt Used:**
"I am getting a `ModuleNotFoundError` when I try to import `grid.py` in my `main.py` in GitHub."

**AI Output Summary:**
The AI explained that Python needs the files to be in the same directory and explained how relative imports work.

**What was Kept:**
I kept the standard import method (e.g., `import grid`) instead of relative imports (`from . import grid`) so it runs easily on our local machines without needing to run it as a package.
