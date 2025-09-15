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