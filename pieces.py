from typing import List, Tuple, Optional

class Piece:
    """
    Abstract base class representing a generic chess piece.
    """
    def __init__(self, color: str, row: int, col: int, name: str):
        """
        Initialize a chess piece.
        
        :param color: 'w' for white, 'b' for black.
        :param row: Current row index on the board (0-7).
        :param col: Current column index on the board (0-7).
        :param name: Piece identifier (e.g., 'R' for Rook, 'N' for Knight).
        """
        self.color = color
        self.row = row
        self.col = col
        self.name = name

    def get_possible_moves(self, board: List[List[Optional['Piece']]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        """
        Generate all pseudo-legal moves for this piece based on the board state.
        
        :param board: 2D list representing the current state of the chessboard.
        :return: List of tuples representing valid (row, col) destination coordinates.
        """
        raise NotImplementedError("This method must be overridden in subclasses.")
    
    def move (self, new_row: int, new_col: int) -> None:
        """
        Update the piece's coordinates.
        """
        self.row = new_row
        self.col = new_col
    
    def __str__(self) -> str:
        """
        String representation of the piece (e.g., 'wR' for White Rook).
        """
        return f"{self.color}{self.name}"
    
class Rook(Piece):
    """
    Represents a Rook piece.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "R")
    

    def get_possible_moves(self, board: List[List[Optional[Piece]]],en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []

        directions = [(-1,0),(1,0),(0,-1),(0,1)]

        for d_row, d_col in directions:
            current_row, current_col = self.row + d_row, self.col + d_col

            while 0<=current_row<8 and 0<=current_col<8:
                target_piece = board[current_row][current_col]

                if target_piece is None:
                    moves.append((current_row,current_col))

                elif target_piece.color != self.color:
                    moves.append((current_row, current_col))
                    break
                else:
                    break

                current_row += d_row
                current_col += d_col
        return moves
    
class Knight(Piece):
    """
    Represents a Knight piece
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "N")
    def get_possible_moves(self, board: List[List[Optional[Piece]]],en_passant_possible: tuple = ())-> List[Tuple[int,int]]:
        moves = []

        knight_jumps = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for d_row, d_col in knight_jumps:
            target_row, target_col = self.row + d_row, self.col + d_col
            
            # Check if the target square is on the board
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                
                # We can move there if it's empty or occupied by an enemy
                if target_piece is None or target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        return moves
    
class Bishop(Piece):
    """
    Represents a Bishop piece
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "B")

    def get_possible_moves(self, board: List[List[Optional[Piece]]],en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        
        directions = [(-1,-1),(-1,1),(1,1),(1,-1)]

        for d_row, d_col in directions:
            current_row, current_col = self.row + d_row, self.col + d_col

            while 0<=current_row<8 and 0<=current_col<8:
                target_piece = board[current_row][current_col]

                if target_piece is None:
                    moves.append((current_row,current_col))

                elif target_piece.color != self.color:
                    moves.append((current_row, current_col))
                    break
                else:
                    break

                current_row += d_row
                current_col += d_col
        return moves
    

class Queen(Piece):
    """
    Represents a Queen piece.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "Q")

    def get_possible_moves(self, board: List[List[Optional[Piece]]],en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # Queen combines the moves of a Rook and a Bishop
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),   # Rook directions
            (-1, -1), (-1, 1), (1, 1), (1, -1)  # Bishop directions
        ]
        
        for d_row, d_col in directions:
            current_row, current_col = self.row + d_row, self.col + d_col
            
            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target_piece = board[current_row][current_col]
                
                if target_piece is None:
                    moves.append((current_row, current_col))
                elif target_piece.color != self.color:
                    moves.append((current_row, current_col))
                    break
                else:
                    break
                    
                current_row += d_row
                current_col += d_col
                
        return moves


class King(Piece):
    """
    Represents a King piece.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "K")

    def get_possible_moves(self, board: List[List[Optional[Piece]]],en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # King moves exactly 1 square in any of the 8 directions
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, 1), (1, -1)
        ]
        
        for d_row, d_col in directions:
            target_row, target_col = self.row + d_row, self.col + d_col
            
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                if target_piece is None or target_piece.color != self.color:
                    moves.append((target_row, target_col))
                    
        return moves


class Pawn(Piece):
    """
    Represents a Pawn piece.
    """
    def __init__(self, color: str, row: int, col: int):
        super().__init__(color, row, col, "P")

    def get_possible_moves(self, board: List[List[Optional[Piece]]], en_passant_possible: tuple = ()) -> List[Tuple[int, int]]:
        moves = []
        # White pawns move up (-1 row), black pawns move down (+1 row)
        move_direction = -1 if self.color == 'w' else 1
        start_row = 6 if self.color == 'w' else 1
        
        # 1. Move forward one square
        if 0 <= self.row + move_direction < 8:
            if board[self.row + move_direction][self.col] is None:
                moves.append((self.row + move_direction, self.col))
                
                # 2. Move forward two squares from starting position
                if self.row == start_row and board[self.row + 2 * move_direction][self.col] is None:
                    moves.append((self.row + 2 * move_direction, self.col))
                    
        # 3. Capture diagonally
        for d_col in [-1, 1]:
            target_col = self.col + d_col
            target_row = self.row + move_direction
            
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target_piece = board[target_row][target_col]
                # Can only capture an enemy piece
                if target_piece is not None and target_piece.color != self.color:
                    moves.append((target_row, target_col))
        if en_passant_possible != ():
            # Якщо бите поле знаходиться по діагоналі від нас (на 1 рядок вперед і на 1 колонку вбік)
            if self.row + move_direction == en_passant_possible[0]:
                if self.col - 1 == en_passant_possible[1] or self.col + 1 == en_passant_possible[1]:
                    moves.append(en_passant_possible)         
        # Note: En passant and promotion are complex rules that will be 
        # handled globally in the engine, not in the basic move generation.
        return moves