from othello.env import OthelloEnv, BOARD_SIZE, BLACK, WHITE
from othello.ai import RandomAI, MinimaxAI

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

def test_random_ai_move():
    env = OthelloEnv()
    env.reset()
    ai = RandomAI(BLACK)
    move = ai.select_action(env)
    assert move in env.legal_actions()

def test_minimax_ai_move():
    env = OthelloEnv()
    env.reset()
    ai = MinimaxAI(BLACK, depth=1)
    move = ai.select_action(env)
    assert move in env.legal_actions()
