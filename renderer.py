import pygame as p
import sys
from typing import Dict, List, Optional, Tuple
import constants as c
from engine import GameState
from pieces import Piece

class Renderer:
    """
    handles drawing everything on screen
    acts as the view in mvc architecture
    """
    def __init__(self):
        # dict to store loaded images
        self.images: Dict[str, p.Surface] = {}
        self._load_images()

    
    def draw_game_state(self, screen: p.Surface, gs: GameState, sq_selected: tuple, valid_moves: list, is_board_flipped: bool = False) -> None:
        """
        master drawing method called every frame
        order of execution is critical
        """
        self._draw_board(screen, is_board_flipped)
        self._draw_last_move(screen, gs, is_board_flipped)
        self._draw_highlights(screen, gs, sq_selected, is_board_flipped)
        self._draw_check_highlight(screen, gs, is_board_flipped) 
        self._draw_valid_moves(screen, valid_moves, gs.board, is_board_flipped)
        self._draw_pieces(screen, gs.board, is_board_flipped)

    def draw_promotion_menu(self, screen: p.Surface, color: str) -> None:
        """
        draws pop-up menu when pawn reaches final rank
        """
        overlay = p.Surface((c.WIDTH, c.HEIGHT))
        overlay.set_alpha(150) 
        overlay.fill(p.Color('black'))
        screen.blit(overlay, (0, 0))

        menu_width = 4 * c.SQ_SIZE
        start_x = (c.WIDTH - menu_width) // 2
        start_y = (c.HEIGHT - c.SQ_SIZE) // 2
        
        bg_rect = p.Rect(start_x, start_y, menu_width, c.SQ_SIZE)
        p.draw.rect(screen, p.Color('white'), bg_rect)
        p.draw.rect(screen, p.Color('black'), bg_rect, 2)

        pieces = ['Q', 'R', 'B', 'N']
        for i, piece_name in enumerate(pieces):
            image_key = f"{color}{piece_name}"
            
            icon_x = start_x + i * c.SQ_SIZE
            screen.blit(self.images[image_key], p.Rect(icon_x, start_y, c.SQ_SIZE, c.SQ_SIZE))
            
            if i > 0:
                p.draw.line(screen, p.Color('black'), (icon_x, start_y), (icon_x, start_y + c.SQ_SIZE), 2)

    def draw_main_menu(self, screen: p.Surface) -> tuple:
        """
        draws main menu and returns button rects for collision detection
        """
        screen.fill(p.Color('dim gray'))

        font_title = p.font.SysFont("Helvetica", 60, True, False)
        font_button = p.font.SysFont("Helvetica", 30, False, False)

        text_title = font_title.render("CHESS", True, p.Color('white'))
        title_rect = p.Rect(0, 0, text_title.get_width(), text_title.get_height())
        title_rect.center = (c.WIDTH // 2, c.HEIGHT // 4)
        screen.blit(text_title, title_rect)

        pvp_text = font_button.render("Player vs Player", True, p.Color('black'))
        pvp_btn = p.Rect(0, 0, 250, 50)
        pvp_btn.center = (c.WIDTH // 2, c.HEIGHT // 2)
        p.draw.rect(screen, p.Color('light gray'), pvp_btn, border_radius=10)
        screen.blit(pvp_text, (pvp_btn.centerx - pvp_text.get_width() // 2, pvp_btn.centery - pvp_text.get_height() // 2))

        pve_text = font_button.render("Player vs AI", True, p.Color('black'))
        pve_btn = p.Rect(0, 0, 250, 50)
        pve_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 70)
        p.draw.rect(screen, p.Color('light gray'), pve_btn, border_radius=10)
        screen.blit(pve_text, (pve_btn.centerx - pve_text.get_width() // 2, pve_btn.centery - pve_text.get_height() // 2))

        quit_text = font_button.render("Quit", True, p.Color('black'))
        quit_btn = p.Rect(0, 0, 250, 50)
        quit_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 140)
        p.draw.rect(screen, p.Color('light gray'), quit_btn, border_radius=10)
        screen.blit(quit_text, (quit_btn.centerx - quit_text.get_width() // 2, quit_btn.centery - quit_text.get_height() // 2))

        return pvp_btn, pve_btn, quit_btn

    def draw_color_menu(self, screen: p.Surface) -> tuple:
        """
        draws color selection menu for pve
        """
        screen.fill(p.Color('dim gray'))

        font_title = p.font.SysFont("Helvetica", 50, True, False)
        font_button = p.font.SysFont("Helvetica", 30, False, False)

        text_title = font_title.render("Choose Color", True, p.Color('white'))
        title_rect = p.Rect(0, 0, text_title.get_width(), text_title.get_height())
        title_rect.center = (c.WIDTH // 2, c.HEIGHT // 4)
        screen.blit(text_title, title_rect)

        white_text = font_button.render("Play as White", True, p.Color('black'))
        white_btn = p.Rect(0, 0, 250, 50)
        white_btn.center = (c.WIDTH // 2, c.HEIGHT // 2)
        p.draw.rect(screen, p.Color('white'), white_btn, border_radius=10)
        screen.blit(white_text, (white_btn.centerx - white_text.get_width() // 2, white_btn.centery - white_text.get_height() // 2))

        black_text = font_button.render("Play as Black", True, p.Color('white'))
        black_btn = p.Rect(0, 0, 250, 50)
        black_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 70)
        p.draw.rect(screen, p.Color('black'), black_btn, border_radius=10)
        p.draw.rect(screen, p.Color('white'), black_btn, border_radius=10, width=2)
        screen.blit(black_text, (black_btn.centerx - black_text.get_width() // 2, black_btn.centery - black_text.get_height() // 2))

        back_text = font_button.render("Back to Menu", True, p.Color('black'))
        back_btn = p.Rect(0, 0, 250, 50)
        back_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 140)
        p.draw.rect(screen, p.Color('light gray'), back_btn, border_radius=10)
        screen.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))

        return white_btn, black_btn, back_btn
    
    def draw_game_over(self, screen: p.Surface, text: str) -> None:
        """
        draws overlay with game over text
        """
        s = p.Surface((c.WIDTH, c.HEIGHT))
        s.set_alpha(180)
        s.fill(p.Color('black'))
        screen.blit(s, (0, 0))

        font = p.font.SysFont("Helvetica", 40, True, False)
        text_shadow = font.render(text, True, p.Color('black'))
        text_obj = font.render(text, True, p.Color('gold'))
        
        text_rect = text_obj.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
        shadow_rect = text_shadow.get_rect(center=(c.WIDTH // 2 + 3, c.HEIGHT // 2 + 3))
        
        screen.blit(text_shadow, shadow_rect)
        screen.blit(text_obj, text_rect)

    def draw_difficulty_menu(self, screen: p.Surface) -> tuple:
        """
        draws ai difficulty selection menu
        """
        screen.fill(p.Color('dim gray'))

        font_title = p.font.SysFont("Helvetica", 50, True, False)
        font_button = p.font.SysFont("Helvetica", 30, False, False)

        text_title = font_title.render("Choose Difficulty", True, p.Color('white'))
        title_rect = p.Rect(0, 0, text_title.get_width(), text_title.get_height())
        title_rect.center = (c.WIDTH // 2, c.HEIGHT // 4 - 30)
        screen.blit(text_title, title_rect)

        easy_text = font_button.render("Easy (Random)", True, p.Color('black'))
        easy_btn = p.Rect(0, 0, 250, 50)
        easy_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 - 40)
        p.draw.rect(screen, p.Color('light green'), easy_btn, border_radius=10)
        screen.blit(easy_text, (easy_btn.centerx - easy_text.get_width() // 2, easy_btn.centery - easy_text.get_height() // 2))

        med_text = font_button.render("Medium (Greedy)", True, p.Color('black'))
        med_btn = p.Rect(0, 0, 250, 50)
        med_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 30)
        p.draw.rect(screen, p.Color('yellow'), med_btn, border_radius=10)
        screen.blit(med_text, (med_btn.centerx - med_text.get_width() // 2, med_btn.centery - med_text.get_height() // 2))

        hard_text = font_button.render("Hard (Minimax)", True, p.Color('white'))
        hard_btn = p.Rect(0, 0, 250, 50)
        hard_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 100)
        p.draw.rect(screen, p.Color('tomato'), hard_btn, border_radius=10)
        screen.blit(hard_text, (hard_btn.centerx - hard_text.get_width() // 2, hard_btn.centery - hard_text.get_height() // 2))

        back_text = font_button.render("Back", True, p.Color('black'))
        back_btn = p.Rect(0, 0, 250, 50)
        back_btn.center = (c.WIDTH // 2, c.HEIGHT // 2 + 170)
        p.draw.rect(screen, p.Color('light gray'), back_btn, border_radius=10)
        screen.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))

        return easy_btn, med_btn, hard_btn, back_btn

    def _draw_check_highlight(self, screen: p.Surface, gs: GameState, is_board_flipped: bool) -> None:
        """
        highlights king's square in red if in check
        """
        if gs.in_check():
            king_str = 'wK' if gs.white_to_move else 'bK'
            k_row, k_col = None, None 
            
            for row in range(8):
                for col in range(8):
                    if str(gs.board[row][col]) == king_str:
                        k_row, k_col = row, col
                        break
                        
            if k_row is not None and k_col is not None:
                display_r, display_c = (7 - k_row, 7 - k_col) if is_board_flipped else (k_row, k_col)
                
                s = p.Surface((c.SQ_SIZE, c.SQ_SIZE))
                s.set_alpha(150)
                s.fill(p.Color('red'))
                screen.blit(s, (display_c * c.SQ_SIZE, display_r * c.SQ_SIZE))

    def _load_images(self) -> None:
        """
        loads pngs and scales them to fit board squares
        """
        pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            image_path = f"images/{piece}.png"
            try:
                image = p.image.load(image_path)
                self.images[piece] = p.transform.scale(image, (c.SQ_SIZE, c.SQ_SIZE))
            except FileNotFoundError:
                print(f"Error: Could not find image at {image_path}")
                sys.exit(1)

    def _draw_board(self, screen: p.Surface, flipped: bool) -> None:
        """
        draws 8x8 checkerboard background
        """
        colors = [c.WHITE_SQUARE, c.BLACK_SQUARE]
        for row in range(c.DIMENSION):
            for col in range(c.DIMENSION):
                color = colors[((row + col) % 2)]
                p.draw.rect(screen, color, p.Rect(col * c.SQ_SIZE, row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

    def _draw_highlights(self, screen: p.Surface, gs: GameState, sq_selected: tuple, flipped: bool) -> None:
        """
        draws yellow border around selected square
        """
        if sq_selected != ():
            row, col = sq_selected
            display_r, display_col = (7 - row, 7 - col) if flipped else (row, col)

            piece = gs.board[row][col]
            if piece is not None and (
                (piece.color == 'w' and gs.white_to_move) or 
                (piece.color == 'b' and not gs.white_to_move)
            ):
                highlight = p.Surface((c.SQ_SIZE, c.SQ_SIZE))
                highlight.set_alpha(100) 
                highlight.fill(p.Color('yellow'))
                screen.blit(highlight, (display_col * c.SQ_SIZE, display_r * c.SQ_SIZE))

    def _draw_valid_moves(self, screen: p.Surface, valid_moves: list, board: List[List[Optional[Piece]]], flipped: bool) -> None:
        """
        draws green dots for valid moves and red rings for captures
        """
        for move in valid_moves:
            row, col = move
            display_r, display_col = (7 - row, 7 - col) if flipped else (row, col)

            center_x = display_col * c.SQ_SIZE + c.SQ_SIZE // 2
            center_y = display_r * c.SQ_SIZE + c.SQ_SIZE // 2
            
            if board[row][col] is not None:
                radius = c.SQ_SIZE // 2 - 4
                p.draw.circle(screen, p.Color('red'), (center_x, center_y), radius, 4)
            else:
                radius = c.SQ_SIZE // 6
                p.draw.circle(screen, p.Color('darkgreen'), (center_x, center_y), radius)

    def _draw_pieces(self, screen: p.Surface, board: List[List[Optional[Piece]]], flipped: bool) -> None:
        """
        draws pieces on top of the board
        """
        for row in range(c.DIMENSION):
            for col in range(c.DIMENSION):
                display_row, display_col = (7 - row, 7 - col) if flipped else (row, col)
                piece = board[row][col]
                if piece is not None:
                    screen.blit(self.images[str(piece)], p.Rect(display_col * c.SQ_SIZE, display_row * c.SQ_SIZE, c.SQ_SIZE, c.SQ_SIZE))

    def _draw_last_move(self, screen: p.Surface, gs: GameState, flipped: bool) -> None:
        """
        highlights start and end squares of last move
        """
        if len(gs.move_log) > 0:
            last_move = gs.move_log[-1]
            start_row, start_col = last_move['start_pos']
            end_row, end_col = last_move['end_pos']

            if flipped:
                start_row, start_col = 7 - start_row, 7 - start_col
                end_row, end_col = 7 - end_row, 7 - end_col

            highlight_surface = p.Surface((c.SQ_SIZE, c.SQ_SIZE))
            highlight_surface.set_alpha(100) 
            highlight_surface.fill(p.Color('yellow')) 

            screen.blit(highlight_surface, (start_col * c.SQ_SIZE, start_row * c.SQ_SIZE))
            screen.blit(highlight_surface, (end_col * c.SQ_SIZE, end_row * c.SQ_SIZE))