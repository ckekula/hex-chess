"""
AI Engine for Glinski's Hex Chess using Minimax with Alpha-Beta Pruning.

This implements a basic chess engine with:
- Minimax algorithm
- Alpha-beta pruning
- Iterative deepening
- Move ordering
"""

import time
from typing import Optional, Tuple, List
from hex_board import HexBoard
from evaluation import Evaluator
from game import MoveGenerator, MoveValidator

class HexChessEngine:
    """
    Chess engine for hexagonal chess using minimax with alpha-beta pruning.
    """
    
    def __init__(self, board_size: int = 6):
        self.evaluator = Evaluator(board_size)
        self.nodes_searched = 0
        self.best_move = None
        self.time_limit = 5.0  # seconds
        self.start_time = 0
        self.move_gen = None
        self.move_validator = None
    
    def get_best_move(self, board: HexBoard, depth: int = 3, time_limit: float = 5.0) -> Optional[Tuple]:
        """
        Find the best move using iterative deepening minimax.
        
        Args:
            board: Current board state
            depth: Maximum search depth
            time_limit: Time limit in seconds
        
        Returns:
            Tuple of (from_q, from_r, to_q, to_r) or None
        """
        self.time_limit = time_limit
        self.start_time = time.time()
        self.nodes_searched = 0
        self.best_move = None
        
        # Iterative deepening
        for current_depth in range(1, depth + 1):
            if time.time() - self.start_time > self.time_limit * 0.9:
                break
            
            try:
                score = self._minimax_root(board, current_depth)
                print(f"Depth {current_depth}: score={score:+d}, nodes={self.nodes_searched}, move={self.best_move}")
            except TimeoutError:
                print(f"Search timeout at depth {current_depth}")
                break
        
        return self.best_move
    
    def _minimax_root(self, board: HexBoard, depth: int) -> int:
        """Root node of minimax search."""
        is_maximizing = (board.current_turn == 'white')
        alpha = float('-inf')
        beta = float('inf')
        best_score = float('-inf') if is_maximizing else float('inf')
        best_move = None
        
        # Get all possible moves
        moves = self._get_all_legal_moves(board, board.current_turn)
        
        # Order moves for better pruning
        moves = self._order_moves(board, moves)
        
        for from_q, from_r, to_q, to_r in moves:
            if time.time() - self.start_time > self.time_limit:
                raise TimeoutError()
            
            # Make move
            piece, captured = self._make_move(board, from_q, from_r, to_q, to_r)
            
            # Search
            score = self._minimax(board, depth - 1, alpha, beta, not is_maximizing)
            
            # Undo move
            self._undo_move(board, from_q, from_r, to_q, to_r, piece, captured)
            
            # Update best move
            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = (from_q, from_r, to_q, to_r)
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = (from_q, from_r, to_q, to_r)
                beta = min(beta, score)
        
        self.best_move = best_move
        return best_score
    
    def _minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, 
                 is_maximizing: bool) -> int:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            is_maximizing: True if maximizing player (white)
        
        Returns:
            Evaluation score
        """
        self.nodes_searched += 1
        
        # Check time limit
        if time.time() - self.start_time > self.time_limit:
            raise TimeoutError()
        
        # Terminal node or depth limit reached
        if depth == 0:
            return self._quiescence_search(board, alpha, beta, is_maximizing, 2)
        
        # Check for game over
        validator = MoveValidator(board)
        game_status = validator.get_game_status()
        if game_status in ['checkmate', 'stalemate']:
            return self.evaluator.evaluate_position(board)
        
        # Get all legal moves
        color = 'white' if is_maximizing else 'black'
        moves = self._get_all_legal_moves(board, color)
        
        if not moves:
            # No legal moves (shouldn't happen if game status is correct)
            return self.evaluator.evaluate_position(board)
        
        # Order moves for better pruning
        moves = self._order_moves(board, moves)
        
        if is_maximizing:
            max_eval = float('-inf')
            for from_q, from_r, to_q, to_r in moves:
                piece, captured = self._make_move(board, from_q, from_r, to_q, to_r)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                self._undo_move(board, from_q, from_r, to_q, to_r, piece, captured)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
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
                    break  # Alpha cutoff
            return min_eval
    
    def _quiescence_search(self, board: HexBoard, alpha: float, beta: float,
                          is_maximizing: bool, depth: int) -> int:
        """
        Quiescence search to avoid horizon effect.
        Only searches captures to reach a quiet position.
        """
        stand_pat = self.evaluator.evaluate_position(board)
        
        if depth == 0:
            return stand_pat
        
        if is_maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
        
        # Get only capture moves
        color = 'white' if is_maximizing else 'black'
        captures = self._get_capture_moves(board, color)
        
        for from_q, from_r, to_q, to_r in captures:
            piece, captured = self._make_move(board, from_q, from_r, to_q, to_r)
            score = self._quiescence_search(board, alpha, beta, not is_maximizing, depth - 1)
            self._undo_move(board, from_q, from_r, to_q, to_r, piece, captured)
            
            if is_maximizing:
                alpha = max(alpha, score)
                if alpha >= beta:
                    return beta
            else:
                beta = min(beta, score)
                if beta <= alpha:
                    return alpha
        
        return alpha if is_maximizing else beta
    
    def _get_all_legal_moves(self, board: HexBoard, color: str) -> List[Tuple]:
        """Get all legal moves for a color."""
        if self.move_gen is None:
            self.move_gen = MoveGenerator(board)
        if self.move_validator is None:
            self.move_validator = MoveValidator(board)
        
        moves = []
        for (q, r), tile in board.tiles.items():
            if tile.has_piece():
                piece_color, _ = tile.get_piece()
                if piece_color == color:
                    legal_moves = self.move_gen.get_legal_moves(q, r)
                    for to_q, to_r in legal_moves:
                        # Filter moves that leave king in check
                        if self.move_validator.simulate_move(q, r, to_q, to_r):
                            moves.append((q, r, to_q, to_r))
        return moves
    
    def _get_capture_moves(self, board: HexBoard, color: str) -> List[Tuple]:
        """Get only capture moves for quiescence search."""
        if self.move_gen is None:
            self.move_gen = MoveGenerator(board)
        if self.move_validator is None:
            self.move_validator = MoveValidator(board)
        
        captures = []
        for (q, r), tile in board.tiles.items():
            if tile.has_piece():
                piece_color, _ = tile.get_piece()
                if piece_color == color:
                    legal_moves = self.move_gen.get_legal_moves(q, r)
                    for to_q, to_r in legal_moves:
                        target_tile = board.get_tile(to_q, to_r)
                        if target_tile and target_tile.has_piece():
                            if self.move_validator.simulate_move(q, r, to_q, to_r):
                                captures.append((q, r, to_q, to_r))
        return captures
    
    def _order_moves(self, board: HexBoard, moves: List[Tuple]) -> List[Tuple]:
        """
        Order moves for better alpha-beta pruning.
        Priority: Captures > Checks > Other moves
        """
        def move_score(move):
            from_q, from_r, to_q, to_r = move
            score = 0
            
            # Prioritize captures
            target = board.get_tile(to_q, to_r)
            if target and target.has_piece():
                _, captured_piece = target.get_piece()
                from_tile = board.get_tile(from_q, from_r)
                _, moving_piece = from_tile.get_piece()
                
                # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                from evaluation import PIECE_VALUES
                victim_value = PIECE_VALUES.get(captured_piece, 0)
                attacker_value = PIECE_VALUES.get(moving_piece, 0)
                score += victim_value * 10 - attacker_value
            
            return score
        
        return sorted(moves, key=move_score, reverse=True)
    
    def _make_move(self, board: HexBoard, from_q: int, from_r: int, 
                   to_q: int, to_r: int) -> Tuple:
        """Make a move on the board and return state for undo."""
        from_tile = board.get_tile(from_q, from_r)
        to_tile = board.get_tile(to_q, to_r)
        
        piece = from_tile.piece
        captured = to_tile.piece
        
        # Make the move
        to_tile.piece = piece
        from_tile.piece = None
        
        # Switch turn
        board.current_turn = "black" if board.current_turn == "white" else "white"
        
        return piece, captured
    
    def _undo_move(self, board: HexBoard, from_q: int, from_r: int,
                   to_q: int, to_r: int, piece: Tuple, captured: Optional[Tuple]):
        """Undo a move on the board."""
        from_tile = board.get_tile(from_q, from_r)
        to_tile = board.get_tile(to_q, to_r)
        
        # Restore pieces
        from_tile.piece = piece
        to_tile.piece = captured
        
        # Restore turn
        board.current_turn = "black" if board.current_turn == "white" else "white"
