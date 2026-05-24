import socket
import threading
from typing import Callable, Optional

from connect4.network_protocol import decode_message, encode_message


MessageHandler = Callable[[dict], None]
DisconnectHandler = Callable[[], None]


class GuiNetworkClient:
    def __init__(
        self,
        host: str,
        port: int,
        on_message: MessageHandler,
        on_disconnect: DisconnectHandler,
        connect_timeout: float = 3,
    ) -> None:
        self.host = host
        self.port = port
        self.on_message = on_message
        self.on_disconnect = on_disconnect
        self.connect_timeout = connect_timeout
        self.socket: Optional[socket.socket] = None
        self.socket_file = None
        self.running = False

    def connect(self) -> None:
        self.socket = socket.create_connection((self.host, self.port), timeout=self.connect_timeout)
        self.socket.settimeout(None)
        self.socket_file = self.socket.makefile("rwb")
        self.running = True

        thread = threading.Thread(target=self._read_messages, daemon=True)
        thread.start()

    def send_move(self, column: int) -> None:
        self._send("move", column=column)

    def close(self) -> None:
        self.running = False

        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

        if self.socket_file is not None:
            try:
                self.socket_file.close()
            except OSError:
                pass
            self.socket_file = None

        if self.socket is not None:
            try:
                self.socket.close()
            except OSError:
                pass
            self.socket = None

    def _send(self, message_type: str, **data) -> None:
        if self.socket_file is None:
            return

        self.socket_file.write(encode_message(message_type, **data))
        self.socket_file.flush()

    def _read_messages(self) -> None:
        try:
            for line in self.socket_file:
                if not self.running:
                    break
                self.on_message(decode_message(line))
        except (ConnectionError, OSError, ValueError):
            pass
        finally:
            if self.running:
                self.on_disconnect()
