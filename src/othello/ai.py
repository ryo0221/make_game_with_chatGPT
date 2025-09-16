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
    

class QLearningAgent(AbstractAI):
    """Q学習ベースのオセロAI"""

    def __init__(self, player: int, alpha=0.1, gamma=0.9, epsilon=0.2, epsilon_decay=0.999):
        super().__init__(player)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.q_table = {}
        self.actions = 64  # 8x8 マス

    
    def _state_key(self, env: OthelloEnv):
        return (env.extract_features(), env.current_player)
    
    #def _state_key(self, board, current_player):
    #    """盤面＋手番をタプル化してQテーブルのキーに"""
    #    return (tuple(tuple(row) for row in board.board), current_player)


    def select_action(self, env: OthelloEnv) -> int:
        """ε-greedyで行動を選択"""
        state = self._state_key(env)
        legal = env.legal_actions()
        if not legal:
            return None

        # ε-greedy
        if random.random() < self.epsilon or state not in self.q_table:
            return random.choice(legal)

        q_values = self.q_table[state]
        legal_qs = [(a, q_values.get(a, 0.0)) for a in legal]
        best_action = max(legal_qs, key=lambda x: x[1])[0]
        return best_action

    def update(self, state_board, action, reward, next_board, next_player, done):
        """Q値更新"""
        state_key = state_board, self.player
        next_key = next_board

        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if action not in self.q_table[state_key]:
            self.q_table[state_key][action] = 0.0

        old_value = self.q_table[state_key][action]
        next_max = 0.0

        if not done and next_key in self.q_table:
            next_max = max(self.q_table[next_key].values(), default=0.0)

        target = reward + (0 if done else self.gamma * next_max)
        self.q_table[state_key][action] = old_value + self.alpha * (target - old_value)

        # εを少しずつ減らす
        self.epsilon *= self.epsilon_decay