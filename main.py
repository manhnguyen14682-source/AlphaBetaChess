from src.controller import ChessController


def main() -> None:
    app = ChessController(ai_depth=3)
    app.run()


if __name__ == "__main__":
    main()
