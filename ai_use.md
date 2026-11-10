# AI Use

Generative AI used: Yes

If no group member used AI, no entries are needed. Otherwise add an entry for each substantive use, including assistance with code, design, debugging, documentation or videos.

## Entry

- Member and date: Raaghav
- Tool and model/version, where available: DeepSeek
- Purpose: To refine the code's draft and scan for changes to make the program function better without bugs.
- Relevant prompts and outputs used, or retained transcript location: Prompt: 'Review and refine these files for code of a program's base grid and functionality with board restrictions and different level building.'
- Files/materials affected: grid.py, paths.py, levels.py (later replaced by level_setup.py, so these files are not in the final submission)
- What we kept, changed or rejected: Kept changes that made the program more concise, like combining 'if' statements that had the same output, and the suggestions that fixed incorrect code (e.g. paths.wall_blocks_route returned false positives, which the chatbot detected). Only about half of the suggested changes were kept.
- How we checked it; tests and corrections: Used the VS Code 'Run and Debug' option to pinpoint errors and corrected some myself. Ran the suggested changes one at a time to see whether they caused errors (some did, because of naming errors by the chatbot).

## Entry

- Member and date: Edwige
- Tool and model/version, where available: Gemini
- Purpose: Help with the opponent's logic in pc_logic.py: how to do the collapsing walls, and writing a test case.
- Relevant prompts and outputs used, or retained transcript location: Prompt gave the full game description (2D turn-based Barricade game, tutorial plus 3 levels from 9x9 to 13x13, the Echoes meta-puzzle, and an opponent that becomes an "Opportunist" in Level 2 and a "Survivalist" in Level 3). Follow-up prompts: "How to do the collapsing walls" and "Writing a test case for me". Output: README.md.
- Files/materials affected: pc_logic.py, testing.py, README.md
- What we kept, changed or rejected: My own breakdown of the functions: get_shortest_path (BFS used by everyone, also returns the full path for Survey), update_patrol_walls (stall counter, drops the Anchor shard after 2 stalls), get_next_pc_move, avoiding rings that are about to collapse, switching the target to the Keystone (lockdown_node), and has_phase_step / walls_passed so the path can go through exactly one wall. [Edwige: add what you kept, changed or rejected from Gemini's answers]
- How we checked it; tests and corrections: testing.py ("All tests passed"). [Edwige: add any corrections you made]

## Entry

- Member and date: Adhyayan 
- Tool and model/version, where available: Claude (Anthropic)
- Purpose: Building main.py and debugging imports.
- Relevant prompts and outputs used, or retained transcript location: Prompt 1: "I need a Python skeleton for a `while True` game loop that imports separate modules for grid, levels, player, pc_logic, and display. It needs to handle user input, check win/lose conditions, and update hazards." Prompt 2: "I am getting a `ModuleNotFoundError` when I try to import `grid.py` in my `main.py` in GitHub."
- Files/materials affected: main.py
- What we kept, changed or rejected: Kept the overall `while True` loop structure and the quit logic. Rejected the suggestion to use the `pygame` library, because the project must run in the terminal. Changed generic names like `state` and `enemy` to match teammates' files. Kept standard imports (`import grid`) instead of relative imports so the game runs without being set up as a package.
- How we checked it; tests and corrections: [Adhyayan: add how you tested main.py]

## Entry

- Member and date: Arjith 
- Tool and model/version, where available: Claude (Anthropic)
- Purpose: Design the "puzzle in a puzzle" (the Echoes idea), write and refine the player logic and board display, test them, and check that everyone's files work together.
- Relevant prompts and outputs used, or retained transcript location: First prompt: our game description (2D overhead room, Barricade against the computer, levels 0 to 3, each level needing something from the previous ones, a shared move budget) and asking for a puzzle that uses powers from earlier levels. Claude suggested the Echoes idea (Sight from Level 1, Anchor from Level 2, both needed in Level 3). 
- Files/materials affected: player.py.
- What we kept, changed or rejected: Claude drafted player.py and display.py from my breakdown and Edwige's pc_logic.py; I then directed every change. Used AI to:  shorten and simplify the code; and double-check that my files integrate with the sheja branch. I chose 2-tile walls instead of walls between tiles, because walls between tiles don't work with Edwige's BFS, and a cursor for placing walls instead of typing coordinates.
- How we checked it; tests and corrections: Used AI to run test cases: a test file (35 to 56 checks, run locally, not submitted) and a playable test board, to check that everything works as intended.

Keep evidence accessible to the teaching team. Remove credentials and unrelated personal information. Submit the completed file as `ai_use.md` with the project.
