import numpy as np

EMPTY, BLACK, WHITE = 0, 1, -1
BOARD_SIZE = 8

# ------------------ 盤面ロジック ------------------
class OthelloBoard:
    DIRECTIONS = [(-1,-1), (-1,0), (-1,1),
                  (0,-1),          (0,1),
                  (1,-1),  (1,0),  (1,1)]
    
    def __init__(self):
        self.board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.reset()

    def reset(self):
        self.board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        mid = BOARD_SIZE//2
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

        for dr, dc in self.DIRECTIONS:
            nr, nc = r+dr, c+dc
            found_opponent = False
            while self.inside(nr,nc) and self.board[nr][nc] == -player:
                nr += dr
                nc += dc
                found_opponent = True
            if found_opponent and self.inside(nr,nc) and self.board[nr][nc] == player:
                return True
        return False

    def make_move(self, player, r, c):
        if not self.is_valid_move(player, r, c):
            return []
        self.board[r][c] = player
        flipped = []

        for dr, dc in self.DIRECTIONS:
            stones = []
            nr, nc = r+dr, c+dc
            while self.inside(nr,nc) and self.board[nr][nc] == -player:
                stones.append((nr,nc))
                nr += dr
                nc += dc
            if stones and self.inside(nr,nc) and self.board[nr][nc] == player:
                for rr, cc in stones:
                    self.board[rr][cc] = player
                    flipped.append((rr, cc, -player, player))
        return flipped

    def score(self):
        black = sum(row.count(BLACK) for row in self.board)
        white = sum(row.count(WHITE) for row in self.board)
        return black, white

    def copy(self):
        new_board = OthelloBoard()
        new_board.board = [row[:] for row in self.board]  # 深いコピー
        return new_board
    

class OthelloEnv:
    """オセロの強化学習環境。

    Attributes:
        board (OthelloBoard): 現在の盤面情報を保持。
        current_player (int): 現在の手番。BLACK=1, WHITE=-1。
    """

    def __init__(self):
        """OthelloEnv を初期化する。盤面はリセットされる。"""
        self.board = OthelloBoard()
        self.current_player = BLACK
        self.done = False

    def reset(self):
        """盤面を初期状態にリセットし、最初の観察を返す。

        Returns:
            np.ndarray: 8x8の盤面状態。BLACK=1, WHITE=-1, EMPTY=0。
        """
        self.board = OthelloBoard()
        self.current_player = BLACK
        return self._get_obs()

    def _get_obs(self):
        """現在の盤面状態を NumPy 配列で取得する。

        Returns:
            np.ndarray: 8x8の盤面状態。
        """
        return np.array(self.board.board, dtype=np.int8)

    def state_key(self):
        """現在の盤面＋手番をハッシュ可能キーにする"""
        return (tuple(tuple(row) for row in self.board.board), self.current_player)

    def legal_actions(self):
        """現在の手番での合法手を返す。

        Returns:
            List[int]: 0~63 の整数で表現された合法手。
        """
        moves = self.board.valid_moves(self.current_player)
        return [r*8 + c for r, c in moves]
    
    def is_game_over(self):
        """ゲームが終了しているかを返す。

        Returns:
            bool: ゲーム終了なら True、そうでなければ False。
        """
        return not (self.board.valid_moves(BLACK) or self.board.valid_moves(WHITE))

    def clone(self):
        """現在の環境のディープコピーを返す."""
        new_env = OthelloEnv()
        # 盤面のコピー
        new_env.board.board = [row[:] for row in self.board.board]
        # 現在のプレイヤー
        new_env.current_player = self.current_player
        # ゲーム終了フラグ
        new_env.done = self.done
        return new_env

    def extract_features(self):
        """盤面から特徴ベクトルを抽出"""
        black, white = self.board.score()

        # 石の差
        stone_diff = black - white

        # 合法手数
        black_moves = len(self.board.valid_moves(BLACK))
        white_moves = len(self.board.valid_moves(WHITE))

        # 角を取った数
        corners = [(0,0), (0,7), (7,0), (7,7)]
        black_corners = sum(1 for r,c in corners if self.board.board[r][c] == BLACK)
        white_corners = sum(1 for r,c in corners if self.board.board[r][c] == WHITE)

        # ゲーム進行度（置かれた石の割合）
        filled = black + white
        progress = filled / 64.0

        return (stone_diff, black_moves, white_moves, black_corners, white_corners, progress)

    def step(self, action):
        """指定した行動を実行し、次の状態、報酬、終了フラグ、追加情報を返す。

        Args:
            action (int): 0~63 の整数で表現される行動。

        Returns:
            tuple:
                np.ndarray: 次の盤面状態。
                float: 報酬。ゲーム終了時に ±1、引き分け 0、途中は 0。
                bool: ゲーム終了フラグ。
                dict: 追加情報（未使用）。
        """
        r, c = divmod(action, 8)
        self.board.make_move(self.current_player, r, c)
        done = self.is_game_over()
        reward = 0.0
        if done:
            b, w = self.board.score()
            if b > w:
                reward = b - w if self.current_player == BLACK else -1.0
            elif w > b:
                reward = w - b if self.current_player == WHITE else -1.0
            else:
                reward = 0.0

        # プレイヤー交代（相手に合法手がなければ同じプレイヤー）
        self.current_player = -self.current_player if self.board.valid_moves(-self.current_player) else self.current_player

        return self._get_obs(), reward, done, {}

    def render(self):
        """盤面をターミナルに表示する。

        使用例:
            env.render()
        """
        symbols = {BLACK: "●", WHITE: "○", EMPTY: "."}
        print("  a b c d e f g h")
        for r in range(8):
            row = [symbols[self.board.board[r][c]] for c in range(8)]
            print(f"{r+1} {' '.join(row)}")
        print(f"Next player: {'BLACK' if self.current_player==BLACK else 'WHITE'}\n")
