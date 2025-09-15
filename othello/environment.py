import random
import numpy as np
import gym
from gym import spaces

# ------------------ 定数 ------------------
EMPTY, BLACK, WHITE = 0, 1, -1
BOARD_SIZE = 8

# ------------------ 盤面ロジック ------------------
class OthelloBoard:
    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.reset()

    def reset(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        mid = BOARD_SIZE // 2
        self.board[mid-1][mid-1] = WHITE
        self.board[mid][mid] = WHITE
        self.board[mid-1][mid] = BLACK
        self.board[mid][mid-1] = BLACK

    def inside(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def valid_moves(self, player):
        return [(r, c) for r in range(BOARD_SIZE)
                for c in range(BOARD_SIZE)
                if self.is_valid_move(player, r, c)]

    def is_valid_move(self, player, r, c):
        if not self.inside(r, c) or self.board[r][c] != EMPTY:
            return False
        directions = [(-1,-1),(-1,0),(-1,1),
                      (0,-1),       (0,1),
                      (1,-1),(1,0),(1,1)]
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            found_opponent = False
            while self.inside(nr, nc) and self.board[nr][nc] == -player:
                nr += dr
                nc += dc
                found_opponent = True
            if found_opponent and self.inside(nr, nc) and self.board[nr][nc] == player:
                return True
        return False

    def make_move(self, player, r, c):
        if not self.is_valid_move(player, r, c):
            return []
        self.board[r][c] = player
        flipped = []
        directions = [(-1,-1),(-1,0),(-1,1),
                      (0,-1),       (0,1),
                      (1,-1),(1,0),(1,1)]
        for dr, dc in directions:
            stones = []
            nr, nc = r+dr, c+dc
            while self.inside(nr, nc) and self.board[nr][nc] == -player:
                stones.append((nr, nc))
                nr += dr
                nc += dc
            if stones and self.inside(nr, nc) and self.board[nr][nc] == player:
                for rr, cc in stones:
                    self.board[rr][cc] = player
                    flipped.append((rr, cc))
        return flipped

    def score(self):
        black = sum(row.count(BLACK) for row in self.board)
        white = sum(row.count(WHITE) for row in self.board)
        return black, white

    def copy(self):
        new_board = OthelloBoard()
        new_board.board = [row[:] for row in self.board]
        return new_board


# ------------------ ゲーム進行 ------------------
class OthelloGame:
    def __init__(self):
        self.board = OthelloBoard()
        self.turn = BLACK

    def switch_turn(self):
        self.turn = -self.turn

    def has_valid_moves(self, player):
        return bool(self.board.valid_moves(player))

    def is_game_over(self):
        return not (self.has_valid_moves(BLACK) or self.has_valid_moves(WHITE))


# ------------------ ランダムAI ------------------
class RandomAI:
    def __init__(self, player):
        self.player = player

    def get_move(self, board: OthelloBoard):
        moves = board.valid_moves(self.player)
        if not moves:
            return None
        return random.choice(moves)


# ------------------ Minimax AI ------------------
class MinimaxAI:
    def __init__(self, player, depth=3):
        self.player = player
        self.depth = depth

    def evaluate(self, board: OthelloBoard):
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                v = board.board[r][c]
                if v == self.player:
                    score += 1
                    if (r==0 or r==BOARD_SIZE-1) and (c==0 or c==BOARD_SIZE-1):
                        score += 3
                elif v == -self.player:
                    score -= 1
                    if (r==0 or r==BOARD_SIZE-1) and (c==0 or c==BOARD_SIZE-1):
                        score -= 3
        return score

    def minimax(self, board: OthelloBoard, depth, maximizing):
        if depth == 0 or not (board.valid_moves(BLACK) or board.valid_moves(WHITE)):
            return self.evaluate(board), None
        player = self.player if maximizing else -self.player
        moves = board.valid_moves(player)
        if not moves:
            return self.evaluate(board), None
        best_move = None
        if maximizing:
            max_eval = -float("inf")
            for r, c in moves:
                new_board = board.copy()
                new_board.make_move(player, r, c)
                eval_score, _ = self.minimax(new_board, depth-1, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (r, c)
            return max_eval, best_move
        else:
            min_eval = float("inf")
            for r, c in moves:
                new_board = board.copy()
                new_board.make_move(player, r, c)
                eval_score, _ = self.minimax(new_board, depth-1, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (r, c)
            return min_eval, best_move

    def get_move(self, board: OthelloBoard):
        _, move = self.minimax(board, self.depth, True)
        return move


# ------------------ Gym 互換環境 ------------------
class OthelloEnv(gym.Env):
    metadata = {"render.modes": ["human", "ansi"]}

    def __init__(self):
        super().__init__()
        self.game = OthelloGame()

        self.observation_space = spaces.Box(
            low=-1, high=1, shape=(8, 8), dtype=np.int8
        )
        self.action_space = spaces.Discrete(64)

    def reset(self):
        self.game = OthelloGame()
        return np.array(self.game.board.board, dtype=np.int8)

    def step(self, action):
        r, c = divmod(action, 8)
        player = self.game.turn

        if self.game.board.is_valid_move(player, r, c):
            self.game.board.make_move(player, r, c)
            self.game.switch_turn()

        state = np.array(self.game.board.board, dtype=np.int8)
        done = self.game.is_game_over()
        reward = self._get_reward(player, done)

        return state, reward, done, {}

    def _get_reward(self, player, done):
        if not done:
            return 0
        black, white = self.game.board.score()
        if black > white:
            return 1 if player == BLACK else -1
        elif white > black:
            return 1 if player == WHITE else -1
        return 0

    def render(self, mode="human"):
        board = self.game.board.board
        symbols = {EMPTY: "·", BLACK: "●", WHITE: "○"}
        rows = []
        for r in range(8):
            row = " ".join(symbols[v] for v in board[r])
            rows.append(row)
        output = "\n".join(rows)
        if mode == "human":
            print(output)
        return output

if __name__ == "__main__":
    env = OthelloEnv()
    state = env.reset()
    done = False
    while not done:
        action = env.action_space.sample()
        state, reward, done, info = env.step(action)
        env.render()
    print("最終報酬:", reward)