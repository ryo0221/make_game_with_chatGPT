import numpy as np
from othello.othello import OthelloBoard, BLACK, WHITE

class OthelloEnv:
    """OpenAI Gym ライクなオセロ環境"""
    def __init__(self):
        self.board = OthelloBoard()
        self.current_player = BLACK
        self.done = False

    def reset(self):
        self.board.reset()
        self.current_player = BLACK
        self.done = False
        return self._get_obs()

    def _get_obs(self):
        return np.array(self.board.board, dtype=np.int8)

    def legal_actions(self):
        moves = self.board.valid_moves(self.current_player)
        return [r*8 + c for r, c in moves]

    def step(self, action):
        if self.done:
            raise ValueError("Episode has ended. Call reset().")

        r, c = divmod(action, 8)
        reward = 0.0

        if self.board.is_valid_move(self.current_player, r, c):
            self.board.make_move(self.current_player, r, c)
        else:
            reward = -0.1

        # ターン交代
        self.current_player = -self.current_player
        if not self.board.valid_moves(self.current_player):
            self.current_player = -self.current_player
            if not self.board.valid_moves(self.current_player):
                self.done = True
                black, white = self.board.score()
                if black > white:
                    reward = 1.0 if self.current_player == BLACK else -1.0
                elif white > black:
                    reward = 1.0 if self.current_player == WHITE else -1.0
                else:
                    reward = 0.0

        obs = self._get_obs()
        info = {"current_player": self.current_player, "legal_actions": self.legal_actions()}
        return obs, reward, self.done, info

    def render(self):
        for row in self.board.board:
            print(" ".join("●" if x==BLACK else "○" if x==WHITE else "·" for x in row))
        print()