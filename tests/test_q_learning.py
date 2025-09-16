from othello.env import OthelloEnv, BLACK, WHITE
from othello.ai import QLearningAgent

env = OthelloEnv()
agent = QLearningAgent(actions=64)

for episode in range(10000):
    state = agent.get_state_key(env.reset(), env.current_player)
    done = False
    
    while not done:
        action = agent.select_action(env)
        next_state, reward, done, info = env.step(action)
        
        # プレイヤーの視点で報酬を調整
        if done:
            # 黒勝ち = +1, 白勝ち = -1 （黒視点）
            black_score, white_score = env.board.count_score()
            if black_score > white_score:
                final_reward = 1 if env.current_player == BLACK else -1
            elif white_score > black_score:
                final_reward = -1 if env.current_player == BLACK else 1
            else:
                final_reward = 0
        else:
            final_reward = 0
        
        next_state_key = agent.get_state_key(env.board, env.current_player)
        agent.update(state, action, final_reward, next_state_key, done)
        state = next_state_key
    
    if episode % 100 == 0:
        print(f"Episode {episode} finished")