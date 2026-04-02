import pygame as p
import sys
from typing import Dict, List, Optional, Tuple
import constants as c
from engine import GameState
from pieces import Piece

class Renderer:
    def __init__(self):
        self.images: Dict[str, p.Surface] = {}
        self._load_images()

    def _load_images(self) -> None:
        pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            image_path = f"images/{piece}.png"
            try:
                image = p.image.load(image_path)
                self.images[piece] = p.transform.scale(image, (c.SQ_SIZE, c.SQ_SIZE))
            except FileNotFoundError:
                print(f"Error: Could not find image at {image_path}")
                sys.exit(1)

    # ДОДАЛИ АРГУМЕНТ valid_moves
    def draw_game_state(self, screen: p.Surface, gs: GameState, sq_selected: tuple, valid_moves: list) -> None:
        self._draw_board(screen)
        self._draw_highlights(screen, gs, sq_selected)
        # Передаємо ще й gs.board, щоб знати, де стоять фігури
        self._draw_valid_moves(screen, valid_moves, gs.board) 
        self._draw_pieces(screen, gs.board)

    # НОВИЙ МЕТОД
    def _draw_highlights(self, screen: p.Surface, gs: GameState, sq_selected: Tuple[int, int]) -> None:
        """
        Highlights the selected square.
        """
        if sq_selected != ():
            row, col = sq_selected
            # Перевіряємо, чи в цій клітинці взагалі є фігура
            if gs.board[row][col] is not None:
                # Створюємо поверхню для малювання
                surface = p.Surface((c.SQ_SIZE, c.SQ_SIZE))
                surface.set_alpha(100) # Прозорість від 0 (невидимий) до 255 (непрозорий)
                surface.fill(p.Color('blue')) # Колір підсвітки
                screen.blit(surface, (col * c.SQ_SIZE, row * c.SQ_SIZE))

    def _draw_board(self, screen: p.Surface) -> None:
        colors = [c.WHITE_SQUARE, c.BLACK_SQUARE]
        for row in range(c.DIMENSION):
            for col in range(c.DIMENSION):
                color = colors[((row + col) % 2)]
                p.draw.rect(screen, color, p.Rect(col * c.SQ_SIZE, row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

    def _draw_pieces(self, screen: p.Surface, board: List[List[Optional[Piece]]]) -> None:
        for row in range(c.DIMENSION):
            for col in range(c.DIMENSION):
                piece = board[row][col]
                if piece is not None:
                    screen.blit(self.images[str(piece)], p.Rect(col * c.SQ_SIZE, row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))


    def _draw_valid_moves(self, screen: p.Surface, valid_moves: list, board: list) -> None:
        for move in valid_moves:
            row, col = move
            center_x = col * c.SQ_SIZE + c.SQ_SIZE // 2
            center_y = row * c.SQ_SIZE + c.SQ_SIZE // 2
            
            # Якщо на клітинці є фігура (ми знаємо, що вона ворожа, бо свої ми відфільтрували)
            if board[row][col] is not None:
                # Малюємо червоне кільце (товщина 4 пікселі)
                radius = c.SQ_SIZE // 2 - 5
                p.draw.circle(screen, p.Color('red'), (center_x, center_y), radius, 4)
            else:
                # Малюємо звичайну зелену крапку для вільного ходу
                radius = c.SQ_SIZE // 6
                p.draw.circle(screen, p.Color('darkgreen'), (center_x, center_y), radius)

    def draw_promotion_menu(self, screen: p.Surface, color: str) -> None:
        """
        Малює горизонтальне меню вибору фігури по центру екрана.
        :param color: 'w' або 'b', щоб знати, які фігури малювати.
        """
        # 1. Створюємо напівпрозорий темний фон, щоб затемнити дошку
        overlay = p.Surface((c.WIDTH, c.HEIGHT))
        overlay.set_alpha(150) # Прозорість
        overlay.fill(p.Color('black'))
        screen.blit(overlay, (0, 0))

        # 2. Налаштування розмірів меню
        menu_width = 4 * c.SQ_SIZE
        start_x = (c.WIDTH - menu_width) // 2
        start_y = (c.HEIGHT - c.SQ_SIZE) // 2
        
        # 3. Малюємо біле тло меню та чорну рамку
        bg_rect = p.Rect(start_x, start_y, menu_width, c.SQ_SIZE)
        p.draw.rect(screen, p.Color('white'), bg_rect)
        p.draw.rect(screen, p.Color('black'), bg_rect, 2)

        # 4. Малюємо 4 іконки фігур
        pieces = ['Q', 'R', 'B', 'N']
        for i, piece_name in enumerate(pieces):
            piece_img = self.images[f"{color}{piece_name}"]
            img_rect = p.Rect(start_x + i * c.SQ_SIZE, start_y, c.SQ_SIZE, c.SQ_SIZE)
            screen.blit(piece_img, img_rect)
            # Малюємо розділові лінії між фігурами
            if i > 0:
                p.draw.line(screen, p.Color('black'), (start_x + i * c.SQ_SIZE, start_y), (start_x + i * c.SQ_SIZE, start_y + c.SQ_SIZE), 2)