import pygame as p
import constants as c
from engine import GameState
from controller import InputHandler
from renderer import Renderer
from ai import RandomAI, GreedyAI, SmartAI

def main() -> None:
    """
    main driver running the game loop
    coordinates mvc and handles screen transitions
    """
    p.init()
    screen = p.display.set_mode((c.WIDTH, c.HEIGHT))
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    
    gs = GameState()            
    input_handler = InputHandler() 
    renderer = Renderer()  

    ai = None  
    
    running = True
    
    # state machine variable for active screen
    app_state = 'main_menu'
    
    # flags for human players to block inputs during ai turns
    player_one = True # white
    player_two = True # black
    is_board_flipped = False
    
    # button collision rectangles
    pvp_btn, pve_btn, quit_btn = None, None, None
    easy_btn, med_btn, hard_btn, diff_back_btn = None, None, None, None
    white_btn, black_btn, back_btn = None, None, None

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
                
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                
                # route click based on current screen
                if app_state == 'main_menu':
                    # local pvp game
                    if pvp_btn and pvp_btn.collidepoint(location):
                        player_one = True
                        player_two = True
                        app_state = 'game'
                    # pve color selection menu
                    elif pve_btn and pve_btn.collidepoint(location):
                        app_state = 'color_menu'
                    # exit app
                    elif quit_btn and quit_btn.collidepoint(location):
                        running = False

                elif app_state == 'color_menu':
                    # human is white, ai is black
                    if white_btn and white_btn.collidepoint(location):
                        player_one = True
                        player_two = False
                        is_board_flipped = False
                        app_state = 'difficulty_menu'
                    # ai is white, human is black
                    elif black_btn and black_btn.collidepoint(location):
                        player_one = False
                        player_two = True
                        is_board_flipped = True
                        app_state = 'difficulty_menu'
                    # cancel pve and return to main
                    elif back_btn and back_btn.collidepoint(location):
                        app_state = 'main_menu'

                # difficulty menu logic
                elif app_state == 'difficulty_menu':
                    if easy_btn and easy_btn.collidepoint(location):
                        ai = RandomAI()
                        app_state = 'game'
                    elif med_btn and med_btn.collidepoint(location):
                        ai = GreedyAI()
                        app_state = 'game'
                    elif hard_btn and hard_btn.collidepoint(location):
                        # depth can be adjusted here
                        ai = SmartAI(depth=2) 
                        app_state = 'game'
                    elif diff_back_btn and diff_back_btn.collidepoint(location):
                        # go back one step
                        app_state = 'color_menu' 

                elif app_state == 'game':
                    # check if game ended
                    game_over = getattr(gs, 'checkmate', False) or getattr(gs, 'stalemate', False)
                    
                    # process board clicks only for human turn
                    human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
                    if human_turn and not game_over:
                        input_handler.handle_mouse_click(location, gs, is_board_flipped)

            elif event.type == p.KEYDOWN:
                # undo move during active game
                if event.key == p.K_z and app_state == 'game':  
                    gs.undo_move()
                    gs.update_game_status()
                    input_handler.reset_clicks()
                    
                # escape to resign and return to menu
                elif event.key == p.K_ESCAPE and app_state == 'game':
                    app_state = 'main_menu'
                    gs = GameState()
                    input_handler.reset_clicks()
                    
        # ai move logic
        if app_state == 'game':
            game_over = getattr(gs, 'checkmate', False) or getattr(gs, 'stalemate', False)
            human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
            
            if not human_turn and not game_over:
                # get move from selected ai
                ai_move = ai.get_move(gs)
                
                if ai_move:
                    start_pos, end_pos = ai_move
                    
                    # check for ai pawn promotion
                    piece = gs.board[start_pos[0]][start_pos[1]]
                    if str(piece)[1] == 'P' and (end_pos[0] == 0 or end_pos[0] == 7):
                        gs.make_move(start_pos, end_pos, promotion_choice='Q')
                    else:
                        gs.make_move(start_pos, end_pos)
                    
                    gs.update_game_status()

        # render graphics based on state
        if app_state == 'main_menu':
            pvp_btn, pve_btn, quit_btn = renderer.draw_main_menu(screen)
        elif app_state == 'color_menu':
            white_btn, black_btn, back_btn = renderer.draw_color_menu(screen)
        elif app_state == 'difficulty_menu':
            easy_btn, med_btn, hard_btn, diff_back_btn = renderer.draw_difficulty_menu(screen)
        elif app_state == 'game':
            renderer.draw_game_state(screen, gs, input_handler.sq_selected, input_handler.valid_moves, is_board_flipped)
            
            # show pawn promotion overlay
            if input_handler.is_promoting:
                start_row, start_col = input_handler.promotion_move[0]
                piece_color = gs.board[start_row][start_col].color
                renderer.draw_promotion_menu(screen, piece_color)

            # end game overlay
            if getattr(gs, 'checkmate', False):
                winner = "Black" if gs.white_to_move else "White"
                renderer.draw_game_over(screen, f"{winner} wins by Checkmate!")
            elif getattr(gs, 'stalemate', False):
                renderer.draw_game_over(screen, "Stalemate - Draw!")

        p.display.flip()
        clock.tick(c.MAX_FPS)

if __name__ == "__main__":
    main()