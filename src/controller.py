from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import chess
from .engine import AlphaBetaEngine
from .gui import ChessGUI


class ChessController:
    def __init__(self, ai_depth: int = 3) -> None:
        self.root = tk.Tk()
        self.board = chess.Board()
        self.player_color = chess.WHITE
        self.ai_color = chess.BLACK
        self.engine = AlphaBetaEngine(depth=ai_depth)
        self.gui = ChessGUI(self.root, self.on_square_clicked)
        self.gui.reset_button.configure(command=self.reset_game)
        self.selected_square: int | None = None
        self.reset_game()

    def run(self) -> None:
        self.root.mainloop()

    def reset_game(self) -> None:
        self.board.reset()
        self._choose_player_color()
        self.selected_square = None
        self.gui.set_selection(None, set())
        self.gui.set_last_ai_move(None, None)
        self.gui.set_perspective(self.player_color)
        self.redraw()
        if self.board.turn == self.ai_color:
            self._schedule_ai_move()

    def _choose_player_color(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Side")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        selected_color: int | None = None
        container = ttk.Frame(dialog, padding=16)
        container.pack(fill=tk.BOTH, expand=True)
        ttk.Label(container, text="Choose your side", font=("Segoe UI", 11, "bold")).pack(pady=(0, 12))
        buttons = ttk.Frame(container)
        buttons.pack(fill=tk.X)

        def choose(color: int) -> None:
            nonlocal selected_color
            selected_color = color
            dialog.destroy()

        ttk.Button(buttons, text="White", command=lambda: choose(chess.WHITE)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(buttons, text="Black", command=lambda: choose(chess.BLACK)).pack(side=tk.LEFT)

        def on_close() -> None:
            choose(chess.WHITE)

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.update_idletasks()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        dialog_w = dialog.winfo_width()
        dialog_h = dialog.winfo_height()
        pos_x = root_x + (root_w - dialog_w) // 2
        pos_y = root_y + (root_h - dialog_h) // 2
        dialog.geometry(f"+{max(pos_x, 0)}+{max(pos_y, 0)}")
        self.root.wait_window(dialog)
        if selected_color is None:
            selected_color = chess.WHITE
        self.player_color = selected_color
        self.ai_color = chess.BLACK if selected_color == chess.WHITE else chess.WHITE

    def on_square_clicked(self, square: int) -> None:
        if self.board.is_game_over() or self.board.turn != self.player_color:
            return
        piece = self.board.piece_at(square)
        if self.selected_square is None:
            if piece and piece.color == self.player_color:
                self.selected_square = square
                self._update_selection_hints(square)
                self.redraw()
            return
        if square == self.selected_square:
            self.selected_square = None
            self.gui.set_selection(None, set())
            self.redraw()
            return
        move = chess.Move(self.selected_square, square)
        if self._is_pawn_promotion(move):
            move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
        if move in self.board.legal_moves:
            self.board.push(move)
            self.selected_square = None
            self.gui.set_selection(None, set())
            self.redraw()
            self._schedule_ai_move()
            return
        if piece and piece.color == self.player_color:
            self.selected_square = square
            self._update_selection_hints(square)
            self.redraw()
        else:
            self.selected_square = None
            self.gui.set_selection(None, set())
            self.redraw()

    def _schedule_ai_move(self) -> None:
        if self.board.is_game_over():
            self.redraw()
            return
        self.root.after(120, self._make_ai_move)

    def _make_ai_move(self) -> None:
        if self.board.turn != self.ai_color or self.board.is_game_over():
            self.redraw()
            return
        best = self.engine.search_best_move(self.board)
        if best is not None:
            self.gui.set_last_ai_move(best.from_square, best.to_square)
            self.board.push(best)
        self.redraw()

    def _is_pawn_promotion(self, move: chess.Move) -> bool:
        piece = self.board.piece_at(move.from_square)
        if piece is None or piece.piece_type != chess.PAWN:
            return False
        target_rank = chess.square_rank(move.to_square)
        return target_rank == 0 or target_rank == 7

    def _update_selection_hints(self, square: int) -> None:
        legal_targets = {
            m.to_square
            for m in self.board.legal_moves
            if m.from_square == square
        }
        self.gui.set_selection(square, legal_targets)

    def redraw(self) -> None:
        self.gui.draw_board(self.board)
        self.gui.set_status(self._status_text())

    def _status_text(self) -> str:
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"Checkmate! {winner} wins."
        if self.board.is_stalemate():
            return "Draw: Stalemate"
        if self.board.is_insufficient_material():
            return "Draw: Insufficient material"
        if self.board.can_claim_threefold_repetition():
            return "Draw: Threefold repetition"
        side = "White" if self.board.turn == chess.WHITE else "Black"
        text = f"{side} to move"
        if self.board.is_check():
            text += " - Check"
        return text
