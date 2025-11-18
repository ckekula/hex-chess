"""
AI Engine for Glinski's Hex Chess using Minimax with Alpha-Beta Pruning.
"""

import time
from typing import Optional, Tuple, List
from hex_board import HexBoard
from evaluation import Evaluator
from game import MoveGenerator, MoveValidator

class HexChessEngine:
    """Chess engine using minimax with alpha-beta pruning."""
    
    def __init__(self, board_size: int = 6):
        self.evaluator = Evaluator(board_size)
        self.nodes_searched = 0
    
    def get_best_move(self, board: HexBoard, depth: int = 2) -> Optional[Tuple]:
        """Find the best move using minimax."""
        self.nodes_searched = 0
        best_move = None
        best_score = float('-inf') if board.current_turn == 'white' else float('inf')
        is_maximizing = (board.current_turn == 'white')
        
        moves = self._get_all_legal_moves(board, board.current_turn)
        
        for from_q, from_r, to_q, to_r in moves:
            piece, captured = self._make_move(board, from_q, from_r, to_q, to_r)
            score = self._minimax(board, depth - 1, float('-inf'), float('inf'), not is_maximizing)
            self._undo_move(board, from_q, from_r, to_q, to_r, piece, captured)
            
            if is_maximizing and score > best_score:
                best_score = score
                best_move = (from_q, from_r, to_q, to_r)
            elif not is_maximizing and score < best_score:
                best_score = score
                best_move = (from_q, from_r, to_q, to_r)
        
        return best_move
    
    def _minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, 
                 is_maximizing: bool) -> int:
        """Minimax with alpha-beta pruning."""
        self.nodes_searched += 1
        
        if depth == 0:
            return self.evaluator.evaluate_position(board)
        
        color = 'white' if is_maximizing else 'black'
        moves = self._get_all_legal_moves(board, color)
        
        if not moves:
            return self.evaluator.evaluate_position(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for from_q, from_r, to_q, to_r in moves:
                piece, captured = self._make_move(board, from_q, from_r, to_q, to_r)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                self._undo_move(board, from_q, from_r, to_q, to_r, piece, captured)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for from_q, from_r, to_q, to_r in moves:
                piece, captured = self._make_move(board, from_q, from_r, to_q, to_r)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                self._undo_move(board, from_q, from_r, to_q, to_r, piece, captured)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def _get_all_legal_moves(self, board: HexBoard, color: str) -> List[Tuple]:
        """Get all legal moves for a color."""
        move_gen = MoveGenerator(board)
        move_validator = MoveValidator(board)
        moves = []
        
        for (q, r), tile in board.tiles.items():
            if tile.has_piece() and tile.get_piece()[0] == color:
                for to_q, to_r in move_gen.get_legal_moves(q, r):
                    if move_validator.simulate_move(q, r, to_q, to_r):
                        moves.append((q, r, to_q, to_r))
        return moves
    
    def _make_move(self, board: HexBoard, from_q: int, from_r: int, 
                   to_q: int, to_r: int) -> Tuple:
        """Make a move and return state for undo."""
        from_tile = board.get_tile(from_q, from_r)
        to_tile = board.get_tile(to_q, to_r)
        piece = from_tile.piece
        captured = to_tile.piece
        to_tile.piece = piece
        from_tile.piece = None
        board.current_turn = "black" if board.current_turn == "white" else "white"
        return piece, captured
    
    def _undo_move(self, board: HexBoard, from_q: int, from_r: int,
                   to_q: int, to_r: int, piece: Tuple, captured: Optional[Tuple]):
        """Undo a move."""
        from_tile = board.get_tile(from_q, from_r)
        to_tile = board.get_tile(to_q, to_r)
        from_tile.piece = piece
        to_tile.piece = captured
        board.current_turn = "black" if board.current_turn == "white" else "white"
