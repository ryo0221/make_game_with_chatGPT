import pygame
import sys
import math
import random
from abc import ABC, abstractmethod


# 定数
EMPTY, BLACK, WHITE = 0, 1, -1
BOARD_SIZE = 8
CELL_SIZE = 80
WINDOW_SIZE = CELL_SIZE * BOARD_SIZE
FPS = 30

# 色
GREEN = (0, 128, 0)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
HIGHLIGHT_ALPHA = 120

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

# ------------------ メニュー画面 ------------------
class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = (0, 100, 0)
        self.title_font = pygame.font.Font("./fonts/MEIRYOB.TTC", 72)
        self.button_font = pygame.font.Font("./fonts/MEIRYO.TTC", 48)
        self.options = ["人 vs 人", "人 vs AI", "AI vs AI"]
        self.selected_mode = None

    def draw_title(self):
        title_text = "Othello"
        shadow = self.title_font.render(title_text, True, (0,0,0))
        rect = shadow.get_rect(center=(WINDOW_SIZE//2+3, 100+3))
        self.screen.blit(shadow, rect)
        img = self.title_font.render(title_text, True, (255,255,0))
        rect = img.get_rect(center=(WINDOW_SIZE//2, 100))
        self.screen.blit(img, rect)

    def draw_buttons(self, mouse_pos):
        for i, text in enumerate(self.options):
            x = WINDOW_SIZE // 2
            y = 250 + i*120
            rect = pygame.Rect(x-150, y-40, 300, 80)
            color = (200,200,50) if rect.collidepoint(mouse_pos) else (255,255,255)
            pygame.draw.rect(self.screen, (50,50,50), rect)
            pygame.draw.rect(self.screen, color, rect, 3)
            img = self.button_font.render(text, True, color)
            img_rect = img.get_rect(center=rect.center)
            self.screen.blit(img, img_rect)
            pygame.draw.circle(self.screen, BLACK_COLOR if i==0 else WHITE_COLOR, (rect.left+40, rect.centery), 20)
        
    
    '''def draw_buttons(self, mouse_pos):
        for i, text in enumerate(self.options):
            x = WINDOW_SIZE // 2
            y = 250 + i*120
            rect = pygame.Rect(x-150, y-40, 300, 80)
            color = (200, 200, 50) if rect.collidepoint(mouse_pos) else (255, 255, 255)
            pygame.draw.rect(self.screen, (50,50,50), rect)
            pygame.draw.rect(self.screen, color, rect, 3)
            img = self.button_font.render(text, True, color)
            img_rect = img.get_rect(center=rect.center)
            self.screen.blit(img, img_rect)
            pygame.draw.circle(self.screen, BLACK_COLOR if i==0 else WHITE_COLOR, (rect.left+40, rect.centery), 20)
            '''

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill(self.bg_color)
            self.draw_title()
            self.draw_buttons(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, text in enumerate(self.options):
                        rect = pygame.Rect(WINDOW_SIZE//2-150, 250 + i*120-40, 300, 80)
                        if rect.collidepoint(event.pos):
                            self.selected_mode = ["PVP","PVAI","AIvsAI"][i]
                            running = False
            pygame.display.flip()
            clock.tick(FPS)
        return self.selected_mode


# ------------------ GUI ------------------
class OthelloGUI:
    def __init__(self, mode="PVP"):
        pygame.init()
        self.mode = mode
        self.game = OthelloGame()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Othello")
        self.clock = pygame.time.Clock()
        if mode=="PVAI":
            self.ai = MinimaxAI(WHITE)
        elif mode=="AIvsAI":
            self.black_ai = RandomAI(BLACK)
            self.white_ai = MinimaxAI(WHITE, depth=2)

    def draw_board(self, draw_flips=True):
        self.screen.fill(GREEN)
        for i in range(BOARD_SIZE+1):
            pygame.draw.line(self.screen, LINE_COLOR, (i*CELL_SIZE,0), (i*CELL_SIZE,WINDOW_SIZE))
            pygame.draw.line(self.screen, LINE_COLOR, (0,i*CELL_SIZE), (WINDOW_SIZE,i*CELL_SIZE))
        # 石描画
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                v = self.game.board.board[r][c]
                if v != EMPTY:
                    center = (c*CELL_SIZE + CELL_SIZE//2, r*CELL_SIZE + CELL_SIZE//2)
                    color = BLACK_COLOR if v==BLACK else WHITE_COLOR
                    pygame.draw.circle(self.screen, color, center, CELL_SIZE//2 - 5)
        # 合法手ハイライト
        if draw_flips and not self.game.is_game_over():
            moves = self.game.board.valid_moves(self.game.turn)
            alpha = int(100 + 80 * abs(math.sin(pygame.time.get_ticks()/300)))
            color = (0,0,0,alpha) if self.game.turn==BLACK else (255,255,255,alpha)
            for r,c in moves:
                s = pygame.Surface((CELL_SIZE,CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (CELL_SIZE//2,CELL_SIZE//2), CELL_SIZE//3)
                self.screen.blit(s, (c*CELL_SIZE, r*CELL_SIZE))
        # 勝敗判定
        if self.game.is_game_over():
            font = pygame.font.SysFont(None,36)
            b,w = self.game.board.score()
            if b>w:
                text = f"Game Over! Black wins! ({b}-{w})"
            elif w>b:
                text = f"Game Over! White wins! ({b}-{w})"
            else:
                text = f"Game Over! Draw! ({b}-{w})"
            img = font.render(text, True, (255,255,0))
            rect = img.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            self.screen.blit(img, rect)

    def handle_click(self, pos):
        c = pos[0] // CELL_SIZE
        r = pos[1] // CELL_SIZE
        if self.game.board.is_valid_move(self.game.turn, r, c):
            self.game.board.make_move(self.game.turn, r, c)
            # 裏返しアニメーションはなし → 即描画
            self.game.switch_turn()

    def run(self):
        running = True
        while running:
            if self.game.turn == BLACK and not self.game.board.valid_moves(BLACK):
                self.game.switch_turn()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game.is_game_over() and self.game.board.valid_moves(BLACK):
                    self.handle_click(event.pos)

            # AIの手番処理
            if self.mode=="PVAI" and self.game.turn==WHITE and not self.game.is_game_over():
                moves = self.game.board.valid_moves(self.game.turn)
                if moves:
                    pygame.time.delay(300)  # 少し待って自然に
                    move = self.ai.get_move(self.game.board)
                    if move:
                        r,c = move
                        self.game.board.make_move(self.game.turn, r, c)
                self.game.switch_turn()

            elif self.mode=="AIvsAI" and not self.game.is_game_over():
                current_ai = self.black_ai if self.game.turn==BLACK else self.white_ai
                move = current_ai.get_move(self.game.board)
                if move:
                    r,c = move
                    self.game.board.make_move(self.game.turn, r, c)
                self.game.switch_turn()

            # 描画
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()





if __name__ == "__main__":
    
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    menu = MenuScreen(screen)
    mode = menu.run()  # "PVP" または "PVAI" または "AIvsAI"
    gui = OthelloGUI(mode)
    gui.run()
