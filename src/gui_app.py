import threading
import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional

from connect4.game_logic import COLUMNS, EMPTY, ROWS, GameStatus, Connect4Game
from connect4.gui_network_client import GuiNetworkClient
from network_server import Connect4Server, PORT


CELL_SIZE = 68
BOARD_PADDING = 14
DROP_ZONE_HEIGHT = 74
DISC_MARGIN = 7
BOARD_COLOR = "#2563eb"
EMPTY_COLOR = "#f8fafc"
BACKGROUND_COLOR = "#e2e8f0"
HIGHLIGHT_COLOR = "#93c5fd"
PLAYER_COLORS = {
    1: "#ef4444",
    2: "#facc15",
}


class Connect4Gui:
    def __init__(self) -> None:
        self.game = Connect4Game()
        self.mode = "local"
        self.network_client: Optional[GuiNetworkClient] = None
        self.network_player_number: Optional[int] = None
        self.network_waiting = False
        self.connection_in_progress = False
        self.server_started = False
        self.dragging_disc = False
        self.drag_x = 0
        self.drag_y = 0
        self.hover_column = None

        self.root = tk.Tk()
        self.root.title("Connect 4")
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        self.menu_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=48, pady=42)
        self.join_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=48, pady=34)
        self.game_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.create_menu()
        self.create_join_view()
        self.create_game_view()
        self.show_menu()

    def create_menu(self) -> None:
        title = tk.Label(
            self.menu_frame,
            text="Connect 4",
            font=("Segoe UI", 30, "bold"),
            bg=BACKGROUND_COLOR,
            fg="#0f172a",
        )
        title.pack(pady=(0, 8))

        subtitle = tk.Label(
            self.menu_frame,
            text="Projekt gry sieciowej",
            font=("Segoe UI", 13),
            bg=BACKGROUND_COLOR,
            fg="#475569",
        )
        subtitle.pack(pady=(0, 28))

        local_game_button = tk.Button(
            self.menu_frame,
            text="Gra lokalna",
            font=("Segoe UI", 13),
            width=22,
            command=self.start_local_game,
        )
        local_game_button.pack(pady=6)

        host_game_button = tk.Button(
            self.menu_frame,
            text="Hostuj gre",
            font=("Segoe UI", 13),
            width=22,
            command=self.host_network_game,
        )
        host_game_button.pack(pady=6)

        join_game_button = tk.Button(
            self.menu_frame,
            text="Dolacz do gry",
            font=("Segoe UI", 13),
            width=22,
            command=self.show_join_view,
        )
        join_game_button.pack(pady=6)

        exit_button = tk.Button(
            self.menu_frame,
            text="Wyjscie",
            font=("Segoe UI", 13),
            width=22,
            command=self.root.destroy,
        )
        exit_button.pack(pady=6)

    def create_join_view(self) -> None:
        title = tk.Label(
            self.join_frame,
            text="Dolacz do gry",
            font=("Segoe UI", 24, "bold"),
            bg=BACKGROUND_COLOR,
            fg="#0f172a",
        )
        title.pack(pady=(0, 18))

        label = tk.Label(
            self.join_frame,
            text="Adres IP serwera",
            font=("Segoe UI", 12),
            bg=BACKGROUND_COLOR,
            fg="#334155",
        )
        label.pack(anchor="w")

        self.host_entry = tk.Entry(self.join_frame, font=("Segoe UI", 13), width=26)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(pady=(4, 16))

        self.connect_button = tk.Button(
            self.join_frame,
            text="Polacz",
            font=("Segoe UI", 13),
            width=22,
            command=self.join_network_game,
        )
        self.connect_button.pack(pady=6)

        back_button = tk.Button(
            self.join_frame,
            text="Wroc",
            font=("Segoe UI", 13),
            width=22,
            command=self.show_menu,
        )
        back_button.pack(pady=6)

    def create_game_view(self) -> None:
        self.status_label = tk.Label(
            self.game_frame,
            text="Tura gracza 1",
            font=("Segoe UI", 16, "bold"),
            bg=BACKGROUND_COLOR,
            fg="#0f172a",
            pady=12,
        )
        self.status_label.pack()

        board_width = COLUMNS * CELL_SIZE + BOARD_PADDING * 2
        board_height = DROP_ZONE_HEIGHT + ROWS * CELL_SIZE + BOARD_PADDING * 2
        self.canvas = tk.Canvas(
            self.game_frame,
            width=board_width,
            height=board_height,
            bg=BACKGROUND_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=18, pady=8)
        self.canvas.bind("<Button-1>", self.handle_mouse_down)
        self.canvas.bind("<B1-Motion>", self.handle_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_mouse_release)

        controls_frame = tk.Frame(self.game_frame, bg=BACKGROUND_COLOR)
        controls_frame.pack(pady=(8, 16))

        self.reset_button = tk.Button(
            controls_frame,
            text="Nowa gra",
            font=("Segoe UI", 12),
            command=self.reset_game,
        )
        self.reset_button.pack(side=tk.LEFT, padx=8)

        self.menu_button = tk.Button(
            controls_frame,
            text="Menu",
            font=("Segoe UI", 12),
            command=self.show_menu,
        )
        self.menu_button.pack(side=tk.LEFT, padx=8)

        self.draw_board()

    def run(self) -> None:
        self.root.mainloop()

    def show_menu(self) -> None:
        self.disconnect_from_network()
        self.game_frame.pack_forget()
        self.join_frame.pack_forget()
        self.menu_frame.pack()

    def show_join_view(self) -> None:
        self.menu_frame.pack_forget()
        self.game_frame.pack_forget()
        self.join_frame.pack()

    def start_local_game(self) -> None:
        self.disconnect_from_network()
        self.mode = "local"
        self.network_player_number = None
        self.network_waiting = False
        self.reset_button.config(state=tk.NORMAL)
        self.reset_game()
        self.menu_frame.pack_forget()
        self.join_frame.pack_forget()
        self.game_frame.pack()

    def host_network_game(self) -> None:
        self.start_server_if_needed()
        self.connect_to_network_game("127.0.0.1", retry_count=10)

    def join_network_game(self) -> None:
        host = self.host_entry.get().strip()
        if not host:
            messagebox.showwarning("Brak adresu", "Wpisz adres IP serwera.")
            return

        self.connect_to_network_game(host, retry_count=1)

    def start_server_if_needed(self) -> None:
        if self.server_started:
            return

        server = Connect4Server()
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        self.server_started = True

    def connect_to_network_game(self, host: str, retry_count: int) -> None:
        if self.connection_in_progress:
            return

        self.disconnect_from_network()
        self.connection_in_progress = True
        self.mode = "network"
        self.network_player_number = None
        self.network_waiting = True
        self.game.reset()
        self.draw_board()
        self.status_label.config(text="Laczenie z serwerem...")
        self.connect_button.config(state=tk.DISABLED)

        client = GuiNetworkClient(
            host,
            PORT,
            on_message=lambda message: self.root.after(0, self.handle_network_message, message),
            on_disconnect=lambda: self.root.after(0, self.handle_network_disconnect),
        )

        thread = threading.Thread(
            target=self.connect_to_network_game_in_background,
            args=(client, retry_count),
            daemon=True,
        )
        thread.start()

    def connect_to_network_game_in_background(
        self, client: GuiNetworkClient, retry_count: int
    ) -> None:
        last_error = None
        for _ in range(retry_count):
            try:
                client.connect()
                self.root.after(0, self.handle_network_connect_success, client)
                return
            except OSError as error:
                last_error = error
                time.sleep(0.1)

        self.root.after(0, self.handle_network_connect_error, last_error)

    def handle_network_connect_success(self, client: GuiNetworkClient) -> None:
        self.connection_in_progress = False
        self.network_client = client
        self.connect_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)
        self.menu_frame.pack_forget()
        self.join_frame.pack_forget()
        self.game_frame.pack()

    def handle_network_connect_error(self, error: Optional[OSError]) -> None:
        self.connection_in_progress = False
        self.mode = "local"
        self.network_waiting = False
        self.connect_button.config(state=tk.NORMAL)
        self.status_label.config(text="Tura gracza 1")
        messagebox.showerror(
            "Blad polaczenia",
            f"Nie udalo sie polaczyc z serwerem:\n{error}",
        )

    def handle_mouse_down(self, event: tk.Event) -> None:
        if self.game.status != GameStatus.IN_PROGRESS:
            return

        if self.mode == "network" and (
            self.network_waiting or self.network_player_number != self.game.current_player
        ):
            return

        if not self.is_inside_start_disc(event.x, event.y):
            return

        self.dragging_disc = True
        self.drag_x = event.x
        self.drag_y = event.y
        self.hover_column = self.get_column_from_x(event.x)
        self.draw_board()

    def handle_mouse_drag(self, event: tk.Event) -> None:
        if not self.dragging_disc:
            return

        self.drag_x = event.x
        self.drag_y = event.y
        self.hover_column = self.get_column_from_x(event.x)
        self.draw_board()

    def handle_mouse_release(self, event: tk.Event) -> None:
        if self.game.status != GameStatus.IN_PROGRESS:
            return

        column = self.get_column_from_x(event.x)

        if self.dragging_disc:
            self.dragging_disc = False
            self.hover_column = None
            self.draw_board()
            if column is None or not self.is_inside_board(event.x, event.y):
                return
            self.make_move(column)
            return

        if self.is_inside_board(event.x, event.y) and column is not None:
            self.make_move(column)

    def make_move(self, column: int) -> None:
        if self.mode == "network":
            if self.network_waiting:
                messagebox.showwarning("Poczekaj", "Czekamy na drugiego gracza.")
                return

            if self.network_player_number != self.game.current_player:
                messagebox.showwarning("Poczekaj", "To nie jest twoja tura.")
                return

            if self.network_client is not None:
                self.network_client.send_move(column)
            return

        try:
            self.game.drop_piece(column)
        except ValueError as error:
            messagebox.showwarning("Niepoprawny ruch", str(error))
            return

        self.draw_board()
        self.update_status()

    def reset_game(self) -> None:
        if self.mode == "network":
            return

        self.game.reset()
        self.dragging_disc = False
        self.hover_column = None
        self.draw_board()
        self.update_status()

    def draw_board(self) -> None:
        self.canvas.delete("all")
        self.draw_drop_zone()
        self.draw_board_background()

        for row in range(ROWS):
            for column in range(COLUMNS):
                self.draw_disc(row, column)

        self.draw_current_player_disc()

    def draw_drop_zone(self) -> None:
        if self.game.moves_count > 0:
            return

        self.canvas.create_text(
            BOARD_PADDING,
            18,
            text="Przeciagnij pionek nad kolumne albo kliknij kolumne",
            anchor="w",
            fill="#334155",
            font=("Segoe UI", 11),
        )

    def draw_board_background(self) -> None:
        x1 = BOARD_PADDING
        y1 = self.get_board_top()
        x2 = BOARD_PADDING + COLUMNS * CELL_SIZE
        y2 = y1 + ROWS * CELL_SIZE

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=BOARD_COLOR, outline=BOARD_COLOR)

        if self.hover_column is not None:
            highlight_x1 = BOARD_PADDING + self.hover_column * CELL_SIZE
            highlight_x2 = highlight_x1 + CELL_SIZE
            self.canvas.create_rectangle(
                highlight_x1,
                y1,
                highlight_x2,
                y2,
                fill=HIGHLIGHT_COLOR,
                outline=HIGHLIGHT_COLOR,
            )

    def draw_disc(self, row: int, column: int) -> None:
        x1 = BOARD_PADDING + column * CELL_SIZE + DISC_MARGIN
        y1 = self.get_board_top() + row * CELL_SIZE + DISC_MARGIN
        x2 = x1 + CELL_SIZE - DISC_MARGIN * 2
        y2 = y1 + CELL_SIZE - DISC_MARGIN * 2

        cell = self.game.board[row][column]
        color = EMPTY_COLOR if cell == EMPTY else PLAYER_COLORS[cell]

        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=color,
            outline="#1e40af",
            width=2,
        )

    def draw_current_player_disc(self) -> None:
        if self.game.status != GameStatus.IN_PROGRESS:
            return

        if self.mode == "network" and (
            self.network_waiting or self.network_player_number != self.game.current_player
        ):
            return

        radius = (CELL_SIZE - DISC_MARGIN * 2) // 2
        x = self.drag_x if self.dragging_disc else BOARD_PADDING + CELL_SIZE // 2
        y = self.drag_y if self.dragging_disc else DROP_ZONE_HEIGHT // 2 + 12
        color = PLAYER_COLORS[self.game.current_player]

        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=color,
            outline="#334155",
            width=2,
        )

    def get_board_top(self) -> int:
        return DROP_ZONE_HEIGHT + BOARD_PADDING

    def get_column_from_x(self, x: int) -> Optional[int]:
        column = (x - BOARD_PADDING) // CELL_SIZE
        if column < 0 or column >= COLUMNS:
            return None
        return column

    def is_inside_board(self, x: int, y: int) -> bool:
        board_left = BOARD_PADDING
        board_right = BOARD_PADDING + COLUMNS * CELL_SIZE
        board_top = self.get_board_top()
        board_bottom = board_top + ROWS * CELL_SIZE
        return board_left <= x <= board_right and board_top <= y <= board_bottom

    def is_inside_start_disc(self, x: int, y: int) -> bool:
        center_x = BOARD_PADDING + CELL_SIZE // 2
        center_y = DROP_ZONE_HEIGHT // 2 + 12
        radius = (CELL_SIZE - DISC_MARGIN * 2) // 2
        return (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2

    def update_status(self) -> None:
        if self.game.status == GameStatus.IN_PROGRESS:
            if self.mode == "network" and self.network_player_number is not None:
                if self.network_player_number == self.game.current_player:
                    self.status_label.config(text=f"Gracz {self.network_player_number}: twoja tura")
                else:
                    self.status_label.config(text=f"Gracz {self.network_player_number}: tura przeciwnika")
            else:
                self.status_label.config(text=f"Tura gracza {self.game.current_player}")
        elif self.game.status == GameStatus.PLAYER_ONE_WON:
            self.status_label.config(text="Wygral gracz 1")
            messagebox.showinfo("Koniec gry", "Wygral gracz 1.")
        elif self.game.status == GameStatus.PLAYER_TWO_WON:
            self.status_label.config(text="Wygral gracz 2")
            messagebox.showinfo("Koniec gry", "Wygral gracz 2.")
        elif self.game.status == GameStatus.DRAW:
            self.status_label.config(text="Remis")
            messagebox.showinfo("Koniec gry", "Gra zakonczyla sie remisem.")

    def handle_network_message(self, message: dict) -> None:
        message_type = message.get("type")

        if message_type == "welcome":
            self.network_player_number = message["player"]
            self.update_status()
        elif message_type == "state":
            self.game.board = message["board"]
            self.game.current_player = message["current_player"]
            self.game.status = GameStatus(message["status"])
            self.game.moves_count = message["moves_count"]
            self.network_waiting = bool(message.get("text"))
            self.dragging_disc = False
            self.hover_column = None
            self.draw_board()

            if message.get("text"):
                self.status_label.config(text=message["text"])
            else:
                self.update_status()
        elif message_type == "error":
            messagebox.showwarning("Serwer", message["text"])
        elif message_type == "opponent_left":
            messagebox.showinfo("Rozlaczenie", message["text"])

    def handle_network_disconnect(self) -> None:
        if self.mode == "network":
            messagebox.showwarning("Rozlaczenie", "Utracono polaczenie z serwerem.")
            self.show_menu()

    def disconnect_from_network(self) -> None:
        if self.network_client is not None:
            self.network_client.close()
            self.network_client = None
        self.network_waiting = False

    def close_app(self) -> None:
        self.disconnect_from_network()
        self.root.destroy()


def main() -> None:
    app = Connect4Gui()
    app.run()


if __name__ == "__main__":
    main()
