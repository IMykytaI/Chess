import pygame as p
import sys
from typing import Dict

import practice11.Chess.constants as c
from practice11.Chess.engine import GameState

# Global dictionary to store images. 
# We load them only once to optimize performance.
IMAGES: Dict[str, p.Surface] = {}

def load_images() -> None:
    """
    Initialize a global directory of images.
    This will be called exactly once in the main.
    Expects images in an 'images' folder (e.g., 'images/wP.png').
    """
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        # Load the image and scale it to fit the square size
        image_path = f"images/{piece}.png"
        try:
            image = p.image.load(image_path)
            IMAGES[piece] = p.transform.scale(image, (c.SQ_SIZE, c.SQ_SIZE))
        except FileNotFoundError:
            print(f"Error: Could not find image at {image_path}")
            sys.exit(1)

def draw_game_state(screen: p.Surface, gs: GameState) -> None:
    """
    Responsible for all the graphics within a current game state.
    """
    draw_board(screen)
    draw_pieces(screen, gs.board)

def draw_board(screen: p.Surface) -> None:
    """
    Draw the squares on the board.
    The top left square is always light.
    """
    colors = [c.WHITE_SQUARE, c.BLACK_SQUARE]
    for row in range(c.DIMENSION):
        for col in range(c.DIMENSION):
            # If row + col is even, it's a light square. If odd, it's dark.
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * c.SQ_SIZE, row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

def draw_pieces(screen: p.Surface, board: list) -> None:
    """
    Draw the pieces on the board using the current GameState.board.
    """
    for row in range(c.DIMENSION):
        for col in range(c.DIMENSION):
            piece = board[row][col]
            if piece is not None:
                # Use the piece's string representation (e.g., 'wP') to get the image
                screen.blit(IMAGES[str(piece)], p.Rect(col * c.SQ_SIZE, row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

def main() -> None:
    """
    The main driver for our code. 
    This will handle user input and updating the graphics.
    """
    p.init()
    screen = p.display.set_mode((c.WIDTH, c.HEIGHT))
    p.display.set_caption("Chess Project - AI & Player")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    gs = GameState()
    load_images()
    
    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
                
        draw_game_state(screen, gs)
        clock.tick(c.MAX_FPS)
        p.display.flip()
        
    p.quit()

if __name__ == "__main__":
    main()