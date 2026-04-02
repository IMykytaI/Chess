import pygame as p
import constants as c
from engine import GameState
from controller import InputHandler
from renderer import Renderer

def main() -> None:
    """
    This is the main driver of our game. 
    It brings the Model, View, and Controller together and runs the infinite game loop.
    """
    # --- 1. INITIALIZATION ---
    p.init()
    screen = p.display.set_mode((c.WIDTH, c.HEIGHT))
    p.display.set_caption("Chess Project - MVC Architecture")
    
    # Use a clock to control how fast our game runs (Frames Per Second)
    clock = p.time.Clock()
    
    # Initialize our three main MVC components
    gs = GameState()               # The Engine (Model): knows the rules and current state
    input_handler = InputHandler() # The Controller: handles clicks and logic decisions
    renderer = Renderer()          # The View: handles drawing pictures on the screen
    
    running = True
    
    # --- 2. THE MAIN GAME LOOP ---
    # This loop runs constantly (e.g., 15 times a second) until the player closes the window
    while running:
        
        # Look at every event (action) that happened since the last frame
        for event in p.event.get():
            
            # Event: Player clicked the 'X' to close the window
            if event.type == p.QUIT:
                running = False
                
            # Event: Player clicked the mouse
            elif event.type == p.MOUSEBUTTONDOWN:
                # Get the exact pixel coordinates of the mouse on the screen
                location = p.mouse.get_pos()
                # Pass these coordinates to our Controller to figure out what to do
                input_handler.handle_mouse_click(location, gs)
                
            # Event: Player pressed a key on the keyboard
            elif event.type == p.KEYDOWN:
                # If the key pressed was 'Z'
                if event.key == p.K_z:
                    gs.undo_move()
                    # We must tell the controller to forget any half-made clicks 
                    # (like if the player clicked a piece, then pressed 'Z' before finishing the move)
                    input_handler.reset_clicks()
                    print(f"Відміна ходу! Зараз хід білих? -> {gs.white_to_move}")

        # --- 3. DRAWING PHASE ---
        # Tell the View to draw the current state of the board, highlights, and valid moves
        renderer.draw_game_state(screen, gs, input_handler.sq_selected, input_handler.valid_moves)
        
        # If the controller says we are currently choosing a piece for promotion,
        # draw the popup menu ON TOP of the board.
        if input_handler.is_promoting:
            start_row, start_col = input_handler.promotion_move[0]
            piece_color = gs.board[start_row][start_col].color
            renderer.draw_promotion_menu(screen, piece_color)

        # Wait a tiny bit so the loop doesn't run infinitely fast and fry the CPU
        clock.tick(c.MAX_FPS)
        
        # Tell Pygame to update the physical screen with all the new drawings
        p.display.flip()

if __name__ == "__main__":
    main()