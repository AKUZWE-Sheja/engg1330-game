import sys
import time
import os

import grid
import levels
import player
import display
import pc_logic

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # 1. Load all levels using levels.py
    all_boards = levels.build_all()
    
    # 2. Initialize the player
    human = player.new_player()
    
    # Start at Level 0 (Tutorial)
    current_level_index = 0
    board_obj = all_boards[current_level_index]
    
    # Reset player for the current level
    start_pos = board_obj.actors.get("player", (4, 7))
    player.reset_for_level(human, current_level_index, start_pos)
    
    # The pc_logic.py and player.py are slightly disconnected. 
    # We set up a basic PC position (usually the goal area)
    pc_start = board_obj.meta.get("pc_start", (0, 0))
    board_obj.actors["pc"] = pc_start

    # 3. The Main Game Loop
    while True:
        clear_screen()
        display.draw_key()
        
        # Convert the Board class into the Dictionary format that player.py expects
        board_dict = {
            "size": board_obj.width,
            "player_walls": {k: v for k, v in board_obj.walls.items() if v == "player"},
            "pc_walls": {k: v for k, v in board_obj.walls.items() if v == "pc"},
            "neutral_walls": set(),
            "collapsed": board_obj.collapsed,
            "door_tiles": board_obj.exits if board_obj.sealed else set(),
            "pickups": board_obj.pickups,
            "prism": None,
            "shard": None,
            "keystone": None,
            "glyphs": [],
            "player_goal": board_obj.exits,
            "pc_goal": set(), # Add PC goal logic later if needed
            "pc_pos": board_obj.actors.get("pc", (0,0)),
            "round": 1,
            "pc_walls_left": 5,
            "protected": set(),
            "anchored": set(),
            "pc_jammed": False
        }

        # Display the board using display.py
        display.draw_board(human, board_dict)
        display.draw_controls(human)
        
        # Get user input
        user_input = input("\nEnter command (or 'q' to quit): ").strip().lower()
        
        if user_input == 'q':
            print("Quitting...")
            sys.exit()

        # Handle the player's move using player.py
        player.begin_turn(human)
        success, message, events = player.handle_command(human, board_dict, user_input)
        
        # Update the original board object with any changes made
        board_obj.walls.update({k: "player" for k in board_dict["player_walls"]})
        board_obj.pickups = board_dict["pickups"]
        
        print("\n" + message)
        
        # Check win condition
        if ("won",) in events:
            print("You won the level!")
            current_level_index += 1
            if current_level_index >= len(all_boards):
                print("Congratulations, you beat the game!")
                break
            else:
                board_obj = all_boards[current_level_index]
                start_pos = board_obj.actors.get("player", (4, 7))
                player.reset_for_level(human, current_level_index, start_pos)
            input("Press Enter to continue...")
            continue

        player.end_turn(human)
        
        # PC Turn (Basic implementation)
        # Note: Your pc_logic.py functions are written for a different board format, 
        # so for now, we simulate a simple move so the game doesn't crash.
        if success:
            # Simulate PC moving randomly for now
            pc_pos = board_obj.actors.get("pc", (0,0))
            if pc_pos[0] < board_obj.height - 1:
                board_obj.actors["pc"] = (pc_pos[0] + 1, pc_pos[1])
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
