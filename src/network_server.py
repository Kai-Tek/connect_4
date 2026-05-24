import socket
import threading
from typing import Dict, Optional

from connect4.game_logic import GameStatus, Connect4Game
from connect4.network_protocol import (
    decode_message,
    encode_message,
    encode_raw_message,
    make_state_message,
)


HOST = "0.0.0.0"
PORT = 5000
MAX_PLAYERS = 2


class ClientConnection:
    def __init__(self, socket_file, player_number: int) -> None:
        self.socket_file = socket_file
        self.player_number = player_number

    def send(self, message_type: str, **data) -> None:
        self.socket_file.write(encode_message(message_type, **data))
        self.socket_file.flush()

    def send_message(self, message: dict) -> None:
        self.socket_file.write(encode_raw_message(message))
        self.socket_file.flush()


class Connect4Server:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.game = Connect4Game()
        self.clients: Dict[int, ClientConnection] = {}
        self.lock = threading.Lock()

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(MAX_PLAYERS)

            print(f"Serwer Connect 4 dziala na porcie {self.port}.")
            print("Czekam na dwoch graczy...")

            while True:
                client_socket, address = server_socket.accept()
                player_number = self.add_client(client_socket)

                if player_number is None:
                    client_socket.close()
                    continue

                print(f"Gracz {player_number} dolaczyl: {address[0]}:{address[1]}")
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, player_number),
                    daemon=True,
                )
                thread.start()

    def add_client(self, client_socket: socket.socket) -> Optional[int]:
        with self.lock:
            if len(self.clients) >= MAX_PLAYERS:
                return None

            player_number = 1 if 1 not in self.clients else 2
            socket_file = client_socket.makefile("rwb")
            self.clients[player_number] = ClientConnection(socket_file, player_number)
            return player_number

    def handle_client(self, client_socket: socket.socket, player_number: int) -> None:
        client = self.clients[player_number]

        try:
            client.send("welcome", player=player_number)
            self.broadcast_state()

            for line in client.socket_file:
                message = decode_message(line)
                self.handle_message(player_number, message)
        except ConnectionError:
            pass
        finally:
            self.remove_client(player_number)
            client_socket.close()

    def handle_message(self, player_number: int, message: dict) -> None:
        if message.get("type") != "move":
            return

        column = message.get("column")
        if not isinstance(column, int):
            self.clients[player_number].send("error", text="Niepoprawny format ruchu.")
            return

        with self.lock:
            if len(self.clients) < MAX_PLAYERS:
                self.clients[player_number].send("error", text="Czekamy na drugiego gracza.")
                return

            if self.game.status != GameStatus.IN_PROGRESS:
                self.clients[player_number].send("error", text="Gra jest juz zakonczona.")
                return

            if self.game.current_player != player_number:
                self.clients[player_number].send("error", text="To nie jest twoja tura.")
                return

            try:
                self.game.drop_piece(column)
            except ValueError as error:
                self.clients[player_number].send("error", text=str(error))
                return

            self.broadcast_state_locked()

    def broadcast_state(self) -> None:
        with self.lock:
            self.broadcast_state_locked()

    def broadcast_state_locked(self) -> None:
        if len(self.clients) < MAX_PLAYERS:
            message = make_state_message(self.game, "Czekamy na drugiego gracza.")
        else:
            message = make_state_message(self.game)

        for client in self.clients.values():
            client.send_message(message)

    def remove_client(self, player_number: int) -> None:
        with self.lock:
            if player_number in self.clients:
                del self.clients[player_number]
                print(f"Gracz {player_number} rozlaczyl sie.")

            self.game.reset()
            for client in self.clients.values():
                client.send("opponent_left", text="Drugi gracz rozlaczyl sie. Gra zostala zresetowana.")
                client.send_message(make_state_message(self.game, "Czekamy na drugiego gracza."))


def main() -> None:
    server = Connect4Server()
    server.run()


if __name__ == "__main__":
    main()
