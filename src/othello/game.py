from othello.env import OthelloBoard, BLACK, WHITE

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
    