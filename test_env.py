from othello.env import OthelloEnv
import random

env = OthelloEnv()

# 初期状態を確認
obs = env.reset()
print("初期盤面:")
env.render()

done = False
turn = 0

# ランダムでプレイを進めるテスト
while not done and turn < 20:  # 最大20手まで
    actions = env.legal_actions()
    if not actions:
        print("手番なし、スキップ")
        env.current_player = -env.current_player
        continue
    action = random.choice(actions)
    obs, reward, done, info = env.step(action)
    print(f"手番: {'BLACK' if env.current_player==-1 else 'WHITE'} 置いた場所: {action}")
    env.render()
    turn += 1

if done:
    print("ゲーム終了")
    print(f"最終スコア: {env.board.score()}")
    print(f"最終報酬: {reward}")