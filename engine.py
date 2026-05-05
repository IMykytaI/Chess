import copy
from typing import List, Optional, Tuple, Dict, Any
from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King


class CastleRights:
    """
    stores castling rights for both players
    true means right is available, false means lost
    """
    def __init__(self, wks: bool, bks: bool, wqs: bool, bqs: bool):
        self.wks = wks  # white king-side
        self.bks = bks  # black king-side
        self.wqs = wqs  # white queen-side
        self.bqs = bqs  # black queen-side


class GameState:
    """
    stores all game state info
    handles valid moves and move log
    """
    def __init__(self):
        # 8x8 matrix for the board
        self.board: List[List[Optional[Piece]]] = self._setup_board()
        
        # tracks whose turn it is
        self.white_to_move: bool = True
        
        # stack to save every move made for undo and ai
        self.move_log: List[Dict[str, Any]] = []

        # track king locations for fast check evaluation
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

        # target square for en passant capture
        self.en_passant_possible = ()

        # current castling rights
        self.current_castling_right = CastleRights(True, True, True, True)
        
        # history of castling rights for undoing moves
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                               self.current_castling_right.wqs, self.current_castling_right.bqs)]
        
        # game ending flags
        self.checkmate: bool = False
        self.stalemate: bool = False

    def update_game_status(self) -> None:
        """
        scans board for valid moves across all pieces
        updates checkmate and stalemate flags
        """
        has_valid_moves = False
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None:
                    # check pieces of the active player
                    if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
                        if len(self.get_valid_moves_for_piece(r, c)) > 0:
                            has_valid_moves = True
                            break
            if has_valid_moves:
                break
                
        # if zero valid moves found across the board
        if not has_valid_moves:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

    def get_valid_moves_for_piece(self, row: int, col: int) -> list:
        """
        returns strictly legal moves for a piece
        guarantees king safety
        """
        piece = self.board[row][col]
        # return empty if clicked empty square
        if piece is None:
            return []
            
        # calculate moves only for active player
        if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
            
            # get pseudo moves from piece logic
            if str(piece)[1] == 'P':
                pseudo_moves = piece.get_possible_moves(self.board, self.en_passant_possible)
            else:
                pseudo_moves = piece.get_possible_moves(self.board)

            valid_moves = []
            
            # test every move to ensure king safety
            for end_pos in pseudo_moves:
                # simulate move
                self.make_move((row, col), end_pos)
                
                # switch turn back to check own king
                self.white_to_move = not self.white_to_move
                
                # if king is safe, move is valid
                if not self.in_check():
                    valid_moves.append(end_pos)
                    
                # revert turn and undo simulation
                self.white_to_move = not self.white_to_move
                self.undo_move()

            # check castling if king is safe
            if str(piece)[1] == 'K' and not self.in_check():
                self._get_castle_moves(row, col, valid_moves, piece.color)
            return valid_moves
            
        return []

    def make_move(self, start_pos: tuple, end_pos: tuple, promotion_choice: str = 'Q') -> None:
        """
        executes move and updates variables
        assumes move is already validated
        """
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        piece_moved = self.board[start_row][start_col]
        piece_captured = self.board[end_row][end_col]
        
        if piece_moved is not None:

            # check for en passant
            is_enpassant_move = (str(piece_moved)[1] == 'P' and end_pos == self.en_passant_possible)
            
            if is_enpassant_move:
                # captured pawn is behind target square
                piece_captured = self.board[start_row][end_col]
                self.board[start_row][end_col] = None
            
            # check for castling
            is_castle_move = (str(piece_moved)[1] == 'K' and abs(start_col - end_col) == 2)

            # update board matrix
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = piece_moved
            
            # pawn promotion check
            is_promotion = False
            if str(piece_moved)[1] == 'P' and (end_row == 0 or end_row == 7):
                is_promotion = True
                if promotion_choice == 'Q':
                    self.board[end_row][end_col] = Queen(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'R':
                    self.board[end_row][end_col] = Rook(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'B':
                    self.board[end_row][end_col] = Bishop(piece_moved.color, end_row, end_col)
                elif promotion_choice == 'N':
                    self.board[end_row][end_col] = Knight(piece_moved.color, end_row, end_col)

            # move rook for castling
            if is_castle_move:
                if end_col - start_col == 2: # king-side
                    self.board[end_row][end_col - 1] = self.board[end_row][end_col + 1]
                    self.board[end_row][end_col + 1] = None
                    self.board[end_row][end_col - 1].move(end_row, end_col - 1)
                else: # queen-side
                    self.board[end_row][end_col + 1] = self.board[end_row][end_col - 2]
                    self.board[end_row][end_col - 2] = None
                    self.board[end_row][end_col + 1].move(end_row, end_col + 1)

            # update piece coordinates
            piece_moved.move(end_row, end_col)

            # handle en passant history
            en_passant_log = self.en_passant_possible
            
            # setup new en passant square if pawn jumps 2 squares
            if str(piece_moved)[1] == 'P' and abs(start_row - end_row) == 2:
                self.en_passant_possible = ((start_row + end_row) // 2, start_col)
            else:
                self.en_passant_possible = ()

            # update castling rights and save to log
            self._update_castle_rights(piece_moved, piece_captured, start_col, end_col)
            self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                                       self.current_castling_right.wqs, self.current_castling_right.bqs))
            
            # save move to memory
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
            
            # pass turn
            self.white_to_move = not self.white_to_move
            
            # update king trackers
            if str(piece_moved)[1] == 'K':
                if piece_moved.color == 'w':
                    self.white_king_location = (end_row, end_col)
                else:
                    self.black_king_location = (end_row, end_col)

    def undo_move(self) -> None:
        """
        undoes the last move
        used for z key and ai move simulation
        """
        if len(self.move_log) != 0:
            last_move = self.move_log.pop()
            
            start_row, start_col = last_move['start_pos']
            end_row, end_col = last_move['end_pos']
            piece_moved = last_move['piece_moved']
            piece_captured = last_move['piece_captured']
            
            # restore en passant state
            self.en_passant_possible = last_move.get('en_passant_possible', ())
            
            # restore board matrix
            self.board[start_row][start_col] = piece_moved
            self.board[end_row][end_col] = piece_captured

            is_castle_move = last_move.get('is_castle_move', False)

            # undo en passant exception
            if last_move.get('is_enpassant_move', False):
                self.board[end_row][end_col] = None 
                self.board[start_row][end_col] = piece_captured 
                
            # restore rook for castling
            if is_castle_move:
                if end_col - start_col == 2: # king-side
                    self.board[end_row][end_col + 1] = self.board[end_row][end_col - 1]
                    self.board[end_row][end_col - 1] = None
                    self.board[end_row][end_col + 1].move(end_row, end_col + 1)
                else: # queen-side
                    self.board[end_row][end_col - 2] = self.board[end_row][end_col + 1]
                    self.board[end_row][end_col + 1] = None
                    self.board[end_row][end_col - 2].move(end_row, end_col - 2)

            # restore piece coordinates
            piece_moved.move(start_row, start_col)

            # restore castling rights from history
            self.castle_rights_log.pop()
            last_rights = self.castle_rights_log[-1]
            self.current_castling_right = CastleRights(last_rights.wks, last_rights.bks, last_rights.wqs, last_rights.bqs)
            
            # revert turn
            self.white_to_move = not self.white_to_move
            
            # revert king trackers
            if str(piece_moved)[1] == 'K':
                if piece_moved.color == 'w':
                    self.white_king_location = (start_row, start_col)
                else:
                    self.black_king_location = (start_row, start_col)

    def get_all_possible_moves(self) -> list:
        """
        generates basic moves ignoring king safety
        used to check controlled squares
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece is not None:
                    # check for active player
                    if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
                        
                        if str(piece)[1] == 'P':
                            piece_moves = piece.get_possible_moves(self.board, self.en_passant_possible)
                        else:
                            piece_moves = piece.get_possible_moves(self.board)
                            
                        moves.extend(piece_moves)
        return moves

    def in_check(self) -> bool:
        """
        checks if current king is under attack
        """
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row: int, col: int) -> bool:
        """
        checks if enemy can attack a specific square
        core logic for check detection
        """
        # switch to opponent view
        self.white_to_move = not self.white_to_move  
        
        opponents_moves = self.get_all_possible_moves()
        
        # switch back
        self.white_to_move = not self.white_to_move  
        
        for move in opponents_moves:
            if move == (row, col):
                return True 
                
        return False 

    def _update_castle_rights(self, piece_moved: Piece, piece_captured: Optional[Piece], start_col: int, end_col: int) -> None:
        """
        updates castling rights based on moves
        rights lost on king or rook move/capture
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
        checks if castling is legal and adds moves
        checks empty squares and check status
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
        initializes board with starting pieces
        """
        board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        
        # place pawns
        for col in range(8):
            board[1][col] = Pawn('b', 1, col)
            board[6][col] = Pawn('w', 6, col)

        # place main pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            piece_class = piece_order[col]
            board[0][col] = piece_class('b', 0, col)
            board[7][col] = piece_class('w', 7, col)

        return board