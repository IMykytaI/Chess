import pygame as p
import constants as c
from engine import GameState
from controller import InputHandler
from renderer import Renderer

def main() -> None:
    """
    Main driver running the game loop. Coordinates Model, View, and Controller.
    """
    p.init()
    screen = p.display.set_mode((c.WIDTH, c.HEIGHT))
    p.display.set_caption("Chess Project - MVC Architecture")
    clock = p.time.Clock()
    
    # Initialize our MVC components
    gs = GameState()            # Model
    input_handler = InputHandler() # Controller
    renderer = Renderer()       # View
    
    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
                
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                input_handler.handle_mouse_click(location, gs)
                
            # ДОДАЄМО ОБРОБКУ КЛАВІАТУРИ ТУТ
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:  # Undo when 'Z' is pressed
                    gs.undo_move()
                    input_handler.reset_clicks()
                    print(f"Відміна ходу! Зараз хід білих? -> {gs.white_to_move}")

        # Draw current state and update display
        renderer.draw_game_state(screen, gs, input_handler.sq_selected, input_handler.valid_moves)
        if input_handler.is_promoting:
            start_row, start_col = input_handler.promotion_move[0]
            piece_color = gs.board[start_row][start_col].color
            renderer.draw_promotion_menu(screen, piece_color)
        
        clock.tick(c.MAX_FPS)
        p.display.flip()
        
    p.quit()

if __name__ == "__main__":
    main()