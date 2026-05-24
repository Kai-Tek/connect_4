import unittest

from connect4.game_logic import (
    COLUMNS,
    ROWS,
    EMPTY,
    PLAYER_ONE,
    PLAYER_TWO,
    GameStatus,
    Connect4Game,
)


class Connect4GameTests(unittest.TestCase):
    def test_new_game_has_empty_board_and_player_one_starts(self):
        game = Connect4Game()

        self.assertEqual(game.current_player, PLAYER_ONE)
        self.assertEqual(game.status, GameStatus.IN_PROGRESS)
        self.assertEqual(game.moves_count, 0)
        self.assertEqual(game.board, [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)])

    def test_piece_falls_to_lowest_free_row(self):
        game = Connect4Game()

        row, column = game.drop_piece(3)

        self.assertEqual((row, column), (ROWS - 1, 3))
        self.assertEqual(game.board[ROWS - 1][3], PLAYER_ONE)
        self.assertEqual(game.moves_count, 1)

    def test_players_switch_after_valid_move(self):
        game = Connect4Game()

        game.drop_piece(0)

        self.assertEqual(game.current_player, PLAYER_TWO)

    def test_cannot_drop_piece_outside_board(self):
        game = Connect4Game()

        with self.assertRaises(ValueError):
            game.drop_piece(COLUMNS)

    def test_cannot_drop_piece_into_full_column(self):
        game = Connect4Game()

        for _ in range(ROWS):
            game.drop_piece(0)

        with self.assertRaises(ValueError):
            game.drop_piece(0)

    def test_horizontal_win(self):
        game = Connect4Game()

        game.drop_piece(0)
        game.drop_piece(0)
        game.drop_piece(1)
        game.drop_piece(1)
        game.drop_piece(2)
        game.drop_piece(2)
        game.drop_piece(3)

        self.assertEqual(game.status, GameStatus.PLAYER_ONE_WON)

    def test_vertical_win(self):
        game = Connect4Game()

        game.drop_piece(0)
        game.drop_piece(1)
        game.drop_piece(0)
        game.drop_piece(1)
        game.drop_piece(0)
        game.drop_piece(1)
        game.drop_piece(0)

        self.assertEqual(game.status, GameStatus.PLAYER_ONE_WON)

    def test_diagonal_win(self):
        game = Connect4Game()

        game.drop_piece(0)
        game.drop_piece(1)
        game.drop_piece(1)
        game.drop_piece(2)
        game.drop_piece(3)
        game.drop_piece(2)
        game.drop_piece(2)
        game.drop_piece(3)
        game.drop_piece(3)
        game.drop_piece(4)
        game.drop_piece(3)

        self.assertEqual(game.status, GameStatus.PLAYER_ONE_WON)


if __name__ == "__main__":
    unittest.main()
