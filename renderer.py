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

    def draw_game_state(self, screen: p.Surface, gs: GameState, sq_selected: tuple, valid_moves: list, flipped: bool = False) -> None:
        """
        The master drawing method called every single frame in the main game loop.
        The order of calling these methods is CRITICAL! 
        We must draw the board first, then highlights, and finally the pieces on top.
        """
        self._draw_board(screen, flipped)
        self._draw_highlights(screen, gs, sq_selected, flipped)
        self._draw_valid_moves(screen, valid_moves, gs.board, flipped) 
        self._draw_pieces(screen, gs.board, flipped)

    def _draw_board(self, screen: p.Surface, flipped: bool) -> None:
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

    def _draw_highlights(self, screen: p.Surface, gs: GameState, sq_selected: tuple, flipped: bool) -> None:
        """
        Draws a colored border around the square the player just clicked.
        """
        if sq_selected != ():
            row, col = sq_selected
            
            # Convert logical board coordinates to visual screen coordinates
            display_r, display_col = (7 - row, 7 - col) if flipped else (row, col)

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
                screen.blit(highlight, (display_col * c.SQ_SIZE, display_r * c.SQ_SIZE))

    def _draw_valid_moves(self, screen: p.Surface, valid_moves: list, board: List[List[Optional[Piece]]], flipped: bool) -> None:
        """
        Draws indicators showing where the currently selected piece can legally move.
        Draws a small green dot for empty squares, and a red circle for capture squares.
        """
        for move in valid_moves:
            row, col = move
            
            display_r, display_col = (7 - row, 7 - col) if flipped else (row, col)

            # Find the exact center pixel of the target square to draw our circle
            center_x = display_col * c.SQ_SIZE + c.SQ_SIZE // 2
            center_y = display_r * c.SQ_SIZE + c.SQ_SIZE // 2
            
            # If there is a piece on the destination square (it must be an enemy, as own pieces are filtered out)
            if board[row][col] is not None:
                # Draw a red ring (thickness = 4 pixels) to indicate a capture
                radius = c.SQ_SIZE // 2 - 4
                p.draw.circle(screen, p.Color('red'), (center_x, center_y), radius, 4)
            else:
                # Draw a solid dark green dot for a normal move to an empty square
                radius = c.SQ_SIZE // 6
                p.draw.circle(screen, p.Color('darkgreen'), (center_x, center_y), radius)

    def _draw_pieces(self, screen: p.Surface, board: List[List[Optional[Piece]]], flipped: bool) -> None:
        """
        Looks at the engine's board matrix and draws the corresponding pre-loaded images.
        """
        for row in range(c.DIMENSION):
            for col in range(c.DIMENSION):
                # Calculate which piece to show based on flip status
                display_row, display_col = (7 - row, 7 - col) if flipped else (row, col)
                piece = board[row][col]
                if piece is not None:
                    # 'blit' means copy pixels from one image to another (draws piece onto screen)
                    screen.blit(self.images[str(piece)], p.Rect(display_col * c.SQ_SIZE, display_row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

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


    def draw_main_menu(self, screen: p.Surface) -> tuple:
        """
        Draws the main menu with a title and buttons.
        Returns rectangles for PvP, PvE, and Quit buttons for collision detection.
        """
        # Fill the background with a solid color to hide the chessboard
        screen.fill(p.Color('dim gray'))

        # Set up fonts for the title and the buttons
        font_title = p.font.SysFont("Helvetica", 60, True, False)
        font_button = p.font.SysFont("Helvetica", 30, False, False)

        # Render and position the main title text
        text_title = font_title.render("CHESS", True, p.Color('white'))
        title_rect = p.Rect(0, 0, text_title.get_width(), text_title.get_height())
        title_rect.center = (c.WIDTH // 2, c.HEIGHT // 4)
        screen.blit(text_title, title_rect)

        # Render the 'Player vs Player' button background and text
        pvp_text = font_button.render("Player vs Player", True, p.Color('black'))
        pvp_btn = p.Rect(0, 0, 250, 50)
        pvp_btn.center = (c.WIDTH // 2, c.HEIGHT // 2)
        p.draw.rect(screen, p.Color('light gray'), pvp_btn, border_radius=10)
        screen.blit(pvp_text, (pvp_btn.centerx - pvp_text.get_width() // 2, pvp_btn.centery - pvp_text.get_height() // 2))

        # Render the 'Player vs AI' button background and text
        pve_text = font_button.render("Player vs AI", True, p.Color('black'))
        pve_btn = p.Rect(0, 0, 250, 50)
        pve_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 70)
        p.draw.rect(screen, p.Color('light gray'), pve_btn, border_radius=10)
        screen.blit(pve_text, (pve_btn.centerx - pve_text.get_width() // 2, pve_btn.centery - pve_text.get_height() // 2))

        # Render the 'Quit' button to exit the application completely
        quit_text = font_button.render("Quit", True, p.Color('black'))
        quit_btn = p.Rect(0, 0, 250, 50)
        quit_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 140)
        p.draw.rect(screen, p.Color('light gray'), quit_btn, border_radius=10)
        screen.blit(quit_text, (quit_btn.centerx - quit_text.get_width() // 2, quit_btn.centery - quit_text.get_height() // 2))

        # Return the clickable areas so the controller knows where the user clicked
        return pvp_btn, pve_btn, quit_btn

    def draw_color_menu(self, screen: p.Surface) -> tuple:
        """
        Draws the color selection menu for PvE mode.
        Returns rectangles for Play as White, Play as Black, and Back buttons.
        """
        # Clear the screen for the sub-menu
        screen.fill(p.Color('dim gray'))

        # Prepare fonts for this specific screen
        font_title = p.font.SysFont("Helvetica", 50, True, False)
        font_button = p.font.SysFont("Helvetica", 30, False, False)

        # Render and center the screen title
        text_title = font_title.render("Choose Color", True, p.Color('white'))
        title_rect = p.Rect(0, 0, text_title.get_width(), text_title.get_height())
        title_rect.center = (c.WIDTH // 2, c.HEIGHT // 4)
        screen.blit(text_title, title_rect)

        # Button for playing as White: white background, black text
        white_text = font_button.render("Play as White", True, p.Color('black'))
        white_btn = p.Rect(0, 0, 250, 50)
        white_btn.center = (c.WIDTH // 2, c.HEIGHT // 2)
        p.draw.rect(screen, p.Color('white'), white_btn, border_radius=10)
        screen.blit(white_text, (white_btn.centerx - white_text.get_width() // 2, white_btn.centery - white_text.get_height() // 2))

        # Button for playing as Black: black background, white text and border
        black_text = font_button.render("Play as Black", True, p.Color('white'))
        black_btn = p.Rect(0, 0, 250, 50)
        black_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 70)
        p.draw.rect(screen, p.Color('black'), black_btn, border_radius=10)
        p.draw.rect(screen, p.Color('white'), black_btn, border_radius=10, width=2)
        screen.blit(black_text, (black_btn.centerx - black_text.get_width() // 2, black_btn.centery - black_text.get_height() // 2))

        # Navigation button to return to the main menu without starting a game
        back_text = font_button.render("Back to Menu", True, p.Color('black'))
        back_btn = p.Rect(0, 0, 250, 50)
        back_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 140)
        p.draw.rect(screen, p.Color('light gray'), back_btn, border_radius=10)
        screen.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))

        return white_btn, black_btn, back_btn