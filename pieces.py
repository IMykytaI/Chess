from typing import List, Tuple, Optional

class Piece:
    """
    base class for all chess pieces
    stores shared info like color, row, col, and name
    """
    def __init__(self, color: str, row: int, col: int, name: str):
        # w for white, b for black
        self.color = color
        # current grid position
        self.row = row
        self.col = col
        # single letter representing piece type
        self.name = name

    def get_possible_moves(self, board: List[List[Optional['Piece']]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        """
        must be implemented by child classes to calculate their specific moves
        """
        raise NotImplementedError("This method must be overridden in subclasses")
    
    def move(self, new_row: int, new_col: int) -> None:
        """
        updates piece position after a move is made
        """
        self.row = new_row
        self.col = new_col
    
    def __str__(self) -> str:
        """
        combines color and name like wK for white king
        """
        return f"{self.color}{self.name}"


class Pawn(Piece):
    """
    pawn logic including forward moves, captures, double jumps, and en passant
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "P")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        
        # white moves up (-1), black moves down (+1)
        move_direction = -1 if self.color == 'w' else 1
        
        # starting row for double jump check
        start_row = 6 if self.color == 'w' else 1
        
        # normal forward moves
        if 0 <= self.row + move_direction < 8:
            # 1 step forward if empty
            if board[self.row + move_direction][self.col] is None:
                moves.append((self.row + move_direction, self.col))
                
                # double jump if on starting row and path is clear
                if self.row == start_row and board[self.row + 2 * move_direction][self.col] is None:
                    moves.append((self.row + 2 * move_direction, self.col))
                    
        # diagonal captures
        for d_col in [-1, 1]:
            target_col = self.col + d_col
            target_row = self.row + move_direction
            
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                
                # capture if there is an enemy piece
                if target_piece is not None and target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        # en passant capture
        if en_passant_possible != ():
            # ghost square must be one row ahead
            if self.row + move_direction == en_passant_possible[0]:
                # and exactly one column left or right
                if self.col - 1 == en_passant_possible[1] or self.col + 1 == en_passant_possible[1]:
                    moves.append(en_passant_possible)         
                    
        return moves


class Knight(Piece):
    """
    knight logic for L-shaped jumps
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "N")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # all 8 possible L jumps
        knight_jumps = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for jump in knight_jumps:
            target_row = self.row + jump[0]
            target_col = self.col + jump[1]
            
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                
                # valid if empty or enemy
                if target_piece is None or target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        return moves


class Bishop(Piece):
    """
    bishop logic for diagonal sliding
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "B")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # 4 diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for d in directions:
            # keep sliding until hitting edge or piece
            for step in range(1, 8):
                target_row = self.row + d[0] * step
                target_col = self.col + d[1] * step
                
                if not (0 <= target_row < 8 and 0 <= target_col < 8):
                    break
                    
                target_piece = board[target_row][target_col]
                
                if target_piece is None:
                    # add empty square and keep sliding
                    moves.append((target_row, target_col))
                elif target_piece.color != self.color:
                    # capture enemy but stop sliding
                    moves.append((target_row, target_col))
                    break
                else:
                    # blocked by friendly piece
                    break
                    
        return moves


class Rook(Piece):
    """
    rook logic for straight sliding
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "R")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # 4 straight directions
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        
        for d in directions:
            for step in range(1, 8):
                target_row = self.row + d[0] * step
                target_col = self.col + d[1] * step
                
                if not (0 <= target_row < 8 and 0 <= target_col < 8):
                    break
                    
                target_piece = board[target_row][target_col]
                
                if target_piece is None:
                    moves.append((target_row, target_col))
                elif target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    break
                else:
                    break
                    
        return moves


class Queen(Piece):
    """
    queen logic combining rook and bishop moves
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "Q")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # 8 directions straight and diagonal
        directions = [
            (-1, 0), (0, -1), (1, 0), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        for d in directions:
            for step in range(1, 8):
                target_row = self.row + d[0] * step
                target_col = self.col + d[1] * step
                
                if not (0 <= target_row < 8 and 0 <= target_col < 8):
                    break
                    
                target_piece = board[target_row][target_col]
                
                if target_piece is None:
                    moves.append((target_row, target_col))
                elif target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    break
                else:
                    break
                    
        return moves


class King(Piece):
    """
    king logic for 1 step in any direction
    castling is handled in engine
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "K")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # 8 adjacent squares
        directions = [
            (-1, 0), (0, -1), (1, 0), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        for d in directions:
            target_row = self.row + d[0]
            target_col = self.col + d[1]
            
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                
                # valid if empty or enemy
                if target_piece is None or target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        return moves