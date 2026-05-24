import socket
import sys
import threading
from typing import Optional

from connect4.game_logic import COLUMNS, EMPTY, GameStatus
from connect4.network_protocol import decode_message, encode_message


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
SYMBOLS = {
    EMPTY: ".",
    1: "X",
    2: "O",
}


class Connect4NetworkClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.player_number: Optional[int] = None
        self.current_player: Optional[int] = None
        self.status = GameStatus.IN_PROGRESS.value
        self.running = True
        self.socket_file = None

    def run(self) -> None:
        with socket.create_connection((self.host, self.port)) as client_socket:
            self.socket_file = client_socket.makefile("rwb")
            reader = threading.Thread(target=self.read_messages, daemon=True)
            reader.start()

            print("Polaczono z serwerem.")
            print("Wpisz numer kolumny od 1 do 7, gdy bedzie twoja tura.")

            while self.running:
                user_input = input("> ").strip()

                if user_input.lower() in {"q", "quit", "exit"}:
                    self.running = False
                    break

                if not user_input:
                    continue

                try:
                    column = int(user_input) - 1
                except ValueError:
                    print("Wpisz liczbe od 1 do 7.")
                    continue

                if column < 0 or column >= COLUMNS:
                    print("Wpisz liczbe od 1 do 7.")
                    continue

                self.send("move", column=column)

    def send(self, message_type: str, **data) -> None:
        if self.socket_file is None:
            return

        self.socket_file.write(encode_message(message_type, **data))
        self.socket_file.flush()

    def read_messages(self) -> None:
        try:
            for line in self.socket_file:
                message = decode_message(line)
                self.handle_message(message)
        except ConnectionError:
            pass
        finally:
            self.running = False
            print("Rozlaczono z serwerem.")

    def handle_message(self, message: dict) -> None:
        message_type = message.get("type")

        if message_type == "welcome":
            self.player_number = message["player"]
            print(f"Jestes graczem {self.player_number}.")
        elif message_type == "state":
            self.current_player = message["current_player"]
            self.status = message["status"]
            self.print_board(message["board"])
            if message.get("text"):
                print(message["text"])
            self.print_turn_or_result()
        elif message_type == "error":
            print(f"Blad: {message['text']}")
        elif message_type == "opponent_left":
            print(message["text"])

    def print_board(self, board: list[list[int]]) -> None:
        print()
        print(" ".join(str(number) for number in range(1, COLUMNS + 1)))
        for row in board:
            print(" ".join(SYMBOLS[cell] for cell in row))
        print()

    def print_turn_or_result(self) -> None:
        if self.status == GameStatus.IN_PROGRESS.value:
            if self.current_player == self.player_number:
                print("Twoja tura.")
            else:
                print(f"Tura gracza {self.current_player}.")
        elif self.status == GameStatus.PLAYER_ONE_WON.value:
            print("Wygral gracz 1.")
        elif self.status == GameStatus.PLAYER_TWO_WON.value:
            print("Wygral gracz 2.")
        elif self.status == GameStatus.DRAW.value:
            print("Remis.")


def main() -> None:
    host = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_PORT
    client = Connect4NetworkClient(host, port)
    client.run()


if __name__ == "__main__":
    main()
