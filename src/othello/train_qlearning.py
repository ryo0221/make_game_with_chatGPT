# train_qlearning.py
import argparse
import pickle
from pathlib import Path
from othello.env import OthelloEnv
from othello.ai import QLearningAgent, BLACK, WHITE

def train(episodes: int, output_file: str):
    output_path = Path(output_file)
    output_dir = output_path.parent

    # 学習開始前にディレクトリを確認
    if not output_dir.exists():
        print(f"出力先ディレクトリ {output_dir} は存在しません。")
        choice = input("作成しますか？ (y/n): ").strip().lower()
        if choice == "y":
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"ディレクトリ {output_dir} を作成しました。")
        else:
            print("処理を中止します。")
            return

    env = OthelloEnv()
    agent_black = QLearningAgent(player=BLACK)
    agent_white = QLearningAgent(player=WHITE)

    for episode in range(episodes):
        env.reset()
        done = False
        while not done:
            player = env.current_player
            agent = agent_black if player == BLACK else agent_white
            action = agent.select_action(env)

            if action is None:
                env.current_player = -player
                if not env.legal_actions():
                    done = True
                continue

            #  step() の前に状態キーを保存
            state_key = agent._state_key(env)

            obs, reward, done, _ = env.step(action)

            # step() の後に状態キーを取得
            next_state_key = agent._state_key(env)

            agent.update(
                state_key,           # current_state_key
                action,
                reward if player == BLACK else -reward,
                next_state_key,
                - env.current_player,
                done
            )


        if episode % 500 == 0:
            print(f"Episode {episode} finished")

    # Qテーブル保存
    with output_path.open("wb") as f:
        pickle.dump(agent_black.q_table, f)

    print(f"Training finished and Q-table saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Q-Learning Othello agent")
    parser.add_argument("--episodes", type=int, default=500, help="Number of training episodes")
    parser.add_argument(
        "--output",
        type=str,
        default="./models/QLearning/q_table.pkl",
        help="Path to save Q-table",
    )
    args = parser.parse_args()

    train(args.episodes, args.output)
