import pytest
import sys

from othello.env import OthelloBoard, BLACK, WHITE, EMPTY, BOARD_SIZE
from othello.env import OthelloEnv
from othello.game import OthelloGame
from othello.ai import RandomAI, MinimaxAI

def test_reset():
    board = OthelloBoard()
    board.reset()
    mid = 4
    assert board.board[mid-1][mid-1] == WHITE
    assert board.board[mid][mid] == WHITE
    assert board.board[mid-1][mid] == BLACK
    assert board.board[mid][mid-1] == BLACK

def test_is_valid_move():
    board = OthelloBoard()
    board.reset()
    # 初期盤面で合法手
    assert board.is_valid_move(BLACK, 2, 3)
    assert board.is_valid_move(BLACK, 3, 2)
    # 石のあるところは不可
    assert not board.is_valid_move(BLACK, 3, 3)

def test_make_move_flips():
    board = OthelloBoard()
    board.reset()
    flips = board.make_move(BLACK, 2, 3)
    # (3,3) が裏返るはず
    assert (3,3, WHITE, BLACK) in flips
    assert board.board[3][3] == BLACK

def test_valid_moves_list():
    board = OthelloBoard()
    board.reset()
    moves = board.valid_moves(BLACK)
    assert (2,3) in moves
    assert (3,2) in moves

def test_score_count():
    board = OthelloBoard()
    board.reset()
    black, white = board.score()
    assert black == 2
    assert white == 2
    board.make_move(BLACK, 2, 3)
    black, white = board.score()
    assert black > white

def test_copy_board():
    board = OthelloBoard()
    board.reset()
    board2 = board.copy()
    board.make_move(BLACK, 2, 3)
    # 元のboard2は変わっていないはず
    assert board2.board[2][3] == EMPTY

def test_random_ai_move():
    board = OthelloBoard()
    board.reset()
    ai = RandomAI(BLACK)
    move = ai.get_move(board)
    assert move in board.valid_moves(BLACK)

def test_minimax_ai_move():
    board = OthelloBoard()
    board.reset()
    ai = MinimaxAI(BLACK, depth=1)
    move = ai.get_move(board)
    assert move in board.valid_moves(BLACK)

def test_game_over_when_no_moves():
    game = OthelloGame()
    
    # 人間(BLACK)とAI(WHITE)双方の合法手がない状態を作る
    # 例: 盤面を全てBLACKで埋める
    for r in range(8):
        for c in range(8):
            game.board.board[r][c] = BLACK
    
    # 合法手はどちらにもないはず
    assert not game.has_valid_moves(BLACK)
    assert not game.has_valid_moves(WHITE)
    
    # ゲーム終了判定
    assert game.is_game_over()
    
    # スコアが正しい
    black_score, white_score = game.board.score()
    assert black_score == 64
    assert white_score == 0

def test_game_over_partial_board():
    game = OthelloGame()
    # 盤面を交互に埋め、合法手がない状態を作る
    for r in range(8):
        for c in range(8):
            game.board.board[r][c] = BLACK if (r+c)%2==0 else WHITE
    assert not game.has_valid_moves(BLACK)
    assert not game.has_valid_moves(WHITE)
    assert game.is_game_over()
    black_score, white_score = game.board.score()
    assert black_score + white_score == 64

def test_reset_returns_initial_board():
    env = OthelloEnv()
    obs = env.reset()
    # 初期盤面の中央に石が正しく置かれているか
    mid = BOARD_SIZE // 2
    assert env.board.board[mid-1][mid-1] == WHITE
    assert env.board.board[mid][mid] == WHITE
    assert env.board.board[mid-1][mid] == BLACK
    assert env.board.board[mid][mid-1] == BLACK

def test_legal_actions_return_list():
    env = OthelloEnv()
    env.reset()
    actions = env.legal_actions()
    # 行動は0~63のリストで返る
    assert isinstance(actions, list)
    assert all(isinstance(a, int) for a in actions)
    assert all(0 <= a < 64 for a in actions)

def test_step_updates_board_and_player():
    env = OthelloEnv()
    env.reset()
    actions = env.legal_actions()
    action = actions[0]
    obs, reward, done, info = env.step(action)
    # 石を置いた座標がプレイヤーの石に変わっている
    r, c = divmod(action, BOARD_SIZE)
    assert env.board.board[r][c] == -env.current_player  # current_player は次の手番に変わる
    # done は bool 型
    assert isinstance(done, bool)
    # reward は数値
    assert isinstance(reward, (int, float))

def test_game_over_detection():
    env = OthelloEnv()
    env.reset()
    # 全マスを埋めてゲームオーバーを強制
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            env.board.board[r][c] = BLACK
    # legal_actions は空になる
    assert env.legal_actions() == []
    # ゲーム終了判定
    obs, reward, done, info = env.step(0)  # ダミー手
    assert done is True