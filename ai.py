import random
from engine import GameState

# scoring constants
# standard piece values
PIECE_VALUES = {"K": 0, "Q": 90, "R": 50, "B": 30, "N": 30, "P": 10}
# extreme values for checkmate and stalemate
CHECKMATE_SCORE = 100000
STALEMATE_SCORE = 0

class BaseAI:
    """
    base class for all ai bots
    has shared methods for moves and board evaluation
    """
    def __init__(self):
        pass

    def get_all_legal_moves(self, gs: GameState) -> list:
        """
        get all valid moves for the current player
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
        evaluate board based on piece values
        positive means white is winning, negative means black
        """
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece is not None:
                    # p, n, q etc
                    piece_value = PIECE_VALUES.get(piece.name, 0)
                    if piece.color == 'w':
                        score += piece_value
                    elif piece.color == 'b':
                        score -= piece_value
        return score

    def get_move(self, gs: GameState) -> tuple:
        raise NotImplementedError("This method must be overridden in subclasses")


class RandomAI(BaseAI):
    """
    bot that plays random moves
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
    greedy bot that looks 1 move ahead
    simulates moves and picks the best immediate score
    """
    def __init__(self):
        super().__init__()

    def get_move(self, gs: GameState) -> tuple:
        valid_moves = self.get_all_legal_moves(gs)
        if not valid_moves:
            return None

        # turn multiplier to use same logic for white and black
        turn_multiplier = 1 if gs.white_to_move else -1
        max_score = -CHECKMATE_SCORE
        best_move = None

        # shuffle moves to avoid repetitive games
        random.shuffle(valid_moves)

        for player_move in valid_moves:
            start_pos = player_move[0]
            end_pos = player_move[1]
            
            # simulate move
            gs.make_move(start_pos, end_pos)
            
            # check for endgame
            if getattr(gs, 'checkmate', False):
                score = CHECKMATE_SCORE
            elif getattr(gs, 'stalemate', False):
                score = STALEMATE_SCORE
            else:
                # get score and flip based on turn
                score = turn_multiplier * self.score_board(gs.board)
            
            # save best score
            if score > max_score:
                max_score = score
                best_move = player_move
                
            # undo move to restore board
            gs.undo_move()

        # fallback to random if no best move
        return best_move if best_move else random.choice(valid_moves)


class SmartAI(BaseAI):
    """
    minimax algorithm with alpha-beta pruning
    looks a few moves ahead
    """
    def __init__(self, depth: int = 2):
        super().__init__()
        # how many moves ahead to look
        # depth > 3 is too slow in python
        self.depth = depth 
        self.next_move = None

    def get_move(self, gs: GameState) -> tuple:
        valid_moves = self.get_all_legal_moves(gs)
        if not valid_moves:
            return None

        random.shuffle(valid_moves)
        
        # start minimax search
        # alpha is best for maximizer, beta is best for minimizer
        self.find_best_move_minimax(gs, valid_moves, self.depth, -CHECKMATE_SCORE, CHECKMATE_SCORE, 1 if gs.white_to_move else -1)
        
        # next_move is updated in the recursive call
        return self.next_move if self.next_move else random.choice(valid_moves)

    def find_best_move_minimax(self, gs: GameState, valid_moves: list, depth: int, alpha: float, beta: float, turn_multiplier: int) -> float:
        """
        recursive minimax function
        """
        # base case: reached max depth
        if depth == 0:
            return turn_multiplier * self.score_board(gs.board)

        max_score = -CHECKMATE_SCORE
        
        for move in valid_moves:
            start_pos = move[0]
            end_pos = move[1]
            
            gs.make_move(start_pos, end_pos)
            
            # get opponent responses
            next_moves = self.get_all_legal_moves(gs)
            
            # check endgame conditions
            if getattr(gs, 'checkmate', False):
                score = CHECKMATE_SCORE
            elif getattr(gs, 'stalemate', False):
                score = STALEMATE_SCORE
            else:
                # dive deeper and switch turn multiplier
                score = -self.find_best_move_minimax(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
                
            gs.undo_move()

            # update best score
            if score > max_score:
                max_score = score
                if depth == self.depth:
                    # update choice only at the top
                    self.next_move = move
            
            # alpha-beta pruning
            if max_score > alpha:
                alpha = max_score
            if alpha >= beta:
                break # prune branch
                
        return max_score