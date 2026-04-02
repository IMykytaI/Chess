import pygame as p
import sys
from typing import Dict, List, Optional, Tuple
import constants as c
from engine import GameState
from pieces import Piece

class Renderer:
    """
    This class is responsible for drawing everything on the screen.
    It acts as the 'View' in the MVC (Model-View-Controller) architecture.
    It takes data from the GameState (Model) and displays it visually.
    """
    def __init__(self):
        # A dictionary to store our loaded images. 
        # Key: string (e.g., 'wP'), Value: pygame image object.
        self.images: Dict[str, p.Surface] = {}
        
        # We load images only ONCE when the game starts. 
        # Loading images from the hard drive every single frame would make the game terribly slow.
        self._load_images()

    def _load_images(self) -> None:
        """
        Loads the .png files from the 'images' folder and scales them to fit our squares.
        """
        pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            image_path = f"images/{piece}.png"
            try:
                image = p.image.load(image_path)
                # Resize the image to match the exact size of one square on our board
                self.images[piece] = p.transform.scale(image, (c.SQ_SIZE, c.SQ_SIZE))
            except FileNotFoundError:
                # If an image is missing, the game will crash gracefully instead of breaking randomly later
                print(f"Error: Could not find image at {image_path}")
                sys.exit(1)

    def draw_game_state(self, screen: p.Surface, gs: GameState, sq_selected: tuple, valid_moves: list) -> None:
        """
        The master drawing method called every single frame in the main game loop.
        The order of calling these methods is CRITICAL! 
        We must draw the board first, then highlights, and finally the pieces on top.
        """
        self._draw_board(screen)
        self._draw_highlights(screen, gs, sq_selected)
        self._draw_valid_moves(screen, valid_moves, gs.board) 
        self._draw_pieces(screen, gs.board)

    def _draw_board(self, screen: p.Surface) -> None:
        """
        Draws the 8x8 checkerboard background.
        """
        colors = [c.WHITE_SQUARE, c.BLACK_SQUARE]
        for row in range(c.DIMENSION):
            for col in range(c.DIMENSION):
                # Math trick: If row + col is even, it's a light square. If odd, it's a dark square.
                color = colors[((row + col) % 2)]
                
                # Create a rectangle and draw it on the screen
                p.draw.rect(screen, color, p.Rect(col * c.SQ_SIZE, row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

    def _draw_highlights(self, screen: p.Surface, gs: GameState, sq_selected: tuple) -> None:
        """
        Draws a colored border around the square the player just clicked.
        """
        if sq_selected != ():
            row, col = sq_selected
            
            # Make sure we only highlight squares that actually have a piece belonging to the current player
            piece = gs.board[row][col]
            if piece is not None and (
                (piece.color == 'w' and gs.white_to_move) or 
                (piece.color == 'b' and not gs.white_to_move)
            ):
                # Create a special surface for transparency (alpha)
                highlight = p.Surface((c.SQ_SIZE, c.SQ_SIZE))
                highlight.set_alpha(100) # Transparency level (0 is invisible, 255 is solid)
                highlight.fill(p.Color('yellow'))
                
                # Draw the yellow highlight directly on top of the selected square
                screen.blit(highlight, (col * c.SQ_SIZE, row * c.SQ_SIZE))

    def _draw_valid_moves(self, screen: p.Surface, valid_moves: list, board: List[List[Optional[Piece]]]) -> None:
        """
        Draws indicators showing where the currently selected piece can legally move.
        Draws a small green dot for empty squares, and a red circle for capture squares.
        """
        for move in valid_moves:
            row, col = move
            
            # Find the exact center pixel of the target square to draw our circle
            center_x = col * c.SQ_SIZE + c.SQ_SIZE // 2
            center_y = row * c.SQ_SIZE + c.SQ_SIZE // 2
            
            # If there is a piece on the destination square (it must be an enemy, as own pieces are filtered out)
            if board[row][col] is not None:
                # Draw a red ring (thickness = 4 pixels) to indicate a capture
                radius = c.SQ_SIZE // 2 - 4
                p.draw.circle(screen, p.Color('red'), (center_x, center_y), radius, 4)
            else:
                # Draw a solid dark green dot for a normal move to an empty square
                radius = c.SQ_SIZE // 6
                p.draw.circle(screen, p.Color('darkgreen'), (center_x, center_y), radius)

    def _draw_pieces(self, screen: p.Surface, board: List[List[Optional[Piece]]]) -> None:
        """
        Looks at the engine's board matrix and draws the corresponding pre-loaded images.
        """
        for row in range(c.DIMENSION):
            for col in range(c.DIMENSION):
                piece = board[row][col]
                if piece is not None:
                    # 'blit' means copy pixels from one image to another (draws piece onto screen)
                    screen.blit(self.images[str(piece)], p.Rect(col * c.SQ_SIZE, row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

    def draw_promotion_menu(self, screen: p.Surface, color: str) -> None:
        """
        Draws a pop-up menu in the center of the screen when a pawn reaches the final rank.
        'color' tells us whether to display white or black pieces in the menu.
        """
        # 1. Create a semi-transparent dark background to focus attention on the menu
        overlay = p.Surface((c.WIDTH, c.HEIGHT))
        overlay.set_alpha(150) 
        overlay.fill(p.Color('black'))
        screen.blit(overlay, (0, 0))

        # 2. Calculate the size and center position for the menu box
        menu_width = 4 * c.SQ_SIZE
        start_x = (c.WIDTH - menu_width) // 2
        start_y = (c.HEIGHT - c.SQ_SIZE) // 2
        
        # 3. Draw the white background of the menu box and its black border
        bg_rect = p.Rect(start_x, start_y, menu_width, c.SQ_SIZE)
        p.draw.rect(screen, p.Color('white'), bg_rect)
        p.draw.rect(screen, p.Color('black'), bg_rect, 2)

        # 4. Draw the 4 piece choices (Queen, Rook, Bishop, Knight) inside the box
        pieces = ['Q', 'R', 'B', 'N']
        for i, piece_name in enumerate(pieces):
            # Combine color and name to fetch the right image (e.g., 'w' + 'Q' = 'wQ')
            image_key = f"{color}{piece_name}"
            
            # Calculate where to put each icon side-by-side
            icon_x = start_x + i * c.SQ_SIZE
            screen.blit(self.images[image_key], p.Rect(icon_x, start_y, c.SQ_SIZE, c.SQ_SIZE))
            
            # Draw a black line between the icons for neatness
            if i > 0:
                p.draw.line(screen, p.Color('black'), (icon_x, start_y), (icon_x, start_y + c.SQ_SIZE), 2)