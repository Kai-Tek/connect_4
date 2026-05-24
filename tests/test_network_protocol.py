import unittest

from connect4.game_logic import Connect4Game, GameStatus
from connect4.network_protocol import (
    decode_message,
    encode_message,
    encode_raw_message,
    make_state_message,
)


class NetworkProtocolTests(unittest.TestCase):
    def test_message_can_be_encoded_and_decoded(self):
        encoded = encode_message("move", column=3)

        decoded = decode_message(encoded)

        self.assertEqual(decoded, {"type": "move", "column": 3})

    def test_raw_message_can_be_encoded_and_decoded(self):
        message = {"type": "state", "current_player": 1}

        decoded = decode_message(encode_raw_message(message))

        self.assertEqual(decoded, message)

    def test_state_message_contains_public_game_state(self):
        game = Connect4Game()
        game.drop_piece(0)

        message = make_state_message(game, "Test")

        self.assertEqual(message["type"], "state")
        self.assertEqual(message["board"], game.board)
        self.assertEqual(message["current_player"], 2)
        self.assertEqual(message["status"], GameStatus.IN_PROGRESS.value)
        self.assertEqual(message["moves_count"], 1)
        self.assertEqual(message["text"], "Test")


if __name__ == "__main__":
    unittest.main()
