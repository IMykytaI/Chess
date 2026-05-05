import pygame as p
import constants as c
from engine import GameState

class InputHandler:
    """
    controller for MVC architecture
    listens to mouse clicks and tells the engine what to do
    """
    def __init__(self):
        # stores row and col of clicked square
        self.sq_selected = ()
        
        # history of clicks for current turn
        self.player_clicks = []
        
        # valid moves for the clicked piece
        # used to draw green dots and verify second click
        self.valid_moves = []

        # pauses normal game to show promotion menu
        self.is_promoting = False
        
        # remembers start and end squares for promotion
        # waits for menu choice before finishing move
        self.promotion_move = None

    def handle_mouse_click(self, location: tuple, gs: GameState, flipped: bool = False) -> None:
        """
        triggered on mouse click
        location is the x and y pixel coordinate
        """
        # promotion menu logic
        # ignore board if menu is open
        if self.is_promoting:
            menu_width = 4 * c.SQ_SIZE
            start_x = (c.WIDTH - menu_width) // 2
            start_y = (c.HEIGHT - c.SQ_SIZE) // 2
            
            mouse_x, mouse_y = location
            
            # check if clicked inside popup menu
            if start_y <= mouse_y <= start_y + c.SQ_SIZE and start_x <= mouse_x <= start_x + menu_width:
                # divide x position to find out which icon was clicked
                index = (mouse_x - start_x) // c.SQ_SIZE
                choices = ['Q', 'R', 'B', 'N']
                choice = choices[index]
                
                # finish move and spawn new piece
                gs.make_move(self.promotion_move[0], self.promotion_move[1], promotion_choice=choice)
                
                # close menu and resume game
                self.reset_clicks()
            
            # do nothing if clicked outside menu
            return 

        # normal board logic
        # convert pixels to grid coordinates
        col = location[0] // c.SQ_SIZE
        row = location[1] // c.SQ_SIZE
        
        # adjust coords if board is flipped
        if flipped:
            row = 7 - row
            col = 7 - col
            
        # deselect piece if clicked twice
        if self.sq_selected == (row, col):
            self.reset_clicks()
        else:
            # save click to history
            self.sq_selected = (row, col)
            self.player_clicks.append(self.sq_selected)
            
            # first click (selecting a piece)
            if len(self.player_clicks) == 1:
                # get valid moves from engine
                self.valid_moves = gs.get_valid_moves_for_piece(row, col)
                
                # cancel if empty square or no moves
                if not self.valid_moves:
                    self.reset_clicks()
        
        # second click (choosing destination)
        if len(self.player_clicks) == 2:
            start_pos = self.player_clicks[0]
            end_pos = self.player_clicks[1]
            
            # check if destination is a valid move
            if end_pos in self.valid_moves:
                piece_to_move = gs.board[start_pos[0]][start_pos[1]]
                
                # check for pawn promotion
                if str(piece_to_move)[1] == 'P' and (end_pos[0] == 0 or end_pos[0] == 7):
                    # show promotion menu
                    self.is_promoting = True
                    self.promotion_move = (start_pos, end_pos)
                else:
                    # normal move, update board
                    gs.make_move(start_pos, end_pos)
                    gs.update_game_status()
                    self.reset_clicks()
            else:
                # cancel if invalid destination
                self.reset_clicks()

    def reset_clicks(self) -> None:
        """
        clears all temporary data
        used after move is made, cancelled or undone
        """
        self.sq_selected = ()
        self.player_clicks = []
        self.valid_moves = []
        self.is_promoting = False
        self.promotion_move = None