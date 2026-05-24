from connect4.game_logic import COLUMNS, EMPTY, GameStatus, Connect4Game


SYMBOLS = {
    EMPTY: ".",
    1: "X",
    2: "O",
}


def print_board(game: Connect4Game) -> None:
    print()
    print(" ".join(str(number) for number in range(1, COLUMNS + 1)))
    for row in game.board:
        print(" ".join(SYMBOLS[cell] for cell in row))
    print()


def print_result(game: Connect4Game) -> None:
    if game.status == GameStatus.PLAYER_ONE_WON:
        print("Wygral gracz 1 (X).")
    elif game.status == GameStatus.PLAYER_TWO_WON:
        print("Wygral gracz 2 (O).")
    else:
        print("Remis.")


def main() -> None:
    game = Connect4Game()

    print("Connect 4 - pierwszy etap projektu")
    print("Wpisz numer kolumny od 1 do 7.")

    while game.status == GameStatus.IN_PROGRESS:
        print_board(game)
        user_input = input(f"Ruch gracza {game.current_player}: ")

        try:
            column = int(user_input) - 1
            game.drop_piece(column)
        except ValueError as error:
            print(f"Nie mozna wykonac ruchu: {error}")

    print_board(game)
    print_result(game)


if __name__ == "__main__":
    main()
