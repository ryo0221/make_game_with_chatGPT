import random
from abc import ABC, abstractmethod

import numpy as np

from othello.env import BLACK, WHITE, BOARD_SIZE, OthelloBoard
from othello.env import OthelloEnv

# --- 抽象クラス ---
class AbstractAI(ABC):
    """すべてのAIはこのインターフェースを実装する。"""

    def __init__(self, player):
        """
        Args:
            player (int): BLACK (1) または WHITE (-1)
        """
        self.player = player

    @abstractmethod
    def select_action(self, env):
        """
        次の手を決定する。
        Args:
            env (OthelloEnv): 強化学習用のオセロ環境
        Returns:
            int: 0~63 のアクション番号
        """
        pass

# --- ランダムAI ---
class RandomAI(AbstractAI):
    """ランダムに合法手を選ぶAI"""

    def select_action(self, env):
        legal = env.legal_actions()
        if not legal:
            return None
        return np.random.choice(legal)


# --- ミニマックスAI ---
class MinimaxAI(AbstractAI):
    """ミニマックスで探索するAI"""

    def __init__(self, player, depth=3):
        super().__init__(player)
        self.depth = depth

    def select_action(self, env):
        _, action = self._minimax(env, self.depth, True)
        return action

    def _minimax(self, env, depth, maximizing):
        if depth == 0 or env.done:
            return self._evaluate(env), None

        player = self.player if maximizing else -self.player
        moves = env.legal_actions()
        if not moves:
            return self._evaluate(env), None

        best_move = None
        if maximizing:
            max_eval = -float("inf")
            for a in moves:
                new_env = env.clone()
                new_env.step(a)
                eval_score, _ = self._minimax(new_env, depth-1, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = a
            return max_eval, best_move
        else:
            min_eval = float("inf")
            for a in moves:
                new_env = env.clone()
                new_env.step(a)
                eval_score, _ = self._minimax(new_env, depth-1, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = a
            return min_eval, best_move

    def _evaluate(self, env):
        b, w = env.board.score()
        return b - w if self.player == 1 else w - b