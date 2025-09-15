import random
from abc import ABC, abstractmethod

from othello.env import BOARD_SIZE, BLACK, WHITE, OthelloBoard

# --- 抽象クラス ---
class AbstractAI(ABC):
    def __init__(self, color):
        self.color = color

    @abstractmethod
    def get_move(self, board):
        """盤面を受け取り、(row, col) の手を返す。打てない場合は None"""
        pass

# --- ランダムAI ---
class RandomAI(AbstractAI):
    def get_move(self, board):
        moves = board.valid_moves(self.color)
        if not moves:
            return None
        return random.choice(moves)

# --- ミニマックスAI ---
class MinimaxAI(AbstractAI):
    def __init__(self, ai_color, depth=3):
        self.ai_color = ai_color      # このAIが担当する色
        self.depth = depth

    def evaluate(self, board: OthelloBoard):
        """評価関数: 石の差 + 角のボーナス"""
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                v = board.board[r][c]
                if v == self.ai_color:
                    score += 1
                    if (r == 0 or r == BOARD_SIZE-1) and (c == 0 or c == BOARD_SIZE-1):
                        score += 3
                elif v == -self.ai_color:
                    score -= 1
                    if (r == 0 or r == BOARD_SIZE-1) and (c == 0 or c == BOARD_SIZE-1):
                        score -= 3
        return score

    def minimax(self, board: OthelloBoard, depth: int, maximizing: bool, current_player: int):
        """Minimax 再帰探索"""
        if depth == 0 or not (board.valid_moves(BLACK) or board.valid_moves(WHITE)):
            return self.evaluate(board), None

        moves = board.valid_moves(current_player)
        if not moves:
            return self.evaluate(board), None

        best_move = None
        if maximizing:
            max_eval = -float("inf")
            for r, c in moves:
                new_board = board.copy()
                new_board.make_move(current_player, r, c)
                eval_score, _ = self.minimax(new_board, depth-1, False, -current_player)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (r, c)
            return max_eval, best_move
        else:
            min_eval = float("inf")
            for r, c in moves:
                new_board = board.copy()
                new_board.make_move(current_player, r, c)
                eval_score, _ = self.minimax(new_board, depth-1, True, -current_player)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (r, c)
            return min_eval, best_move

    def get_move(self, board: OthelloBoard):
        """AIが次に打つ手を返す"""
        _, move = self.minimax(board, self.depth, True, self.ai_color)
        return move
