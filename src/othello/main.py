import pygame
import sys
import math
import random
from abc import ABC, abstractmethod

from othello.env import BOARD_SIZE, BLACK, WHITE, EMPTY
from othello.env import OthelloEnv
from othello.ai import RandomAI, MinimaxAI

# 定数

CELL_SIZE = 80
WINDOW_SIZE = CELL_SIZE * BOARD_SIZE
FPS = 30

# 色
GREEN = (0, 128, 0)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
HIGHLIGHT_ALPHA = 120


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
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, text in enumerate(self.options):
                        rect = pygame.Rect(WINDOW_SIZE//2-150, 250 + i*120-40, 300, 80)
                        if rect.collidepoint(event.pos):
                            self.selected_mode = ["PVP","PVAI","AIVAI"][i]
                            running = False
            pygame.display.flip()
            clock.tick(FPS)
        return self.selected_mode


# ------------------ GUI ------------------
class OthelloGUI:
    def __init__(self, mode="PVP"):
        pygame.init()
        self.mode = mode
        self.env = OthelloEnv()
        self.env.reset()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Othello")
        self.clock = pygame.time.Clock()

        if mode in ("PVAI", "AIVAI"):
            self.ai_black = RandomAI(BLACK) if mode=="AIVAI" else None
            self.ai_white = MinimaxAI(WHITE, depth=3) if mode=="PVAI" else None
    
    def handle_click(self, pos):
        c = pos[0] // CELL_SIZE
        r = pos[1] // CELL_SIZE
        action = r * BOARD_SIZE + c
        if action in self.env.legal_actions():
            self.env.step(action)

    def draw_board(self, draw_flips=True):
        self.screen.fill(GREEN)
        for i in range(BOARD_SIZE+1):
            pygame.draw.line(self.screen, LINE_COLOR, (i*CELL_SIZE,0), (i*CELL_SIZE,WINDOW_SIZE))
            pygame.draw.line(self.screen, LINE_COLOR, (0,i*CELL_SIZE), (WINDOW_SIZE,i*CELL_SIZE))

        # 石描画
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                v = self.env.board.board[r][c]
                if v != EMPTY:
                    center = (c*CELL_SIZE + CELL_SIZE//2, r*CELL_SIZE + CELL_SIZE//2)
                    color = BLACK_COLOR if v==BLACK else WHITE_COLOR
                    pygame.draw.circle(self.screen, color, center, CELL_SIZE//2 - 5)

        # 合法手ハイライト
        if draw_flips:
            moves = self.env.legal_actions()
            alpha = int(100 + 80 * abs(math.sin(pygame.time.get_ticks()/300)))
            color = (0,0,0,alpha) if self.env.current_player == BLACK else (255,255,255,alpha)
            for action in moves:
                r, c = divmod(action, BOARD_SIZE)
                s = pygame.Surface((CELL_SIZE,CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (CELL_SIZE//2,CELL_SIZE//2), CELL_SIZE//3)
                self.screen.blit(s, (c*CELL_SIZE, r*CELL_SIZE))

        # 勝敗判定
        """
        if self.env.done:
            font = pygame.font.SysFont(None,36)
            b,w = self.env.board.score()
            if b>w:
                text = f"Game Over! Black wins! ({b}-{w})"
            elif w>b:
                text = f"Game Over! White wins! ({b}-{w})"
            else:
                text = f"Game Over! Draw! ({b}-{w})"
            img = font.render(text, True, (255,255,0))
            rect = img.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            self.screen.blit(img, rect)
        """
    """        
    def handle_click(self, pos):
        c = pos[0] // CELL_SIZE
        r = pos[1] // CELL_SIZE
        if self.game.board.is_valid_move(self.game.turn, r, c):
            self.game.board.make_move(self.game.turn, r, c)
            # 裏返しアニメーションはなし → 即描画
            self.game.switch_turn()
    """
            
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and self.mode in ("PVP", "PVAI"):
                    if self.env.current_player == BLACK or self.mode == "PVP":
                        self.handle_click(event.pos)
            
            # AIの手番処理
            if self.mode in ("PVAI", "AIVAI"):
                current_ai = self.ai_black if self.env.current_player == BLACK else self.ai_white
                if current_ai:
                    moves = self.env.legal_actions()
                    if moves:
                        pygame.time.delay(300)  # 少し待って自然に
                        action = current_ai.select_action(self.env)
                        if action is not None:
                            self.env.step(action)
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
