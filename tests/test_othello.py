import pytest
import sys

from othello.env import OthelloBoard, BLACK, WHITE, EMPTY, BOARD_SIZE
from othello.env import OthelloEnv


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
