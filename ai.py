import random
from engine import GameState

# ==========================================
# SCORING CONSTANTS
# ==========================================
# Standard chess piece relative values
PIECE_VALUES = {"K": 0, "Q": 90, "R": 50, "B": 30, "N": 30, "P": 10}
# Extreme values for endgame scenarios
CHECKMATE_SCORE = 100000
STALEMATE_SCORE = 0

class BaseAI:
    """
    The base class for all AI algorithms.
    Contains shared methods like move generation and board evaluation.
    """
    def __init__(self):
        pass

    def get_all_legal_moves(self, gs: GameState) -> list:
        """
        Collects all possible legal moves for the current player.
        """
        all_moves = []
        for r in range(8):
            for c in range(8):
                piece = gs.board[r][c]
                if piece is not None:
                    if (piece.color == 'w' and gs.white_to_move) or (piece.color == 'b' and not gs.white_to_move):
                        valid_destinations = gs.get_valid_moves_for_piece(r, c)
                        if valid_destinations:
                            for dest in valid_destinations:
                                all_moves.append(((r, c), dest))
        return all_moves

    def score_board(self, board: list) -> int:
        """
        Evaluates the board state strictly based on material advantage.
        Positive score means White is winning, negative means Black is winning.
        """
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece is not None:
                    # piece.name is 'P', 'N', 'Q', etc.
                    piece_value = PIECE_VALUES.get(piece.name, 0)
                    if piece.color == 'w':
                        score += piece_value
                    elif piece.color == 'b':
                        score -= piece_value
        return score

    def get_move(self, gs: GameState) -> tuple:
        raise NotImplementedError("This method must be overridden in subclasses.")


class RandomAI(BaseAI):
    """
    A simple AI that plays completely at random.
    """
    def __init__(self):
        super().__init__()

    def get_move(self, gs: GameState) -> tuple:
        valid_moves = self.get_all_legal_moves(gs)
        if valid_moves:
            return random.choice(valid_moves)
        return None


class GreedyAI(BaseAI):
    """
    A greedy AI that looks exactly 1 move ahead.
    It simulates every possible move, scores the resulting board, 
    and picks the one that maximizes its immediate score.
    """
    def __init__(self):
        super().__init__()

    def get_move(self, gs: GameState) -> tuple:
        valid_moves = self.get_all_legal_moves(gs)
        if not valid_moves:
            return None

        # Turn multiplier helps us use the same logic for both White and Black.
        # If White, we want the highest positive score. If Black, the lowest negative score.
        turn_multiplier = 1 if gs.white_to_move else -1
        max_score = -CHECKMATE_SCORE
        best_move = None

        # Shuffle moves so the bot doesn't repeat the same exact game every time
        random.shuffle(valid_moves)

        for player_move in valid_moves:
            start_pos = player_move[0]
            end_pos = player_move[1]
            
            # 1. Simulate the move on the actual board
            gs.make_move(start_pos, end_pos)
            
            # 2. Check for immediate checkmate/stalemate
            if getattr(gs, 'checkmate', False):
                score = CHECKMATE_SCORE
            elif getattr(gs, 'stalemate', False):
                score = STALEMATE_SCORE
            else:
                # Calculate material score and flip it based on who is playing
                score = turn_multiplier * self.score_board(gs.board)
            
            # 3. If this is the best score we've seen so far, save it
            if score > max_score:
                max_score = score
                best_move = player_move
                
            # 4. UNDO THE MOVE to restore the board for the next simulation
            gs.undo_move()

        # If somehow no best move was found, fallback to a random move
        return best_move if best_move else random.choice(valid_moves)


class SmartAI(BaseAI):
    """
    An advanced AI utilizing the Minimax algorithm with Alpha-Beta pruning.
    It looks multiple moves deep into the future to find the best continuation.
    """
    def __init__(self, depth: int = 2):
        super().__init__()
        # Depth is how many half-moves the AI looks ahead. 
        # Warning: Python is slow. Depth > 3 will cause noticeable lag without further optimizations.
        self.depth = depth 
        self.next_move = None

    def get_move(self, gs: GameState) -> tuple:
        valid_moves = self.get_all_legal_moves(gs)
        if not valid_moves:
            return None

        random.shuffle(valid_moves)
        
        # We start the recursive Minimax search here
        # Alpha is the best already explored option along the path to the root for the maximizer
        # Beta is the best already explored option along the path to the root for the minimizer
        self.find_best_move_minimax(gs, valid_moves, self.depth, -CHECKMATE_SCORE, CHECKMATE_SCORE, 1 if gs.white_to_move else -1)
        
        # self.next_move is updated by the recursive function
        return self.next_move if self.next_move else random.choice(valid_moves)

    def find_best_move_minimax(self, gs: GameState, valid_moves: list, depth: int, alpha: float, beta: float, turn_multiplier: int) -> float:
        """
        Recursive Minimax function with Alpha-Beta pruning.
        """
        # Base Case: We reached the maximum search depth
        if depth == 0:
            return turn_multiplier * self.score_board(gs.board)

        max_score = -CHECKMATE_SCORE
        
        for move in valid_moves:
            start_pos = move[0]
            end_pos = move[1]
            
            gs.make_move(start_pos, end_pos)
            
            # We need to get the opponent's responses for the next depth level
            next_moves = self.get_all_legal_moves(gs)
            
            # Evaluate end-game conditions deep in the tree
            if getattr(gs, 'checkmate', False):
                score = CHECKMATE_SCORE
            elif getattr(gs, 'stalemate', False):
                score = STALEMATE_SCORE
            else:
                # Recursive call: dive deeper into the tree, switching the turn multiplier
                score = -self.find_best_move_minimax(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
                
            gs.undo_move()

            # Update best score and best move
            if score > max_score:
                max_score = score
                if depth == self.depth:
                    # Only update the final choice at the top of the tree
                    self.next_move = move
            
            # Alpha-Beta Pruning logic
            if max_score > alpha:
                alpha = max_score
            if alpha >= beta:
                break # Prune the branch - opponent will never allow this line
                
        return max_score