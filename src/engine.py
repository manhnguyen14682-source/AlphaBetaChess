from __future__ import annotations

from dataclasses import dataclass

import chess


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


@dataclass
class AlphaBetaEngine:
    depth: int = 3

    def search_best_move(self, board: chess.Board) -> chess.Move | None:
        if board.is_game_over():
            return None
        maximizing = board.turn == chess.WHITE
        best_score = float("-inf") if maximizing else float("inf")
        best_move: chess.Move | None = None
        for move in self._order_moves(board):
            board.push(move)
            score = self._alphabeta(
                board,
                self.depth - 1,
                alpha=float("-inf"),
                beta=float("inf"),
                maximizing=not maximizing,
            )
            board.pop()
            if maximizing and score > best_score:
                best_score = score
                best_move = move
            if not maximizing and score < best_score:
                best_score = score
                best_move = move

        return best_move

    def _alphabeta(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        if depth == 0 or board.is_game_over():
            return self._evaluate(board)

        if maximizing:
            value = float("-inf")
            for move in self._order_moves(board):
                board.push(move)
                value = max(value, self._alphabeta(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        value = float("inf")
        for move in self._order_moves(board):
            board.push(move)
            value = min(value, self._alphabeta(board, depth - 1, alpha, beta, True))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

    def _evaluate(self, board: chess.Board) -> float:
        if board.is_checkmate():
            # If side to move is checkmated, the previous player has won.
            return -100000 if board.turn == chess.WHITE else 100000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        score = 0
        for piece_type, value in PIECE_VALUES.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value
        turn = board.turn
        board.turn = chess.WHITE
        white_mobility = board.legal_moves.count()
        board.turn = chess.BLACK
        black_mobility = board.legal_moves.count()
        board.turn = turn
        score += (white_mobility - black_mobility) * 2
        if board.is_check():
            score += -30 if board.turn == chess.WHITE else 30
        return score

    def _order_moves(self, board: chess.Board) -> list[chess.Move]:
        moves = list(board.legal_moves)
        def move_score(move: chess.Move) -> int:
            score = 0
            if board.is_capture(move):
                score += 50
            if move.promotion:
                score += 80
            if board.gives_check(move):
                score += 40
            return score
        moves.sort(key=move_score, reverse=True)
        return moves
