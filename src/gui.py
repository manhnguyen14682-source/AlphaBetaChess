from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

import chess


ASSET_NAMES = {
    "P": "wp",
    "N": "wn",
    "B": "wb",
    "R": "wr",
    "Q": "wq",
    "K": "wk",
    "p": "bp",
    "n": "bn",
    "b": "bb",
    "r": "br",
    "q": "bq",
    "k": "bk",
}


class ChessGUI:
    def __init__(self, root: tk.Tk, on_square_click):
        self.root = root
        self.on_square_click = on_square_click
        self.square_size = 80
        self.selected_square: int | None = None
        self.highlight_moves: set[int] = set()
        self.last_ai_move_squares: set[int] = set()
        self.player_perspective = chess.WHITE

        self.root.title("Alpha-Beta Chess")
        self.root.geometry("720x700")
        self.root.minsize(520, 560)

        self.container = ttk.Frame(self.root, padding=12)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="White to move")

        self.canvas = tk.Canvas(
            self.container,
            width=self.square_size * 8,
            height=self.square_size * 8,
            highlightthickness=0,
            bg="#202020",
        )
        self.canvas.pack(pady=(0, 12))
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        info_row = ttk.Frame(self.container)
        info_row.pack(fill=tk.X)

        self.status_label = ttk.Label(
            info_row,
            textvariable=self.status_var,
            font=("Segoe UI", 11, "bold")
        )
        self.status_label.pack(side=tk.LEFT)

        self.reset_button = ttk.Button(info_row, text="New Game")
        self.reset_button.pack(side=tk.RIGHT)

        self.piece_images = self._load_piece_images()

    def _load_piece_images(self) -> dict[str, tk.PhotoImage]:
        images = {}
        asset_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

        for symbol, name in ASSET_NAMES.items():
            path = os.path.join(asset_dir, f"{name}.png")

            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing asset: {path}")

            images[symbol] = tk.PhotoImage(file=path)

        return images

    def draw_board(self, board: chess.Board) -> None:
        self.canvas.delete("all")

        light = "#f0d9b5"
        dark = "#b58863"
        last_ai_move = "#d65050"
        selected = "#f6f669"
        hint = "#8ccf7f"

        for rank in range(8):
            for file in range(8):
                if self.player_perspective == chess.BLACK:
                    display_file = 7 - file
                    display_rank = 7 - rank
                else:
                    display_file = file
                    display_rank = rank

                x1 = file * self.square_size
                y1 = rank * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                square = chess.square(display_file, 7 - display_rank)

                color = light if (rank + file) % 2 == 0 else dark
                if square in self.last_ai_move_squares:
                    color = last_ai_move
                if self.selected_square == square:
                    color = selected
                elif square in self.highlight_moves:
                    color = hint

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

                piece = board.piece_at(square)
                if piece:
                    img = self.piece_images[piece.symbol()]
                    self.canvas.create_image(
                        x1 + self.square_size / 2,
                        y1 + self.square_size / 2,
                        image=img
                    )

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def set_selection(self, square: int | None, legal_targets: set[int] | None = None) -> None:
        self.selected_square = square
        self.highlight_moves = legal_targets or set()

    def set_last_ai_move(self, from_square: int | None, to_square: int | None) -> None:
        if from_square is None or to_square is None:
            self.last_ai_move_squares = set()
            return
        self.last_ai_move_squares = {from_square, to_square}

    def set_perspective(self, color: int) -> None:
        self.player_perspective = color

    def _on_canvas_click(self, event: tk.Event) -> None:
        file = event.x // self.square_size
        rank_from_top = event.y // self.square_size

        if not (0 <= file <= 7 and 0 <= rank_from_top <= 7):
            return

        if self.player_perspective == chess.BLACK:
            file = 7 - file
            rank_from_top = 7 - rank_from_top

        rank = 7 - rank_from_top
        square = chess.square(file, rank)
        self.on_square_click(square)