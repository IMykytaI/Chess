import copy
from typing import List, Optional, Tuple, Dict, Any
from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King


class CastleRights:
    """
    Stores the castling rights for both players.
    True means the player still has the right to castle on that side.
    False means the right is lost forever (King moved, Rook moved, or Rook captured).
    """
    def __init__(self, wks: bool, bks: bool, wqs: bool, bqs: bool):
        self.wks = wks  # White King-Side
        self.bks = bks  # Black King-Side
        self.wqs = wqs  # White Queen-Side
        self.bqs = bqs  # Black Queen-Side


class GameState:
    """
    Stores all the information about the current state of a chess game.
    Responsible for determining valid moves at the current state, and keeping a move log.
    """
    def __init__(self):
        # The board is an 8x8 2D list. 
        # Each element is either a Piece object (e.g., Pawn, King) or None (empty square).
        self.board: List[List[Optional[Piece]]] = self._setup_board()
        
        # Keeps track of whose turn it is. True = White's turn, False = Black's turn.
        self.white_to_move: bool = True
        
        # A stack (list) that saves every move made. 
        # This is absolutely necessary for the "Undo" feature ('Z' key) and future AI calculations.
        self.move_log: List[Dict[str, Any]] = []

        # We save the exact row and column of both kings.
        # Why? Because searching the whole 8x8 board every time to find the king is too slow.
        # This allows us to check for "Check" instantly (O(1) time complexity).
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

        # Stores the coordinates of a square where an En Passant capture can happen.
        # It is empty '()' by default, but gets updated when a pawn jumps two squares forward.
        self.en_passant_possible = ()

        # Current status of castling rights for the actual board
        self.current_castling_right = CastleRights(True, True, True, True)
        
        # History of castling rights, needed to restore them exactly when a move is undone
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                               self.current_castling_right.wqs, self.current_castling_right.bqs)]

    def _update_castle_rights(self, piece_moved: Piece, piece_captured: Optional[Piece], start_col: int, end_col: int) -> None:
        """
        Updates the castling rights boolean values based on moves and captures.
        Rights are lost if the King moves, a Rook moves, or a Rook is captured.
        """
        if str(piece_moved) == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif str(piece_moved) == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
            
        elif str(piece_moved) == 'wR':
            if start_col == 0:
                self.current_castling_right.wqs = False
            elif start_col == 7:
                self.current_castling_right.wks = False
        elif str(piece_moved) == 'bR':
            if start_col == 0:
                self.current_castling_right.bqs = False
            elif start_col == 7:
                self.current_castling_right.bks = False

        if piece_captured is not None:
            if str(piece_captured) == 'wR':
                if end_col == 0:
                    self.current_castling_right.wqs = False
                elif end_col == 7:
                    self.current_castling_right.wks = False
            elif str(piece_captured) == 'bR':
                if end_col == 0:
                    self.current_castling_right.bqs = False
                elif end_col == 7:
                    self.current_castling_right.bks = False

    def _get_castle_moves(self, row: int, col: int, valid_moves: list, color: str) -> None:
        """
        Checks if castling is legally possible right now, and if so, adds the 2-square jumps to 'valid_moves'.
        Checks for empty squares and ensures the King does not jump through or into check.
        """
        if (color == 'w' and self.current_castling_right.wks) or (color == 'b' and self.current_castling_right.bks):
            if self.board[row][col + 1] is None and self.board[row][col + 2] is None:
                if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                    valid_moves.append((row, col + 2))
                    
        if (color == 'w' and self.current_castling_right.wqs) or (color == 'b' and self.current_castling_right.bqs):
            if self.board[row][col - 1] is None and self.board[row][col - 2] is None and self.board[row][col - 3] is None:
                if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                    valid_moves.append((row, col - 2))

    def _setup_board(self) -> List[List[Optional[Piece]]]:
        """
        Initializes the board with Piece objects in their starting positions.
        """
        # Create an empty 8x8 matrix filled with 'None'
        board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        
        # Place Pawns on the 2nd row (index 1 for black) and 7th row (index 6 for white)
        for col in range(8):
            board[1][col] = Pawn('b', 1, col)
            board[6][col] = Pawn('w', 6, col)

        # Place the main pieces dynamically using a list of classes
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            piece_class = piece_order[col]
            board[0][col] = piece_class('b', 0, col)
            board[7][col] = piece_class('w', 7, col)

        return board

    def make_move(self, start_pos: tuple, end_pos: tuple, promotion_choice: str = 'Q') -> None:
        """
        Executes a move on the board and updates all game variables.
        Note: This method assumes the move is completely legal (checked before calling).
        """
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Identify the piece that is moving and the piece (if any) standing on the target square
        piece_moved = self.board[start_row][start_col]
        piece_captured = self.board[end_row][end_col]
        
        if piece_moved is not None:

            # --- EN PASSANT CHECK ---
            # A move is an En Passant if a Pawn moves to the exact square saved in 'en_passant_possible'
            is_enpassant_move = (str(piece_moved)[1] == 'P' and end_pos == self.en_passant_possible)
            
            if is_enpassant_move:
                # In En Passant, the captured pawn is NOT on the target square. 
                # It is sitting right next to our pawn's starting row, but in the target column.
                piece_captured = self.board[start_row][end_col]
                # Remove the enemy pawn from the board manually
                self.board[start_row][end_col] = None
            
            # We know it's a castle move if the King jumps exactly 2 columns left or right
            is_castle_move = (str(piece_moved)[1] == 'K' and abs(start_col - end_col) == 2)

            # --- 1. UPDATE THE BOARD MATRIX ---
            # Move the piece from the old square to the new square
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = piece_moved
            
            # --- PAWN PROMOTION CHECK ---
            is_promotion = False
            # If a Pawn reaches the very top (row 0) or the very bottom (row 7)
            if str(piece_moved)[1] == 'P' and (end_row == 0 or end_row == 7):
                is_promotion = True
                # Replace the pawn object with a new powerful piece object based on player's choice
                if promotion_choice == 'Q':
                    self.board[end_row][end_col] = Queen(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'R':
                    self.board[end_row][end_col] = Rook(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'B':
                    self.board[end_row][end_col] = Bishop(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'N':
                    self.board[end_row][end_col] = Knight(piece_moved.color, end_row, end_col)


            # Move the Rook automatically if the King performed a castling move
            if is_castle_move:
                if end_col - start_col == 2: # King-side castle
                    self.board[end_row][end_col - 1] = self.board[end_row][end_col + 1]
                    self.board[end_row][end_col + 1] = None
                    self.board[end_row][end_col - 1].move(end_row, end_col - 1)
                else: # Queen-side castle
                    self.board[end_row][end_col + 1] = self.board[end_row][end_col - 2]
                    self.board[end_row][end_col - 2] = None
                    self.board[end_row][end_col + 1].move(end_row, end_col + 1)


            # --- 2. UPDATE PIECE COORDINATES ---
            # Tell the piece object its new location so it can calculate future moves correctly
            piece_moved.move(end_row, end_col)

            # --- EN PASSANT HISTORY ---
            # We must save the old 'en_passant_possible' state before changing it, so we can undo this turn later
            en_passant_log = self.en_passant_possible
            
            # Now, update 'en_passant_possible' for the NEXT player's turn.
            # If a pawn just jumped 2 squares forward...
            if str(piece_moved)[1] == 'P' and abs(start_row - end_row) == 2:
                # ...the target square for the enemy is the square right behind our jumping pawn.
                self.en_passant_possible = ((start_row + end_row) // 2, start_col)
            else:
                # If any other move is made, the right to capture En Passant is immediately lost.
                self.en_passant_possible = ()

            # Update the rights based on the piece that just moved or got captured
            self._update_castle_rights(piece_moved, piece_captured, start_col, end_col)
            # Save the newly calculated rights into our history stack
            self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                                       self.current_castling_right.wqs, self.current_castling_right.bqs))
            
            # --- 3. SAVE TO MEMORY ---
            # Pack all information about this move into a dictionary and add it to our history stack
            self.move_log.append({
                'start_pos': start_pos,
                'end_pos': end_pos,
                'piece_moved': piece_moved,
                'piece_captured': piece_captured,
                'is_promotion': is_promotion,
                'is_enpassant_move': is_enpassant_move,
                'en_passant_possible': en_passant_log,
                'is_castle_move': is_castle_move
            })
            
            # --- 4. PASS THE TURN ---
            # If it was True (White), it becomes False (Black), and vice versa.
            self.white_to_move = not self.white_to_move
            
            # --- 5. UPDATE KING TRACKERS ---
            # If the piece that just moved was a King, update its quick-lookup coordinates
            if str(piece_moved)[1] == 'K':
                if piece_moved.color == 'w':
                    self.white_king_location = (end_row, end_col)
                else:
                    self.black_king_location = (end_row, end_col)

    def undo_move(self) -> None:
        """
        Undoes the last move made in the game.
        This is used when the player presses 'Z', and also heavily used by the engine 
        to simulate future moves and check for king safety.
        """
        # We can only undo if there is at least one move in history
        if len(self.move_log) != 0:
            # Pop (remove and return) the last move from the top of the stack
            last_move = self.move_log.pop()
            
            start_row, start_col = last_move['start_pos']
            end_row, end_col = last_move['end_pos']
            piece_moved = last_move['piece_moved']
            piece_captured = last_move['piece_captured']
            
            # Restore the En Passant target square exactly as it was BEFORE this move happened
            self.en_passant_possible = last_move.get('en_passant_possible', ())
            
            # --- 1. RESTORE THE BOARD MATRIX ---
            # Put the moved piece back to its starting square
            self.board[start_row][start_col] = piece_moved
            # Put the captured piece (if any) back to the square where the move ended
            self.board[end_row][end_col] = piece_captured

            is_castle_move = last_move.get('is_castle_move', False)

            # --- UNDO EN PASSANT EXCEPTION ---
            if last_move.get('is_enpassant_move', False):
                # In En Passant, the target square was actually empty, so make it empty again
                self.board[end_row][end_col] = None 
                # And put the captured enemy pawn back beside our pawn
                self.board[start_row][end_col] = piece_captured 
                

            # Put the Rook back to its original corner if the move was a castle
            if is_castle_move:
                if end_col - start_col == 2: # King-side
                    self.board[end_row][end_col + 1] = self.board[end_row][end_col - 1]
                    self.board[end_row][end_col - 1] = None
                    self.board[end_row][end_col + 1].move(end_row, end_col + 1)
                else: # Queen-side
                    self.board[end_row][end_col - 2] = self.board[end_row][end_col + 1]
                    self.board[end_row][end_col + 1] = None
                    self.board[end_row][end_col - 2].move(end_row, end_col - 2)

            # --- 2. RESTORE PIECE COORDINATES ---
            piece_moved.move(start_row, start_col)

            # Remove the last saved rights and restore the previous state from the history stack
            self.castle_rights_log.pop()
            last_rights = self.castle_rights_log[-1]
            self.current_castling_right = CastleRights(last_rights.wks, last_rights.bks, last_rights.wqs, last_rights.bqs)
            
            # --- 3. REVERT THE TURN ---
            self.white_to_move = not self.white_to_move
            
            # --- 4. REVERT KING TRACKERS ---
            # If we are undoing a king move, put the tracker back to the old location
            if str(piece_moved)[1] == 'K':
                if piece_moved.color == 'w':
                    self.white_king_location = (start_row, start_col)
                else:
                    self.black_king_location = (start_row, start_col)

    def get_valid_moves_for_piece(self, row: int, col: int) -> list:
        """
        Returns strictly legal moves for a specific piece.
        Unlike 'get_all_possible_moves', this method guarantees that making the move 
        will not leave your own king under attack (Check).
        """
        piece = self.board[row][col]
        # If the player clicked an empty square, return an empty list
        if piece is None:
            return []
            
        # Ensure we only calculate moves for the player whose turn it currently is
        if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
            
            # Ask the piece object where it CAN go based on its movement rules (ignoring the king's safety for now)
            # IMPORTANT: Pawns need to know if there is an En Passant target available, other pieces don't care.
            if str(piece)[1] == 'P':
                pseudo_moves = piece.get_possible_moves(self.board, self.en_passant_possible)
            else:
                pseudo_moves = piece.get_possible_moves(self.board)

            valid_moves = []
            
            # Now we test every single generated move in our imagination
            for end_pos in pseudo_moves:
                # 1. Simulate the move on the real board
                self.make_move((row, col), end_pos)
                
                # 2. 'make_move' automatically gave the turn to the enemy. 
                # We switch it back temporarily because we want to check our OWN king.
                self.white_to_move = not self.white_to_move
                
                # 3. Check if our king is under attack after this simulated move
                if not self.in_check():
                    # If the king is safe, this move is 100% legal! Add it to the final list.
                    valid_moves.append(end_pos)
                    
                # 4. Give the turn back to the enemy and undo the simulated move to restore the board
                self.white_to_move = not self.white_to_move
                self.undo_move()


            # Castling is a special move because it's only valid if we are NOT currently in Check
            if str(piece)[1] == 'K' and not self.in_check():
                self._get_castle_moves(row, col, valid_moves, piece.color)
                
            return valid_moves
            
        return []
    
    def get_all_possible_moves(self) -> list:
        """
        Generates all basic moves for the current player without worrying about the King's safety.
        This is primarily used by the 'square_under_attack' method to see what squares the enemy is controlling.
        """
        moves = []
        # Loop through every single square on the 8x8 board
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece is not None:
                    # Check if the piece belongs to the active player
                    if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
                        
                        # Generate moves for this specific piece
                        if str(piece)[1] == 'P':
                            piece_moves = piece.get_possible_moves(self.board, self.en_passant_possible)
                        else:
                            piece_moves = piece.get_possible_moves(self.board)
                            
                        # Add these moves to our master list
                        moves.extend(piece_moves)
        return moves

    def in_check(self) -> bool:
        """
        Checks if the current player's King is under attack.
        """
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row: int, col: int) -> bool:
        """
        Determines if any enemy piece can move to the given (row, col) square.
        This is the core logic for detecting "Check" or preventing illegal King moves.
        """
        # Step 1: Switch the turn to see the board from the opponent's perspective
        self.white_to_move = not self.white_to_move  
        
        # Step 2: Generate all possible moves for the opponent
        opponents_moves = self.get_all_possible_moves()
        
        # Step 3: Switch the turn back to the current player
        self.white_to_move = not self.white_to_move  
        
        # Step 4: Check if the target square is inside the opponent's move list
        for move in opponents_moves:
            if move == (row, col):
                return True # An enemy can attack this square!
                
        return False # The square is safe