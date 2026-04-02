from typing import List, Optional, Tuple, Dict, Any
from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King

class GameState:
    """
    Stores all the information about the current state of a chess game.
    Responsible for determining valid moves at the current state, and keeping a move log.
    """
    def __init__(self):
        # 8x8 2D list representing the board. 
        # None represents an empty square.
        self.board: List[List[Optional[Piece]]] = self._setup_board()
        self.white_to_move: bool = True
        
        # A stack to keep track of moves. Crucial for 'Undo' and AI calculations.
        self.move_log: List[Dict[str, Any]] = []

        # New variables to track king positions for O(1) lookup
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

        self.en_passant_possible = ()

    def _setup_board(self) -> List[List[Optional[Piece]]]:
        """
        Initializes the board with Piece objects in their starting positions.
        """
        board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        
        # Place Pawns
        for col in range(8):
            board[1][col] = Pawn('b', 1, col)
            board[6][col] = Pawn('w', 6, col)

        # Place other pieces dynamically
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            piece_class = piece_order[col]
            board[0][col] = piece_class('b', 0, col)
            board[7][col] = piece_class('w', 7, col)

        return board

    def make_move(self, start_pos: tuple, end_pos: tuple, promotion_choice: str = 'Q') -> None:
        """
        Executes a move on the board. 
        Note: This does not check for move validity.
        """
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        piece_moved = self.board[start_row][start_col]
        piece_captured = self.board[end_row][end_col]
        
        if piece_moved is not None:

            # --- НОВЕ: Перевірка En Passant ---
            is_enpassant_move = (str(piece_moved)[1] == 'P' and end_pos == self.en_passant_possible)
            if is_enpassant_move:
                # Зберігаємо реального ворожого пішака, якого ми їмо (він стоїть збоку від нашого start_row)
                piece_captured = self.board[start_row][end_col]
                # Прибираємо його з дошки
                self.board[start_row][end_col] = None
            
            # 1. Update the board matrix
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = piece_moved
            
            # --- НОВЕ: Перетворення пішака ---
            is_promotion = False
            if str(piece_moved)[1] == 'P' and (end_row == 0 or end_row == 7):
                is_promotion = True
                # Замінюємо пішака на нову фігуру на дошці
                if promotion_choice == 'Q':
                    self.board[end_row][end_col] = Queen(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'R':
                    self.board[end_row][end_col] = Rook(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'B':
                    self.board[end_row][end_col] = Bishop(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'N':
                    self.board[end_row][end_col] = Knight(piece_moved.color, end_row, end_col)
            # ---------------------------------

            # 2. Update the piece's internal coordinates
            piece_moved.move(end_row, end_col)

            # --- НОВЕ: Зберігаємо старий стан En Passant для відміни ---
            en_passant_log = self.en_passant_possible
            # Якщо пішак стрибнув на 2 клітинки
            if str(piece_moved)[1] == 'P' and abs(start_row - end_row) == 2:
                # Бите поле - це клітинка між початком і кінцем
                self.en_passant_possible = ((start_row + end_row) // 2, start_col)
            else:
                # Будь-який інший хід скидає право на En Passant
                self.en_passant_possible = ()
            
            # 3. Log the move
            self.move_log.append({
                'start_pos': start_pos,
                'end_pos': end_pos,
                'piece_moved': piece_moved,
                'piece_captured': piece_captured,
                'is_promotion': is_promotion,
                'is_enpassant_move': is_enpassant_move,
                'en_passant_possible': en_passant_log
            })
            
            # 4. Switch turns
            self.white_to_move = not self.white_to_move
            
            # 5. Update king's location for O(1) check lookups
            if str(piece_moved)[1] == 'K':
                if piece_moved.color == 'w':
                    self.white_king_location = (end_row, end_col)
                else:
                    self.black_king_location = (end_row, end_col)

    def undo_move(self) -> None:
        """
        Undoes the last move made in the game.
        Crucial for move generation and the AI algorithm.
        """
        if len(self.move_log) != 0:
            last_move = self.move_log.pop()
            
            start_row, start_col = last_move['start_pos']
            end_row, end_col = last_move['end_pos']
            piece_moved = last_move['piece_moved']
            piece_captured = last_move['piece_captured']
            
            # Відновлюємо стан En Passant, який був ДО цього ходу
            self.en_passant_possible = last_move.get('en_passant_possible', ())
            
            # 1. Restore the board matrix
            self.board[start_row][start_col] = piece_moved
            self.board[end_row][end_col] = piece_captured

            # --- UNDO En Passant ---
            if last_move.get('is_enpassant_move', False):
                self.board[end_row][end_col] = None 
                self.board[start_row][end_col] = piece_captured 
                
            # 2. Restore the moved piece's internal coordinates
            piece_moved.move(start_row, start_col)
            
            # 3. Switch the turn back
            self.white_to_move = not self.white_to_move
            
            # 4. Restore king's location if the move undone was a king move
            if str(piece_moved)[1] == 'K':
                if piece_moved.color == 'w':
                    self.white_king_location = (start_row, start_col)
                else:
                    self.black_king_location = (start_row, start_col)

    def get_valid_moves_for_piece(self, row: int, col: int) -> list:
        """
        Returns strictly legal moves for the piece, 
        ensuring the move does not leave the king in check.
        """
        piece = self.board[row][col]
        if piece is None:
            return []
            
        if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
            pseudo_moves = piece.get_possible_moves(self.board)

            # --- ВАЖЛИВЕ ВИПРАВЛЕННЯ ТУТ ---
            # Передаємо en_passant_possible ТІЛЬКИ пішакам
            if str(piece)[1] == 'P':
                pseudo_moves = piece.get_possible_moves(self.board, self.en_passant_possible)
            else:
                pseudo_moves = piece.get_possible_moves(self.board)
            # -------------------------------


            valid_moves = []
            
            for end_pos in pseudo_moves:
                # 1. Make a simulated move
                self.make_move((row, col), end_pos)
                
                # 2. make_move automatically switches turns, so we switch back to check our own king
                self.white_to_move = not self.white_to_move
                
                # 3. Check if this move results in our king being attacked
                if not self.in_check():
                    valid_moves.append(end_pos)
                    
                # 4. Switch turn back and undo the simulated move
                self.white_to_move = not self.white_to_move
                self.undo_move()
                
            return valid_moves
            
        return []
    
    def get_all_possible_moves(self) -> list:
        """
        Generates all pseudo-legal moves for the current player.
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece is not None:
                    if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
                        # --- І ТАКЕ Ж ВИПРАВЛЕННЯ ТУТ ---
                        if str(piece)[1] == 'P':
                            piece_moves = piece.get_possible_moves(self.board, self.en_passant_possible)
                        else:
                            piece_moves = piece.get_possible_moves(self.board)
                        # --------------------------------
                        moves.extend(piece_moves)
        return moves

    def in_check(self) -> bool:
        """
        Determines if the current player is in check.
        """
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row: int, col: int) -> bool:
        """
        Determines if the enemy can attack the given square.
        """
        self.white_to_move = not self.white_to_move  # Switch to opponent's turn
        opponents_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # Switch back to current player
        
        for move in opponents_moves:
            if move == (row, col):
                return True
        return False