import sys
import time
# Import your teammates' files (Make sure the function names match what they actually named them!)
import grid
import levels
import player
import pc_logic
import display

def main():
    # 1. Initialize the game state
    # (e.g., load level 1 from levels.py, set up the grid)
    current_level = levels.get_level(1) 
    game_state = grid.Grid(current_level)
    
    # 2. Set up the players
    human_player = player.Player(start_pos=(0,0))
    pc_opponent = pc_logic.PCOpponent(start_pos=(5,5))

    # 3. The Main Game Loop
    while True:
        # A. Render the screen
        display.render(game_state, human_player, pc_opponent)
        
        # B. Check for Game Over / Win conditions
        if game_state.is_game_over() or human_player.has_won():
            print("Game Over!")
            break
            
        # C. Get Human Input (Handling their abilities and wall placement)
        user_input = input("Enter move (WASD) or ability (1/2): ").strip().upper()
        
        if user_input == 'Q':
            print("Quitting...")
            sys.exit()
            
        # Apply human move/ability
        human_player.handle_input(user_input, game_state)
        
        # D. PC Opponent Turn
        # (This calls the BFS pathfinding your teammate wrote)
        pc_opponent.take_turn(game_state)
        
        # E. Update Environment (e.g., collapsing walls/decaying)
        game_state.update_hazards()
        
        # F. Small delay so the game isn't unplayably fast (optional)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
