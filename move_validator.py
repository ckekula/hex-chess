"""
Implements legal moves for all pieces in the hexagonal variant.
"""

from typing import List, Tuple
from hex_board import HexBoard

class MoveValidator:
    """Validates moves according to Glinski's hexagonal chess rules."""
    
    # Hexagonal directions (6 main directions)
    HEX_DIRECTIONS = [
        (1, 0), (-1, 0),    # East, West
        (0, 1), (0, -1),    # Southeast, Northwest
        (1, -1), (-1, 1)    # Northeast, Southwest
    ]
    
    # Diagonal directions (6 diagonals)
    DIAGONAL_DIRECTIONS = [
        (2, -1), (-2, 1),   # Long diagonals
        (1, 1), (-1, -1),   # Medium diagonals
        (1, -2), (-1, 2)    # Short diagonals
    ]
    
    def __init__(self, board: HexBoard):
        self.board = board
        self.current_turn = "white"  # Track whose turn it is
    
    def get_legal_moves(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Get all legal moves for the piece at position (q, r)."""
        tile = self.board.get_tile(q, r)
        if not tile or not tile.has_piece():
            return []
        
        piece_color, piece_type = tile.get_piece()
        
        # Check if it's this piece's turn
        if piece_color != self.current_turn:
            return []
        
        # Get moves based on piece type
        if piece_type == "pawn":
            return self._get_pawn_moves(q, r, piece_color)
        elif piece_type == "knight":
            return self._get_knight_moves(q, r, piece_color)
        elif piece_type == "bishop":
            return self._get_bishop_moves(q, r, piece_color)
        elif piece_type == "rook":
            return self._get_rook_moves(q, r, piece_color)
        elif piece_type == "queen":
            return self._get_queen_moves(q, r, piece_color)
        elif piece_type == "king":
            return self._get_king_moves(q, r, piece_color)
        
        return []
    
    def is_legal_move(self, from_q: int, from_r: int, to_q: int, to_r: int) -> bool:
        """Check if a move is legal."""
        legal_moves = self.get_legal_moves(from_q, from_r)
        return (to_q, to_r) in legal_moves
    
    def _is_valid_tile(self, q: int, r: int) -> bool:
        """Check if a tile exists on the board."""
        return self.board.get_tile(q, r) is not None
    
    def _is_empty(self, q: int, r: int) -> bool:
        """Check if a tile is empty."""
        tile = self.board.get_tile(q, r)
        return tile is not None and not tile.has_piece()
    
    def _is_enemy(self, q: int, r: int, friendly_color: str) -> bool:
        """Check if a tile contains an enemy piece."""
        tile = self.board.get_tile(q, r)
        if tile and tile.has_piece():
            piece_color, _ = tile.get_piece()
            return piece_color != friendly_color
        return False
    
    def _can_capture(self, q: int, r: int, friendly_color: str) -> bool:
        """Check if a piece can capture at this position."""
        return self._is_enemy(q, r, friendly_color)
    
    def _get_pawn_moves(self, q: int, r: int, color: str) -> List[Tuple[int, int]]:
        """Get legal pawn moves. Pawns move forward and capture diagonally."""
        moves = []
        
        # Forward directions depend on color
        if color == "white":
            # White pawns move toward negative r
            forward_dirs = [(0, -1), (1, -1), (-1, 0)]
            capture_dirs = [(1, -2), (-1, 1), (1, 1)]
        else:
            # Black pawns move toward positive r
            forward_dirs = [(0, 1), (-1, 1), (1, 0)]
            capture_dirs = [(-1, 2), (1, -1), (-1, -1)]
        
        # Forward moves (can't capture)
        for dq, dr in forward_dirs:
            new_q, new_r = q + dq, r + dr
            if self._is_valid_tile(new_q, new_r) and self._is_empty(new_q, new_r):
                moves.append((new_q, new_r))
        
        # Diagonal captures
        for dq, dr in capture_dirs:
            new_q, new_r = q + dq, r + dr
            if self._is_valid_tile(new_q, new_r) and self._can_capture(new_q, new_r, color):
                moves.append((new_q, new_r))
        
        return moves
    
    def _get_knight_moves(self, q: int, r: int, color: str) -> List[Tuple[int, int]]:
        """Get legal knight moves. Knights jump in an L-shape pattern."""
        moves = []
        
        # Knight moves in hexagonal chess (12 possible positions)
        knight_jumps = [
            (2, -1), (-2, 1), (1, -2), (-1, 2),  # Length 2 jumps
            (2, 1), (-2, -1), (1, 2), (-1, -2),  # More length 2 jumps
            (3, -2), (-3, 2), (2, -3), (-2, 3)   # Length 3 jumps (alternate knight)
        ]
        
        # Simplified: standard knight pattern
        knight_jumps = [
            (2, -1), (-2, 1), (1, -2), (-1, 2),
            (1, 1), (-1, -1), (2, 1), (-2, -1),
            (1, 2), (-1, -2), (3, -1), (-3, 1),
            (3, -2), (-3, 2), (2, -3), (-2, 3)
        ]
        
        for dq, dr in knight_jumps:
            new_q, new_r = q + dq, r + dr
            if self._is_valid_tile(new_q, new_r):
                if self._is_empty(new_q, new_r) or self._can_capture(new_q, new_r, color):
                    moves.append((new_q, new_r))
        
        return moves
    
    def _get_sliding_moves(self, q: int, r: int, color: str, 
                          directions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get moves for sliding pieces (bishop, rook, queen)."""
        moves = []
        
        for dq, dr in directions:
            # Slide in this direction until blocked
            current_q, current_r = q + dq, r + dr
            
            while self._is_valid_tile(current_q, current_r):
                if self._is_empty(current_q, current_r):
                    moves.append((current_q, current_r))
                    current_q += dq
                    current_r += dr
                elif self._can_capture(current_q, current_r, color):
                    moves.append((current_q, current_r))
                    break  # Can't move past captured piece
                else:
                    break  # Blocked by friendly piece
        
        return moves
    
    def _get_bishop_moves(self, q: int, r: int, color: str) -> List[Tuple[int, int]]:
        """Get legal bishop moves. Bishops move diagonally."""
        return self._get_sliding_moves(q, r, color, self.DIAGONAL_DIRECTIONS)
    
    def _get_rook_moves(self, q: int, r: int, color: str) -> List[Tuple[int, int]]:
        """Get legal rook moves. Rooks move along hex edges."""
        return self._get_sliding_moves(q, r, color, self.HEX_DIRECTIONS)
    
    def _get_queen_moves(self, q: int, r: int, color: str) -> List[Tuple[int, int]]:
        """Get legal queen moves. Queens combine rook and bishop movement."""
        all_directions = self.HEX_DIRECTIONS + self.DIAGONAL_DIRECTIONS
        return self._get_sliding_moves(q, r, color, all_directions)
    
    def _get_king_moves(self, q: int, r: int, color: str) -> List[Tuple[int, int]]:
        """Get legal king moves. Kings move one space in any direction."""
        moves = []
        all_directions = self.HEX_DIRECTIONS + self.DIAGONAL_DIRECTIONS
        
        for dq, dr in all_directions:
            new_q, new_r = q + dq, r + dr
            if self._is_valid_tile(new_q, new_r):
                if self._is_empty(new_q, new_r) or self._can_capture(new_q, new_r, color):
                    moves.append((new_q, new_r))
        
        return moves
    
    def switch_turn(self):
        """Switch the current player's turn."""
        self.current_turn = "black" if self.current_turn == "white" else "white"