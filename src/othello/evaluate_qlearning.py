import pickle
from pathlib import Path
from othello.env import OthelloEnv, BLACK, WHITE
from othello.ai import QLearningAgent, RandomAI

def play_game(agent_black, agent_white):
    """1ゲーム実行して勝者を返す"""
    env = OthelloEnv()
    env.reset()
    while not env.is_game_over():
        player = env.current_player
        agent = agent_black if player == BLACK else agent_white
        action = agent.select_action(env)
        if action is None:
            env.current_player = -player
            if not env.legal_actions():
                env.done = True
            continue
        env.step(action)

    b, w = env.board.score()
    if b > w:
        return "black"
    elif w > b:
        return "white"
    else:
        return "draw"

def evaluate(model_path: Path, games=100):
    """学習済みモデルを読み込み、ランダムAIと対戦して勝率を計算"""
    with model_path.open("rb") as f:
        q_table = pickle.load(f)

    agent_black = QLearningAgent(player=BLACK, epsilon=0.0)
    agent_black.q_table = q_table
    agent_white = RandomAI(player=WHITE)

    results = {"black": 0, "white": 0, "draw": 0}
    for _ in range(games):
        winner = play_game(agent_black, agent_white)
        results[winner] += 1
    return results

if __name__ == "__main__":
    model_dir = Path("./models/QLearningFeature/")
    for model_file in model_dir.glob("q_table_*.pkl"):
        print(f"Evaluating model: {model_file}")
        results = evaluate(model_file, games=200)
        total = sum(results.values())
        print(f"  Black(Q-learning) wins: {results['black']}/{total}")
        print(f"  White(Random) wins:    {results['white']}/{total}")
        print(f"  Draws:                 {results['draw']}/{total}")
        print("-"*40)