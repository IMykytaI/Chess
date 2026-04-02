from typing import List, Tuple, Optional

class Piece:
    """
    This is the 'parent' blueprint for all chess pieces.
    It holds the shared information that every piece needs: color, row, col, and name.
    We don't actually put 'Piece' objects on the board, we only use its 'children' (Pawn, Rook, etc.).
    """
    def __init__(self, color: str, row: int, col: int, name: str):
        # 'w' for white, 'b' for black
        self.color = color
        # Current grid position on the board
        self.row = row
        self.col = col
        # The single letter that represents the piece type (e.g., 'R' for Rook)
        self.name = name

    def get_possible_moves(self, board: List[List[Optional['Piece']]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        """
        Every child piece MUST have this method, but they all calculate moves differently.
        So, we just leave it empty here and force the children to write their own rules.
        """
        raise NotImplementedError("This method must be overridden in subclasses.")
    
    def move(self, new_row: int, new_col: int) -> None:
        """
        Updates the piece's memory of where it is standing.
        Called by the engine after a move is actually made on the board.
        """
        self.row = new_row
        self.col = new_col
    
    def __str__(self) -> str:
        """
        Combines the color and the name for the engine and renderer to use.
        Example: White King becomes 'wK'.
        """
        return f"{self.color}{self.name}"


class Pawn(Piece):
    """
    The Pawn is the most complex piece because it moves differently than it captures,
    only moves forward, and has special rules like Double Jump and En Passant.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "P")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        
        # Determine the direction. White goes up the board (row index decreases: -1). Black goes down (+1).
        move_direction = -1 if self.color == 'w' else 1
        
        # Determine the starting row to check if the double jump is allowed.
        start_row = 6 if self.color == 'w' else 1
        
        # --- 1. NORMAL FORWARD MOVES ---
        # First, ensure the square right in front of the pawn is on the board
        if 0 <= self.row + move_direction < 8:
            # If the square immediately in front is completely empty
            if board[self.row + move_direction][self.col] is None:
                moves.append((self.row + move_direction, self.col))
                
                # If the first step was clear, check if we can take a SECOND step (Double Jump).
                # This is only allowed if the pawn is still on its starting row.
                if self.row == start_row and board[self.row + 2 * move_direction][self.col] is None:
                    moves.append((self.row + 2 * move_direction, self.col))
                    
        # --- 2. DIAGONAL CAPTURES ---
        # A pawn can capture left (-1) or right (+1)
        for d_col in [-1, 1]:
            target_col = self.col + d_col
            target_row = self.row + move_direction
            
            # Ensure we are not looking outside the edges of the board
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                
                # We can only move diagonally if there is a piece there AND it is an enemy
                if target_piece is not None and target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        # --- 3. EN PASSANT ---
        # The engine tells us if there is an invisible "ghost" square we can capture.
        if en_passant_possible != ():
            # The ghost square MUST be exactly one row ahead of our pawn
            if self.row + move_direction == en_passant_possible[0]:
                # And it MUST be exactly one column to our left or right
                if self.col - 1 == en_passant_possible[1] or self.col + 1 == en_passant_possible[1]:
                    moves.append(en_passant_possible)         
                    
        return moves


class Knight(Piece):
    """
    The Knight jumps in an 'L' shape and ignores pieces in between.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "N")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # These are all 8 possible 'L' shape jumps a knight can make 
        # (e.g., 2 up and 1 right, 2 down and 1 left)
        knight_jumps = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for jump in knight_jumps:
            target_row = self.row + jump[0]
            target_col = self.col + jump[1]
            
            # Make sure the landing square is inside the board
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                
                # The jump is valid if the square is empty, OR if an enemy is standing there
                if target_piece is None or target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        return moves


class Bishop(Piece):
    """
    The Bishop is a 'sliding' piece. It moves diagonally as far as it wants until it hits something.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "B")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # The 4 diagonal directions: (up-left, up-right, down-left, down-right)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for d in directions:
            # We will use a loop to keep going in this direction step by step
            for step in range(1, 8):
                target_row = self.row + d[0] * step
                target_col = self.col + d[1] * step
                
                # Stop looking in this direction if we hit the edge of the board
                if not (0 <= target_row < 8 and 0 <= target_col < 8):
                    break
                    
                target_piece = board[target_row][target_col]
                
                if target_piece is None:
                    # Empty square: we can move here, and we can keep sliding further
                    moves.append((target_row, target_col))
                elif target_piece.color != self.color:
                    # Enemy piece: we can capture it, but we CANNOT slide past it. Stop looking.
                    moves.append((target_row, target_col))
                    break
                else:
                    # Friendly piece: we can't move here, and we can't slide past it. Stop looking.
                    break
                    
        return moves


class Rook(Piece):
    """
    The Rook is a 'sliding' piece. It moves in straight lines (up, down, left, right).
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "R")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # The 4 straight directions: (up, left, down, right)
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        
        # The logic here is exactly the same as the Bishop, just with different directions
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
    The Queen is the most powerful piece. It combines the sliding powers of both the Rook and the Bishop.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "Q")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # The 8 directions: 4 straight (Rook) + 4 diagonal (Bishop)
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
    The King moves one square in any of the 8 directions.
    Note: Castling logic (рокировка) is usually handled in the engine, not here.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "K")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # The 8 adjacent squares around the King
        directions = [
            (-1, 0), (0, -1), (1, 0), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        for d in directions:
            target_row = self.row + d[0]
            target_col = self.col + d[1]
            
            # Check if the square is on the board
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                
                # The King can move there if it's empty or held by an enemy
                if target_piece is None or target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        return moves