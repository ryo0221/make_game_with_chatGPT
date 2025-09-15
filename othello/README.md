```mermaid
classDiagram
    class OthelloBoard {
        - board: List[List[int]]
        + reset(): void
        + valid_moves(player: int) List[(int,int)]
        + make_move(player: int, r: int, c: int): bool
        + score(): (int, int)
        + is_full(): bool
    }

    class OthelloGame {
        - board: OthelloBoard
        - turn: int
        + switch_turn(): void
        + is_game_over(): bool
        + get_winner(): int
    }

    class OthelloEnv {
        - game: OthelloGame
        + reset(): (state, turn)
        + get_state(): (state, turn)
        + step(move): (state, reward, done)
        + get_reward(done: bool): int
    }

    class AbstractAI {
        <<abstract>>
        + get_move(board: OthelloBoard): (int, int)
    }

    class RandomAI {
        + get_move(board: OthelloBoard): (int, int)
    }

    class MinimaxAI {
        - depth: int
        + get_move(board: OthelloBoard): (int, int)
        - minimax(board, depth, maximizing): int
    }

    OthelloGame --> OthelloBoard : uses
    OthelloEnv --> OthelloGame : manages
    AbstractAI <|-- RandomAI
    AbstractAI <|-- MinimaxAI
    ```