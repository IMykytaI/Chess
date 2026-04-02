import pygame as p
import constants as c
from engine import GameState

class InputHandler:
    """
    Handles user input and updates the game state accordingly.
    Acts as the 'Controller' in the MVC pattern.
    """
    def __init__(self):
        self.sq_selected = ()
        self.player_clicks = []
        self.valid_moves = []

        self.is_promoting = False
        self.promotion_move = None

    def handle_mouse_click(self, location: tuple, gs: GameState) -> None:
        """
        Processes a mouse click event, updating selection or attempting a move.
        """

        if self.is_promoting:
            menu_width = 4 * c.SQ_SIZE
            start_x = (c.WIDTH - menu_width) // 2
            start_y = (c.HEIGHT - c.SQ_SIZE) // 2
            mouse_x, mouse_y = location
            
            # Перевіряємо, чи клік був у межах меню
            if start_y <= mouse_y <= start_y + c.SQ_SIZE and start_x <= mouse_x <= start_x + menu_width:
                index = (mouse_x - start_x) // c.SQ_SIZE
                choices = ['Q', 'R', 'B', 'N']
                choice = choices[index]
                
                # Робимо збережений хід з обраною фігурою
                gs.make_move(self.promotion_move[0], self.promotion_move[1], promotion_choice=choice)
                self.reset_clicks()
            
            # Якщо клікнули повз меню - нічого не робимо (чекаємо вибору)
            return
        
        col = location[0] // c.SQ_SIZE
        row = location[1] // c.SQ_SIZE
        
        if self.sq_selected == (row, col):
            self.reset_clicks()
        else:
            self.sq_selected = (row, col)
            self.player_clicks.append(self.sq_selected)
            
            if len(self.player_clicks) == 1:
                self.valid_moves = gs.get_valid_moves_for_piece(row, col)
                if not self.valid_moves:
                    self.reset_clicks()
        
        if len(self.player_clicks) == 2:
            start_pos = self.player_clicks[0]
            end_pos = self.player_clicks[1]
            
            if end_pos in self.valid_moves:
                piece_to_move = gs.board[start_pos[0]][start_pos[1]]
                # Перевіряємо, чи це пішак, який дійшов до краю
                if str(piece_to_move)[1] == 'P' and (end_pos[0] == 0 or end_pos[0] == 7):
                    self.is_promoting = True
                    self.promotion_move = (start_pos, end_pos)
                else:
                    gs.make_move(start_pos, end_pos)
                    self.reset_clicks()
            else:
                # Якщо клікнули на неправильну клітинку
                self.reset_clicks()

    def reset_clicks(self) -> None:
        """
        Resets the user's click memory and highlighted moves.
        Crucial for clearing UI state after an undo action.
        """
        self.sq_selected = ()
        self.player_clicks = []
        self.valid_moves = []
        self.is_promoting = False
        self.promotion_move = None