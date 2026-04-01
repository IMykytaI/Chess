"""
Constants used for the Pygame window and rendering.
"""

WIDTH: int = 512
HEIGHT: int = 512
DIMENSION: int = 8  # Chessboard is 8x8
SQ_SIZE: int = WIDTH // DIMENSION
MAX_FPS: int = 15   # For animations later

# Colors
WHITE_SQUARE: tuple = (240, 217, 181)  # Light wood/cream color
BLACK_SQUARE: tuple = (181, 136, 99)   # Dark wood color