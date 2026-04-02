import pygame as p
import constants as c
from engine import GameState

class InputHandler:
    """
    This class acts as the 'Controller' in our MVC architecture.
    It listens to the player's mouse clicks, remembers what they selected, 
    and tells the GameState (Engine) what moves to make.
    """
    def __init__(self):
        # Stores the (row, column) of the square the player just clicked.
        # Example: (4, 3). Empty tuple () means nothing is selected.
        self.sq_selected = ()
        
        # Keeps a history of the player's clicks for the current turn.
        # 0 items: Waiting for the player to pick a piece.
        # 1 item: Piece picked, waiting for the destination square.
        # 2 items: Destination picked, time to attempt the move.
        self.player_clicks = []
        
        # When a piece is clicked, we ask the engine for its legal moves and store them here.
        # We use this to draw green dots and to verify the second click.
        self.valid_moves = []

        # --- PAWN PROMOTION STATE ---
        # A switch (True/False) that pauses the normal game to show the piece selection menu.
        self.is_promoting = False
        
        # Remembers the start and end squares of the pawn that is being promoted.
        # We need this because we have to wait for the player's menu choice before finishing the move.
        self.promotion_move = None

    def handle_mouse_click(self, location: tuple, gs: GameState) -> None:
        """
        Triggered every time the left mouse button is pressed.
        'location' is the exact (x, y) pixel coordinate of the mouse on the screen.
        """
        # 1. --- PROMOTION MENU LOGIC ---
        # If the menu is currently open, we completely ignore the chess board.
        if self.is_promoting:
            menu_width = 4 * c.SQ_SIZE
            start_x = (c.WIDTH - menu_width) // 2
            start_y = (c.HEIGHT - c.SQ_SIZE) // 2
            
            mouse_x, mouse_y = location
            
            # Check if the player clicked inside our popup menu box
            if start_y <= mouse_y <= start_y + c.SQ_SIZE and start_x <= mouse_x <= start_x + menu_width:
                # Math trick: divide the x position to figure out which of the 4 icons they clicked
                index = (mouse_x - start_x) // c.SQ_SIZE
                choices = ['Q', 'R', 'B', 'N']
                choice = choices[index]
                
                # Tell the engine to finish the saved move and spawn the new chosen piece
                gs.make_move(self.promotion_move[0], self.promotion_move[1], promotion_choice=choice)
                
                # Close the menu and go back to normal gameplay
                self.reset_clicks()
            
            # If they clicked outside the menu, just do nothing and wait for a valid click
            return 

        # 2. --- NORMAL BOARD LOGIC ---
        # Convert the pixel coordinates into grid coordinates (0 to 7)
        col = location[0] // c.SQ_SIZE
        row = location[1] // c.SQ_SIZE
        
        # If the player clicks the exact same square twice, they probably want to deselect their piece
        if self.sq_selected == (row, col):
            self.reset_clicks()
        else:
            # Save the new click and add it to our history
            self.sq_selected = (row, col)
            self.player_clicks.append(self.sq_selected)
            
            # --- FIRST CLICK (Selecting a piece) ---
            if len(self.player_clicks) == 1:
                # Ask the engine: "Where can this specific piece go safely?"
                self.valid_moves = gs.get_valid_moves_for_piece(row, col)
                
                # If they clicked an empty square or a piece with no legal moves, cancel the selection
                if not self.valid_moves:
                    self.reset_clicks()
        
        # --- SECOND CLICK (Choosing the destination) ---
        if len(self.player_clicks) == 2:
            start_pos = self.player_clicks[0]
            end_pos = self.player_clicks[1]
            
            # Check if the chosen destination is actually a legal move for this piece
            if end_pos in self.valid_moves:
                piece_to_move = gs.board[start_pos[0]][start_pos[1]]
                
                # Check if it's a Pawn ('P') that just reached the top (row 0) or bottom (row 7) edge
                if str(piece_to_move)[1] == 'P' and (end_pos[0] == 0 or end_pos[0] == 7):
                    # Freeze the board interactions and prepare to show the promotion menu
                    self.is_promoting = True
                    self.promotion_move = (start_pos, end_pos)
                else:
                    # It's a normal move. Tell the engine to update the board.
                    gs.make_move(start_pos, end_pos)
                    self.reset_clicks()
            else:
                # The player clicked an invalid destination square. Cancel the whole process.
                self.reset_clicks()

    def reset_clicks(self) -> None:
        """
        Clears all temporary data. 
        We call this when a move is successfully made, when a move is cancelled, 
        or when the player undoes a move ('Z' key).
        """
        self.sq_selected = ()
        self.player_clicks = []
        self.valid_moves = []
        self.is_promoting = False
        self.promotion_move = None