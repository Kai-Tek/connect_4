from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


ROWS = 6
COLUMNS = 7
EMPTY = 0
PLAYER_ONE = 1
PLAYER_TWO = 2
CONNECT_LENGTH = 4


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    PLAYER_ONE_WON = "player_one_won"
    PLAYER_TWO_WON = "player_two_won"
    DRAW = "draw"


@dataclass
class Connect4Game:
    board: list[list[int]] = field(
        default_factory=lambda: [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
    )
    current_player: int = PLAYER_ONE
    status: GameStatus = GameStatus.IN_PROGRESS
    moves_count: int = 0

    def drop_piece(self, column: int) -> tuple[int, int]:
        if self.status != GameStatus.IN_PROGRESS:
            raise ValueError("Gra jest juz zakonczona.")

        if column < 0 or column >= COLUMNS:
            raise ValueError("Wybrana kolumna jest poza plansza.")

        row = self._find_free_row(column)
        if row is None:
            raise ValueError("Ta kolumna jest juz pelna.")

        self.board[row][column] = self.current_player
        self.moves_count += 1
        self._update_status_after_move(row, column)

        if self.status == GameStatus.IN_PROGRESS:
            self._switch_player()

        return row, column

    def reset(self) -> None:
        self.board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_player = PLAYER_ONE
        self.status = GameStatus.IN_PROGRESS
        self.moves_count = 0

    def _find_free_row(self, column: int) -> Optional[int]:
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][column] == EMPTY:
                return row
        return None

    def _switch_player(self) -> None:
        self.current_player = PLAYER_TWO if self.current_player == PLAYER_ONE else PLAYER_ONE

    def _update_status_after_move(self, row: int, column: int) -> None:
        if self._has_winning_line(row, column):
            self.status = (
                GameStatus.PLAYER_ONE_WON
                if self.current_player == PLAYER_ONE
                else GameStatus.PLAYER_TWO_WON
            )
        elif self._is_board_full():
            self.status = GameStatus.DRAW

    def _is_board_full(self) -> bool:
        return all(self.board[0][column] != EMPTY for column in range(COLUMNS))

    def _has_winning_line(self, row: int, column: int) -> bool:
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]

        for row_step, column_step in directions:
            count = 1
            count += self._count_pieces(row, column, row_step, column_step)
            count += self._count_pieces(row, column, -row_step, -column_step)

            if count >= CONNECT_LENGTH:
                return True

        return False

    def _count_pieces(
        self, start_row: int, start_column: int, row_step: int, column_step: int
    ) -> int:
        player = self.board[start_row][start_column]
        row = start_row + row_step
        column = start_column + column_step
        count = 0

        while (
            0 <= row < ROWS
            and 0 <= column < COLUMNS
            and self.board[row][column] == player
        ):
            count += 1
            row += row_step
            column += column_step

        return count
